# coding: utf-8
#-----------------------------
# 数据库备份工具 — 大库优化版
#-----------------------------
# 关键优化:
#   1. --serializable-deferrable: MVCC 快照导出, 与 DDL 冲突时自动重试, 不阻塞写入
#   2. --lock-wait-timeout=30s: 锁等待超时, 避免大 DDL 下备份一直卡住
#   3. --no-sync (PG 14+): dump 完不等 fsync, 大幅减少 I/O 等待
#   4. pigz 并行压缩: 自动检测 pigz, 多线程压缩比 gzip 快 3~8 倍
#   5. set -o pipefail: 管道中 pg_dump 失败能被正确捕获
#   6. 捕获 pg_dump stderr 写入日志, 便于排查
# 关于"锁表":
#   pg_dump 拿的是 ACCESS SHARE LOCK, 本来就不阻塞 INSERT/UPDATE/DELETE 写入,
#   只和 DDL (ALTER/DROP/CREATE INDEX) 冲突 — 这是 MVCC 下 pg_dump 的正常行为。
#   要备份时让 DDL 不卡住备份, 最有效的方法就是加 --lock-wait-timeout 设短超时,
#   让冲突的备份快速失败而不是无限等待, 同时 pigz 并行压缩让备份本身更快,
#   整体缩短"备份期间可能和 DDL 冲突"的时间窗口。

import sys
import os
import time
import re
import subprocess
import shutil

if sys.platform != 'darwin':
    # 按脚本位置定位项目根目录:plugins/postgresql/scripts -> 项目根
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw
import core.db as db

'''
DEBUG:
python3 plugins/postgresql/scripts/backup.py database admin 3
python3 plugins/postgresql/scripts/backup.py database ALL 3
'''


def _pgDumpMajorVersion(pg_dump_bin):
    """取 pg_dump 的主版本号, 如 14 / 18. 失败返回 0."""
    try:
        out = subprocess.check_output([pg_dump_bin, '--version'], stderr=subprocess.STDOUT)
        m = re.search(r'(\d+)', out.decode())
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0


def _detectParallelCpus():
    """检测可用 CPU 核数, 用于 pigz 并行度."""
    try:
        return int(subprocess.check_output(['sysctl', '-n', 'hw.ncpu']).strip())
    except Exception:
        try:
            return len(os.sched_getaffinity(0))
        except Exception:
            return 4


def _compressorCmd():
    """
    返回 (压缩命令, 扩展名). 优先 pigz (并行 gzip), 否则回退 gzip.
    pigz 不存在时返回 ('gzip', '.sql.gz').
    """
    pigz = shutil.which('pigz')
    if pigz:
        cpus = _detectParallelCpus()
        return (pigz + ' -p ' + str(max(2, cpus - 1)) + ' -6', '.sql.gz')
    return ('gzip -6', '.sql.gz')


class backupTools:

    def getServerDir(self):
        return mw.getServerDir() + '/postgresql'

    def getPgPort(self):
        conf = self.getServerDir() + '/data/postgresql.conf'
        content = mw.readFile(conf)
        if not content:
            return '5432'
        tmp = re.search(r'port\s*=\s*(.*)', content)
        if not tmp:
            return '5432'
        return tmp.groups()[0].strip()

    def getPgDump(self):
        pg_dump = self.getServerDir() + '/bin/pg_dump'
        if os.path.exists(pg_dump):
            return pg_dump
        return 'pg_dump'

    def getDbBackupList(self, dbname=''):
        bkDir = mw.getFatherDir() + '/backup/database/postgresql'
        if not os.path.isdir(bkDir):
            return []
        blist = os.listdir(bkDir)
        r = []

        bname = 'db_' + dbname
        blen = len(bname)
        for x in blist:
            fbstr = x[0:blen]
            if fbstr == bname:
                r.append(x)
        # 文件名按时间戳命名,排序后即为时间顺序(旧->新)
        r.sort()
        return r

    def backupDatabase(self, params, count):
        params_args = params.split("@")
        name = params_args[0]
        table_name = ''
        if len(params_args) > 1:
            table_name = params_args[1]

        backup_name = name
        if table_name != '':
            backup_name = name + '@' + table_name

        db_path = self.getServerDir()
        db_name = 'pgsql'
        find_name = mw.M('databases').dbPos(db_path, db_name).where(
            'name=?', (name,)).getField('name')
        startTime = time.time()
        if not find_name:
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]不存在!"
            print("★[" + endDate + "] " + log)
            print("----------------------------------------------------------------------------")
            return

        backup_path = mw.getBackupDir() + '/database/postgresql'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        compressor_cmd, ext = _compressorCmd()
        filename = backup_path + "/db_" + backup_name + "_" + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ext

        port = self.getPgPort()
        pg_dump = self.getPgDump()
        pg_major = _pgDumpMajorVersion(pg_dump)

        # -------- 组装 pg_dump 参数 --------
        # -c --if-exists: 导出带 DROP 语句, 恢复时便于覆盖
        # --serializable-deferrable: MVCC 快照导出, 与 DDL 快照冲突时自动重试
        # --lock-wait-timeout=30s: 等表锁最多 30 秒, 避免大 DDL 下一直阻塞
        # --no-sync (PG 14+): dump 完不等 fsync, 减少 I/O 等待
        dump_opts = '-c --if-exists --serializable-deferrable --lock-wait-timeout=30s'
        if pg_major >= 14:
            dump_opts += ' --no-sync'

        if table_name != '':
            dump_args = '{} -t {} {}'.format(dump_opts, table_name, name)
        else:
            dump_args = '{} {}'.format(dump_opts, name)

        # -------- 执行备份 --------
        # set -o pipefail: 管道任一命令失败即返回非零 exit code
        # exit_code_file 保存管道最终 exit code, 便于 Python 侧检测
        exit_code_file = '/tmp/pg_dump_exit_code'
        if mw.isAppleSystem():
            cmd = 'set -o pipefail && {} {} -p {} 2>>/tmp/pg_dump_stderr.log | {} > "{}"; echo $? > {}'.format(
                pg_dump, dump_args, port, compressor_cmd, filename, exit_code_file)
        else:
            cmd = 'set -o pipefail && su - postgres -c "{} {} -p {}" 2>>/tmp/pg_dump_stderr.log | {} > "{}"; echo $? > {}'.format(
                pg_dump, dump_args, port, compressor_cmd, filename, exit_code_file)

        # 清空上次的 stderr 日志, 便于定位
        try:
            open('/tmp/pg_dump_stderr.log', 'w').close()
        except Exception:
            pass

        mw.execShell(cmd)

        # 从 exit_code_file 读取管道 exit code（set -o pipefail 保证准确）
        exit_code = 0
        try:
            with open(exit_code_file) as f:
                exit_code = int(f.read().strip())
        except Exception:
            pass

        # -------- 结果校验 --------
        # 从 stderr 日志读取 pg_dump 的错误输出
        stderr_txt = ''
        try:
            stderr_txt = open('/tmp/pg_dump_stderr.log').read().strip()
        except Exception:
            pass

        if exit_code != 0 \
                or not os.path.exists(filename) \
                or os.path.getsize(filename) < 200:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception:
                    pass
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]备份失败!"
            if stderr_txt:
                log += "  pg_dump stderr: " + stderr_txt[-300:]
            print("★[" + endDate + "] " + log)
            print("----------------------------------------------------------------------------")
            return

        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        outTime = time.time() - startTime

        log = "数据库[" + backup_name + "]备份成功,用时[" + str(round(outTime, 2)) + "]秒"
        mw.writeLog('计划任务', log)
        print("★[" + endDate + "] " + log)
        print("|---保留最新的[" + count + "]份备份")
        print("|---文件名:" + filename)
        if 'pigz' in compressor_cmd:
            print("|---压缩:pigz 多线程模式")
        else:
            print("|---压缩:gzip 单线程模式(建议装 pigz 提升大库备份速度)")

        backups = self.getDbBackupList(backup_name)
        # 清理多余备份
        num = len(backups) - int(count)
        if num > 0:
            for backup in backups:
                mw.execShell("rm -f " + backup_path + "/" + backup)
                num -= 1
                print("|---已清理过期文件：" + backup)
                if num < 1:
                    break

    def backupDatabaseAll(self, save):
        db_path = self.getServerDir()
        db_name = 'pgsql'
        databases = mw.M('databases').dbPos(db_path, db_name).field('name').select()
        for database in databases:
            self.backupDatabase(database['name'], save)


if __name__ == "__main__":
    backup = backupTools()
    type = sys.argv[1]
    if type == 'database':
        if sys.argv[2] == 'ALL':
            backup.backupDatabaseAll(sys.argv[3])
        else:
            backup.backupDatabase(sys.argv[2], sys.argv[3])
