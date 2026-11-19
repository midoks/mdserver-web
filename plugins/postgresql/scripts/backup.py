# coding: utf-8
#-------------------------------------------------------------
# PostgreSQL 数据库备份工具
#-------------------------------------------------------------
# 用法:
#   python3 backup.py database <dbname>           <keep_count>    # 单库全量
#   python3 backup.py database <dbname>@<table>  <keep_count>    # 指定表
#   python3 backup.py database ALL@               <keep_count>    # 所有库
#   BACKUP_DEBUG=1 python3 backup.py database xx@ 3              # 详细调试
#
# 核心设计:
#   * 认证: pg_hba.conf 全是 scram-sha-256, 从 sqlite config 表
#     读 pg_root 密码, 用 PGPASSWORD 环境变量传, 走 Unix socket (-h /tmp)
#   * shell: bash -c "set -o pipefail && ...", 避免 zsh 内置命令吞 PGPASSWORD,
#     也避免 su - postgres 清环境变量导致二次认证
#   * 管道: pg_dump | pigz/gzip > 文件, echo $? > exit_code_file
#     exit_code_file 用唯一名 /tmp/pg_dump_<pid>_<time>_exit_code, 不覆盖
#   * 调试: BACKUP_DEBUG=1 时打印脱敏后的完整命令、exit_code、stderr 全文
#           BACKUP_DEBUG=2 时打印带密码的原始命令 (不要贴到工单)
#-------------------------------------------------------------

import sys
import os
import time
import re
import subprocess
import shutil

if sys.platform != 'darwin':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

# 全局调试开关: 0=简洁 (默认), 1=详细 (脱敏密码), 2=详细 + 明文密码
DEBUG = int(os.environ.get('BACKUP_DEBUG', '0'))


def _useColor():
    """只有交互式终端才输出 ANSI 颜色.

    面板 / 计划任务会重定向 stdout 到日志或管道, 此时注入颜色码只会
    在页面上残留成 "[1;34m" 之类的乱码, 因此按 NO_COLOR 约定自动降级.
    """
    if os.environ.get('NO_COLOR'):
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


COLOR = _useColor()


def _paint(code, msg):
    if not COLOR:
        return msg
    return "\033[%sm%s\033[0m" % (code, msg)


def _step(idx, total, msg):
    """打印当前步骤, 如 [1/6] 检查数据库存在性"""
    print("%s %s" % (_paint('1;34', '[%d/%d]' % (idx, total)), msg), flush=True)


def _ok(msg='OK'):
    print("  %s %s" % (_paint('1;32', '✓'), msg), flush=True)


def _fail(msg):
    print("  %s %s" % (_paint('1;31', '✗'), msg), flush=True)


def _warn(msg):
    print("  %s %s" % (_paint('1;33', '!'), msg), flush=True)


def _dbg(msg):
    """调试输出, BACKUP_DEBUG>=1 才显示"""
    if DEBUG >= 1:
        print("  %s %s" % (_paint('1;36', '[dbg]'), msg), flush=True)


def _pgDumpMajorVersion(pg_dump_bin):
    try:
        out = subprocess.check_output([pg_dump_bin, '--version'], stderr=subprocess.STDOUT)
        m = re.search(r'(\d+)', out.decode())
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0


def _detectParallelCpus():
    n = os.cpu_count()
    if n and n > 0:
        return n
    try:
        return int(subprocess.check_output(['nproc']).strip())
    except Exception:
        pass
    try:
        return int(subprocess.check_output(['sysctl', '-n', 'hw.ncpu']).strip())
    except Exception:
        pass
    return 4


def _compressorCmd():
    pigz = shutil.which('pigz')
    if pigz:
        cpus = _detectParallelCpus()
        return (pigz + ' -p ' + str(max(2, cpus - 1)) + ' -6', '.sql.gz', True)
    return ('gzip -6', '.sql.gz', False)


def _maskPwd(cmd, pwd):
    """把命令里的 PGPASSWORD='xxx' 换成 PGPASSWORD='***', 避免日志泄露"""
    if DEBUG >= 2:
        return cmd
    safe = pwd.replace("'", "'\\''")
    return cmd.replace("PGPASSWORD='%s'" % safe, "PGPASSWORD='***'")


def _genTempFiles():
    """生成唯一的临时文件名, 避免多次运行互相覆盖"""
    tag = "%d_%d" % (os.getpid(), int(time.time()))
    exit_code_file = '/tmp/pg_dump_%s_exit_code' % tag
    pg_dump_stderr = '/tmp/pg_dump_%s_stderr.log' % tag
    return exit_code_file, pg_dump_stderr


class backupTools:

    def getServerDir(self):
        return mw.getServerDir() + '/postgresql'

    def isSlaveDb(self):
        return os.path.exists(self.getServerDir() + "/data/standby.signal")

    def getPgPort(self):
        conf = self.getServerDir() + '/data/postgresql.conf'
        content = mw.readFile(conf)
        if not content:
            return '5432'
        m = re.search(r'port\s*=\s*(.*)', content)
        return m.group(1).strip() if m else '5432'

    def getPgDump(self):
        pg_dump = self.getServerDir() + '/bin/pg_dump'
        return pg_dump if os.path.exists(pg_dump) else 'pg_dump'

    def getDbBackupList(self, dbname=''):
        bkDir = mw.getFatherDir() + '/backup/database/postgresql'
        if not os.path.isdir(bkDir):
            return []
        blist = os.listdir(bkDir)
        prefix = 'db_' + dbname + '_' + time.strftime('%Y')
        return sorted([x for x in blist if x.startswith(prefix)])

    def _getPgRootPwd(self):
        db_path = self.getServerDir()
        db_name = 'pgsql'
        return mw.M('config').dbPos(db_path, db_name).where('id=?', (1,)).getField('pg_root')

    def _buildDumpCmd(self, name, table_name, socket_dir, port, pg_dump, pg_major,
                      pg_pwd, compressor_cmd, filename, exit_code_file, pg_dump_stderr):
        """组装 pg_dump + 压缩 + 管道失败捕获 的完整 shell 命令"""

        # --- pg_dump 参数 ---
        dump_opts = '-c --if-exists --lock-wait-timeout=30s --no-password'
        if pg_major >= 14:
            dump_opts += ' --no-sync'
        if not self.isSlaveDb():
            dump_opts += ' --serializable-deferrable'

        if table_name:
            dump_args = '{} -t {} {}'.format(dump_opts, table_name, name)
        else:
            dump_args = '{} {}'.format(dump_opts, name)

        # --- shell 命令 ---
        safe_pwd = pg_pwd.replace("'", "'\\''")
        pg_dump_inner = '{} {} -U postgres -h {} -p {} 2>>{}'.format(
            pg_dump, dump_args, socket_dir, port, pg_dump_stderr)

        cmd = "bash -c \"set -o pipefail && PGPASSWORD='{}' {} | {} > \\\"{}\\\"; echo \\$? > {}\"".format(
            safe_pwd, pg_dump_inner, compressor_cmd, filename, exit_code_file)

        return cmd, safe_pwd, dump_opts

    def backupDatabase(self, params, count):
        params_args = params.split("@")
        name = params_args[0]
        table_name = params_args[1] if len(params_args) > 1 else ''

        steps = 6
        _step(1, steps, "校验参数 & 环境")
        _dbg("DEBUG=%s, BACKUP_DEBUG=%s" % (DEBUG, os.environ.get('BACKUP_DEBUG', '0')))
        _dbg("  参数: name=%s, table=%s, keep=%s" % (name, table_name, count))

        server_dir = self.getServerDir()
        db_path = server_dir
        db_name = 'pgsql'
        backup_name = name + ('@' + table_name if table_name else '')

        # --- 1. 数据库存在性 ---
        find_name = mw.M('databases').dbPos(db_path, db_name).where('name=?', (name,)).getField('name')
        if not find_name:
            _fail("数据库 [%s] 在 sqlite 记录里不存在" % name)
            return
        _ok("数据库 [%s] 记录存在" % name)

        # --- 2. 读取 PG 配置 ---
        _step(2, steps, "读取 PostgreSQL 配置")
        port = self.getPgPort()
        pg_dump = self.getPgDump()
        pg_major = _pgDumpMajorVersion(pg_dump)
        pg_pwd = self._getPgRootPwd()
        is_slave = self.isSlaveDb()

        socket_dir = '/tmp'
        socket_path = os.path.join(socket_dir, '.s.PGSQL.' + port)
        _dbg("  port=%s pg_dump=%s pg_ver=%s slave=%s" % (port, pg_dump, pg_major, is_slave))
        _dbg("  socket=%s (%s)" % (socket_path, '存在' if os.path.exists(socket_path) else '不存在!'))
        _dbg("  密码长度=%d, 空=%s" % (len(pg_pwd) if pg_pwd else 0, pg_pwd == '' or pg_pwd is None))
        _ok("端口=%s pg_dump=%s PG=%s" % (port, os.path.basename(pg_dump), pg_major))
        if not os.path.exists(socket_path):
            _warn("Unix socket %s 不存在, 可能 fallback 到 TCP localhost" % socket_path)
        if not pg_pwd:
            _warn("pg_root 密码为空, pg_dump 大概率会认证失败")

        # --- 3. 准备输出 ---
        _step(3, steps, "准备备份路径 & 压缩工具")
        backup_path = mw.getBackupDir() + '/database/postgresql'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        compressor_cmd, ext, is_pigz = _compressorCmd()
        filename = backup_path + "/db_" + backup_name + "_" + time.strftime('%Y%m%d_%H%M%S') + ext
        exit_code_file, pg_dump_stderr = _genTempFiles()

        _dbg("  备份目录: %s" % backup_path)
        _dbg("  输出文件: %s" % filename)
        _dbg("  压缩: %s" % ("pigz 多线程" if is_pigz else "gzip 单线程"))
        _dbg("  exit_code_file: %s" % exit_code_file)
        _dbg("  pg_dump_stderr: %s" % pg_dump_stderr)
        _ok("输出: %s  压缩: %s" % (os.path.basename(filename), 'pigz' if is_pigz else 'gzip'))

        # --- 4. 组装命令 ---
        _step(4, steps, "组装 pg_dump 命令")
        cmd, safe_pwd, dump_opts = self._buildDumpCmd(
            name, table_name, socket_dir, port, pg_dump, pg_major,
            pg_pwd, compressor_cmd, filename, exit_code_file, pg_dump_stderr)

        _dbg("  dump_opts: %s" % dump_opts)
        _dbg("  dump_args: %s%s %s" % (
            dump_opts,
            ' -t ' + table_name if table_name else '',
            name))
        _dbg("  完整命令:\n    %s" % _maskPwd(cmd, safe_pwd))
        _ok("命令已组装")

        # --- 5. 执行 ---
        _step(5, steps, "执行备份")
        start_time = time.time()

        # 清空 stderr 日志
        try:
            open(pg_dump_stderr, 'w').close()
        except Exception:
            pass

        mw.execShell(cmd)
        out_time = time.time() - start_time
        _dbg("  用时: %.2f 秒" % out_time)

        # --- 6. 读取结果 ---
        _step(6, steps, "校验结果")

        exit_code = -1
        try:
            with open(exit_code_file) as f:
                exit_code = int(f.read().strip())
        except Exception as e:
            _dbg("  读 exit_code_file 失败: %s" % e)

        stderr_txt = ''
        try:
            stderr_txt = open(pg_dump_stderr).read().strip()
        except Exception:
            pass

        file_exists = os.path.exists(filename)
        file_size = os.path.getsize(filename) if file_exists else 0

        _dbg("  exit_code = %s" % exit_code)
        _dbg("  file_exists = %s, file_size = %d bytes (%.2f KB)" % (
            file_exists, file_size, file_size / 1024))
        if stderr_txt:
            _dbg("  stderr 内容:\n    %s" % stderr_txt.replace('\n', '\n    '))
        else:
            _dbg("  stderr: (空)")

        # 清理临时文件 (失败时保留, 便于排查)
        try:
            os.remove(pg_dump_stderr)
        except Exception:
            pass

        # --- 判定 ---
        if exit_code != 0 or not file_exists or file_size < 200:
            _fail("备份失败")
            print("  ──────────────────────────────────────")
            print("  失败原因 (优先级从上到下):")
            if exit_code != 0:
                print("    exit_code = %d  (期望 0)" % exit_code)
            if not file_exists:
                print("    输出文件不存在: %s" % filename)
            if file_exists and file_size < 200:
                print("    文件太小 (%d bytes), 可疑" % file_size)
            if stderr_txt:
                print("  pg_dump stderr (最后 500 字):")
                print("    " + stderr_txt[-500:].replace('\n', '\n    '))
            print("  完整命令 (脱敏):")
            print("    " + _maskPwd(cmd, safe_pwd))
            print("  临时文件位置:")
            print("    exit_code: %s" % exit_code_file)
            print("    stderr:    %s" % pg_dump_stderr)
            print("  ──────────────────────────────────────")

            if file_exists:
                try:
                    os.remove(filename)
                except Exception:
                    pass
            return False

        # --- 成功 ---
        size_kb = file_size / 1024
        size_mb = size_kb / 1024
        size_str = "%.2f MB" % size_mb if size_mb >= 1 else "%.2f KB" % size_kb
        _ok("备份成功! 用时 %.2fs, 大小 %s" % (out_time, size_str))

        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        log = "数据库[%s]备份成功,用时[%.2f]秒,大小[%s]" % (backup_name, out_time, size_str)
        mw.writeLog('计划任务', log)
        print("★[%s] %s" % (endDate, log))
        print("  ──────────────────────────────────────")
        print("  输出文件: %s" % filename)
        print("  压缩方式: %s" % ('pigz 多线程 (建议装 pigz 提升速度)' if is_pigz else 'gzip 单线程'))
        print("  恢复命令:")
        print("    gunzip -c %s | psql -h %s -U postgres -d %s" % (filename, socket_dir, name))

        # --- 清理旧备份 ---
        backups = self.getDbBackupList(backup_name)
        num_to_del = len(backups) - int(count)
        if num_to_del > 0:
            print("  ──────────────────────────────────────")
            print("  保留最新 %s 份, 清理 %d 份过期:" % (count, num_to_del))
            for backup in backups:
                full = backup_path + "/" + backup
                mw.execShell("rm -f " + full)
                print("    - %s" % backup)
                num_to_del -= 1
                if num_to_del < 1:
                    break

        # 清理 exit_code_file (成功就没必要留着)
        try:
            os.remove(exit_code_file)
        except Exception:
            pass

        return True

    def backupDatabaseAll(self, save):
        db_path = self.getServerDir()
        db_name = 'pgsql'
        databases = mw.M('databases').dbPos(db_path, db_name).field('name').select()
        total = len(databases)
        print("=" * 60)
        print("批量备份, 共 %d 个数据库, 每库保留 %s 份" % (total, save))
        print("=" * 60)
        ok = fail = 0
        for i, db in enumerate(databases):
            print("\n--- [%d/%d] %s ---" % (i + 1, total, db['name']))
            if self.backupDatabase(db['name'], save):
                ok += 1
            else:
                fail += 1
        print("\n" + "=" * 60)
        print("全部完成: 成功 %d, 失败 %d" % (ok, fail))
        print("=" * 60)


if __name__ == "__main__":
    backup = backupTools()
    type = sys.argv[1] if len(sys.argv) > 1 else 'database'

    if len(sys.argv) < 3:
        print("用法: python3 backup.py database <dbname> [keep_count]")
        print("      python3 backup.py database ALL@ [keep_count]")
        sys.exit(1)

    if type == 'database':
        if sys.argv[2].startswith('ALL@'):
            save = sys.argv[3] if len(sys.argv) > 3 else '3'
            backup.backupDatabaseAll(save)
        else:
            save = sys.argv[3] if len(sys.argv) > 3 else '3'
            backup.backupDatabase(sys.argv[2], save)
    else:
        print("未知类型: %s" % type)
        sys.exit(1)
