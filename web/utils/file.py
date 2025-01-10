# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import pwd
import time
import shutil
import json
import base64

import core.mw as mw
import thisdb

def uploadSegment(path,name,size,start,dir_mode,file_mode,b64_data,upload_files):
    if not mw.fileNameCheck(name):
        return mw.returnData(False, '文件名中不能包含特殊字符!')

    if path == '/':
        return mw.returnData(False, '不能直接上传文件到系统根目录!')

    if name.find('./') != -1 or path.find('./') != -1:
        return mw.returnData(False, '错误的参数')

    if not os.path.exists(path):
        os.makedirs(path, 493)
        if not dir_mode != '' or not file_mode != '':
            mw.setMode(path)

    save_path = os.path.join(path, name + '.' + str(int(size)) + '.upload.tmp')
    d_size = 0
    if os.path.exists(save_path):
        d_size = os.path.getsize(save_path)

    if d_size != int(start):
        return mw.returnData(True, 'size', d_size)

    f = open(save_path, 'ab')
    if b64_data == '1':
        b64_data = base64.b64decode(b64_data)
        f.write(b64_data)
    else:
        for tmp_f in upload_files:
            f.write(tmp_f.read())

    f.close()
    f_size = os.path.getsize(save_path)
    if f_size != int(size):
        return mw.returnData(True, 'size', f_size)

    new_name = os.path.join(path, name)
    if os.path.exists(new_name):
        if new_name.find('.user.ini') != -1:
            mw.execShell("chattr -i " + new_name)
        try:
            os.remove(new_name)
        except:
            mw.execShell("rm -f %s" % new_name)

    os.renames(save_path, new_name)

    if dir_mode != '' and dir_mode != '':
        mode_tmp1 = dir_mode.split(',')
        mw.setMode(path, mode_tmp1[0])
        mw.setOwn(path, mode_tmp1[1])
        mode_tmp2 = file_mode.split(',')
        mw.setMode(new_name, mode_tmp2[0])
        mw.setOwn(new_name, mode_tmp2[1])
    else:
        setMode(new_name)

    msg = mw.getInfo('上传文件[{1}] 到 [{2}]成功!', (new_name, path))
    mw.writeLog('文件管理', msg)
    return mw.returnData(True, '上传成功!', f_size)


def mvFile(sfile, dfile):
    if not checkFileName(dfile):
        return mw.returnData(False, '文件名中不能包含特殊字符!')
    if not os.path.exists(sfile):
        return mw.returnData(False, '指定文件不存在!')

    if not checkDir(sfile):
        return mw.returnData(False, 'FILE_DANGER')


    try:
        pass
    except Exception as e:
        raise e

    try:
        shutil.move(sfile, dfile)
        msg = mw.getInfo('移动或重名命文件[{1}]到[{2}]成功!', (sfile, dfile,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '移动或重名命文件成功!')
    except Exception as e:
        return mw.returnData(False, '移动或重名命文件失败!'+str(e))

def unzip(sfile, dfile, stype, path):
    if not os.path.exists(sfile):
        return mw.returnData(False, '指定文件不存在!')

    try:
        tmps = mw.getPanelDir() + '/logs/panel_exec.log'
        if stype == 'zip':
            mw.execShell("cd " + path + " && unzip -o -d '" + dfile +"' '" + sfile + "' > " + tmps + " 2>&1 &")
        else:
            sfiles = ''
            for sfile in sfile.split(','):
                if not sfile:
                    continue
                sfiles += " '" + sfile + "'"
            mw.execShell("cd " + path + " && tar -zxvf " + sfiles +" -C " + dfile + " > " + tmps + " 2>&1 &")

        if os.path.exists(dfile):
            setFileAccept(dfile)
        mw.writeLog("文件管理", '文件[{1}]解压[{2}]成功!', (sfile, dfile))
        return mw.returnData(True, '文件解压成功!')
    except:
        return mw.returnData(False, '文件解压失败!')

def uncompress(sfile, dfile, path):
    if not os.path.exists(sfile):
        return mw.returnData(False, '指定文件不存在!')

    filename = os.path.basename(sfile)
    extension = os.path.splitext(filename)[-1]
    extension = extension.strip('.')

    tar_gz = 'tar.gz'
    tar_gz_len = len(tar_gz)
    suffix_gz = sfile[-tar_gz_len:]
    if suffix_gz == tar_gz:
        extension = suffix_gz

    if not extension in ['tar.gz', 'gz', 'zip', 'rar']:
        return mw.returnData(False, '现在仅支持gz,zip,rar格式解压!')

    if mw.isAppleSystem() and extension == 'rar':
        return mw.returnData(False, 'macosx暂时不支持rar格式解压')

    cmd = "cd " + path + " "
    try:
        tmps = mw.getPanelDir() + '/logs/panel_exec.log'
        if extension == 'zip':
            cmd += "&& unzip -o -d '" + dfile + "' '" + sfile + "' > " + tmps + " 2>&1 &"
            mw.execShell(cmd)
        if extension == 'tar.gz':
            cmd += "&& tar -zxvf " + sfile + " -C " + dfile + " > " + tmps + " 2>&1 &"
            mw.execShell(cmd)
        if extension == 'gz':
            cmd += "&& gunzip -k " + sfile + " > " + tmps + " 2>&1 &"
            mw.execShell(cmd)
        if extension == 'rar':
            cmd +=  "&& unrar x " + sfile + " " + dfile + " > " + tmps + " 2>&1 &"
            mw.execShell(cmd)

        if os.path.exists(dfile):
            setFileAccept(dfile)
        mw.writeLog("文件管理", '文件[{1}]解压[{2}]成功!', (sfile, dfile,))
        return mw.returnData(True, '文件解压成功!')
    except Exception as e:
        return mw.returnData(False, '文件解压失败!:' + str(e))

def setBatchData(path, stype, access, user, data):
    from admin import session
    if stype == '1' or stype == '2':
        session['selected'] = {
            'path': path,
            'type': stype,
            'access': access,
            'user': user,
            'data': data
        }
        return mw.returnData(True, '标记成功,请在目标目录点击粘贴所有按钮!')
    elif stype == '3':
        for key in json.loads(data):
            try:
                filename = path + '/' + key
                if not checkDir(filename):
                    return mw.returnData(False, 'FILE_DANGER')
                os.system('chmod -R ' + access + " '" + filename + "'")
                os.system('chown -R ' + user + ':' + user + " '" + filename + "'")
            except:
                continue
        mw.writeLog('文件管理', '批量设置权限成功!')
        return mw.returnData(True, '批量设置权限成功!')
    else:
        recycle_bin = thisdb.getOption('recycle_bin')
        is_recycle = False
        if recycle_bin == 'open':
            is_recycle = True
        data = json.loads(data)
        l = len(data)
        i = 0
        for key in data:
            try:
                filename = path + '/' + key
                topath = filename
                if not os.path.exists(filename):
                    continue

                i += 1
                mw.writeSpeed(key, i, l)
                if os.path.isdir(filename):
                    if not checkDir(filename):
                        return mw.returnData(False, '请不要花样作死!')
                    if is_recycle:
                        mvRecycleBin(topath)
                    else:
                        shutil.rmtree(filename)
                else:
                    if key == '.user.ini':
                        os.system('which chattr && chattr -i ' + filename)
                    if is_recycle:
                        mvRecycleBin(topath)
                    else:
                        os.remove(filename)
            except:
                continue
            mw.writeSpeed(None, 0, 0)
        mw.writeLog('文件管理', '批量删除成功!')
        return mw.returnData(True, '批量删除成功！')

def batchPaste(path, stype):
    from admin import session
    if not checkDir(path):
        return mw.returnData(False, '请不要花样作死!')
    i = 0
    myfiles = json.loads(session['selected']['data'])
    l = len(myfiles)
    if stype == '1':
        for key in myfiles:
            i += 1
            mw.writeSpeed(key, i, l)
            try:

                sfile = session['selected'][
                    'path'] + '/' + key
                dfile = path + '/' + key

                if os.path.isdir(sfile):
                    shutil.copytree(sfile, dfile)
                else:
                    shutil.copyfile(sfile, dfile)
                stat = os.stat(sfile)
                os.chown(dfile, stat.st_uid, stat.st_gid)
            except:
                continue
        msg = mw.getInfo('从[{1}]批量复制到[{2}]成功',(session['selected']['path'], path,))
        mw.writeLog('文件管理', msg)
    else:
        for key in myfiles:
            try:
                i += 1
                mw.writeSpeed(key, i, l)

                sfile = session['selected'][
                    'path'] + '/' + key
                dfile = path + '/' + key

                shutil.move(sfile, dfile)
            except:
                continue
        msg = mw.getInfo('从[{1}]批量移动到[{2}]成功',(session['selected']['path'], path,))
        mw.writeLog('文件管理', msg)
    mw.writeSpeed(None, 0, 0)
    errorCount = len(myfiles) - i
    del(session['selected'])
    msg = mw.getInfo('批量操作成功[{1}],失败[{2}]', (str(i), str(errorCount)))
    return mw.returnData(True, msg)


def zip(sfile, dfile, stype, path):
    if sfile.find(',') == -1:
        if not os.path.exists(path + '/' + sfile):
            return mw.returnData(False, '指定文件不存在!')

    try:
        tmps = mw.getPanelDir() + '/logs/panel_exec.log'
        if stype == 'zip':
            mw.execShell("cd '" + path + "' && zip '" + dfile +
                         "' -r '" + sfile + "' > " + tmps + " 2>&1")
        else:
            sfiles = ''
            for sfile in sfile.split(','):
                if not sfile:
                    continue
                sfiles += " '" + sfile + "'"
            mw.execShell("cd '" + path + "' && tar -zcvf '" + dfile + "' " + sfiles + " > " + tmps + " 2>&1")
        setFileAccept(dfile)
        mw.writeLog("文件管理", '文件[{1}]压缩[{2}]成功!', (sfile, dfile))
        return mw.returnData(True, '文件压缩成功!')
    except:
        return mw.returnData(False, '文件压缩失败!')

def unzip(sfile, dfile, stype, path):
    if not os.path.exists(sfile):
        return mw.returnData(False, '指定文件不存在!')

    try:
        tmps = mw.getPanelDir() + '/logs/panel_exec.log'
        if stype == 'zip':
            mw.execShell("cd " + path + " && unzip -o -d '" + dfile + "' '" + sfile + "' > " + tmps + " 2>&1 &")
        else:
            sfiles = ''
            for sfile in sfile.split(','):
                if not sfile:
                    continue
                sfiles += " '" + sfile + "'"
            mw.execShell("cd " + path + " && tar -zxvf " + sfiles + " -C " + dfile + " > " + tmps + " 2>&1 &")

        setFileAccept(dfile)
        mw.writeLog("文件管理", '文件[{1}]解压[{2}]成功!', (sfile, dfile))
        return mw.returnData(True, '文件解压成功!')
    except:
        return mw.returnData(False, '文件解压失败!')

def getAccess(filename):
    data = {}
    try:
        stat = os.stat(filename)
        data['chmod'] = str(oct(stat.st_mode)[-3:])
        data['chown'] = pwd.getpwuid(stat.st_uid).pw_name
    except:
        data['chmod'] = 755
        data['chown'] = 'www'
    return data

def copyDir(src_file, dst_file):
    if not os.path.exists(src_file):
        return mw.returnData(False, '指定目录不存在!')

    if os.path.exists(dst_file):
        return mw.returnData(False, '指定目录已存在!')

    try:
        shutil.copytree(src_file, dst_file)
        stat = os.stat(src_file)
        os.chown(dst_file, stat.st_uid, stat.st_gid)
        msg = mw.getInfo('复制目录[{1}]到[{2}]成功!', (src_file, dst_file))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '目录复制成功!')
    except:
        return mw.returnData(False, '目录复制失败!')

def copyFile(src_file, dst_file):
    if src_file == dst_file:
        return mw.returnJson(False, '源与目的一致!')

    if not os.path.exists(src_file):
        return mw.returnJson(False, '指定文件不存在!')

    if os.path.isdir(src_file):
        return copyDir(src_file, dst_file)

    try:
        shutil.copyfile(src_file, dst_file)
        msg = mw.getInfo('复制文件[{1}]到[{2}]成功!', (src_file, dst_file,))
        mw.writeLog('文件管理', msg)
        stat = os.stat(src_file)
        os.chown(dst_file, stat.st_uid, stat.st_gid)
        return mw.returnData(True, '文件复制成功!')
    except:
        return mw.returnData(False, '文件复制失败!')

def setFileAccept(filename):
    auth = 'www:www'
    if mw.getOs() == 'darwin':
        user = mw.execShell("who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        auth = user + ':staff'
    os.system('chown -R ' + auth + ' ' + filename)
    os.system('chmod -R 755 ' + filename)

def createFile(file_path):
    try:
        if not checkFileName(file_path):
            return mw.returnData(False, '文件名中不能包含特殊字符!')
        if os.path.exists(file_path):
            return mw.returnData(False, '指定文件已存在!')
        _path = os.path.dirname(file_path)
        if not os.path.exists(_path):
            os.makedirs(_path)
        open(file_path, 'w+').close()
        setFileAccept(file)
        msg = mw.getInfo('创建文件[{1}]成功!', (file_path,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '文件创建成功!')
    except Exception as e:
        return mw.returnData(True, '文件创建失败:'+str(e))

def createDir(path):
    try:
        if not checkFileName(path):
            return mw.returnData(False, '目录名中不能包含特殊字符!')
        if os.path.exists(path):
            return mw.returnData(False, '指定目录已存在!')
        os.makedirs(path)
        setFileAccept(path)
        msg = mw.getInfo('创建目录[{1}]成功!', (path,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '目录创建成功!')
    except Exception as e:
        print(e)
        return mw.returnData(False, '目录创建失败!')

# 检查敏感目录
def checkDir(path):
    path = path.replace('//', '/')
    if path[-1:] == '/':
        path = path[:-1]

    sense_dir = ('',
        '/',
        '/*',
        '/www',
        '/root',
        '/boot',
        '/bin',
        '/etc',
        '/home',
        '/dev',
        '/sbin',
        '/var',
        '/usr',
        '/tmp',
        '/sys',
        '/proc',
        '/media',
        '/mnt',
        '/opt',
        '/lib',
        '/srv',
        '/selinux',
        '/www/server',
        mw.getRootDir())
    return not path in sense_dir

def getFileBody(path):
    if not os.path.exists(path):
        return mw.returnData(False, '文件不存在', (path,))

    if os.path.getsize(path) > 2097152:
        return mw.returnData(False, '不能在线编辑大于2MB的文件!')

    if os.path.isdir(path):
        return mw.returnData(False, '这不是一个文件!')

    fp = open(path, 'rb')
    data = {}
    data['status'] = True
    if fp:
        srcBody = fp.read()
        fp.close()

        encoding_list = ['utf-8', 'GBK', 'BIG5']
        for el in encoding_list:
            try:
                data['encoding'] = el
                data['data'] = srcBody.decode(data['encoding'])
                break
            except Exception as ex:
                if el == 'BIG5':
                    return mw.returnData(False, '文件编码不被兼容，无法正确读取文件!' + str(ex))
    else:
        return mw.returnData(False, '文件未正常打开!')
    return mw.returnData(True, 'OK', data)

def saveBody(path, data, encoding):
    if not os.path.exists(path):
        return mw.returnData(False, '文件不存在')
    try:
        if encoding == 'ascii':
            encoding = 'utf-8'

        data = data.encode(encoding, errors='ignore').decode(encoding)
        fp = open(path, 'w+', encoding=encoding)
        fp.write(data)
        fp.close()

        if path.find("web_conf") > 0:
            mw.restartWeb()
        mw.writeLog('文件管理', '文件[{1}]保存成功', (path,))
        return mw.returnData(True, '文件保存成功')
    except Exception as ex:
        return mw.returnData(False, '文件保存错误:' + str(ex))


def sortFileList(path, ftype = 'mtime', sort = 'desc'):
    flist = os.listdir(path)
    if ftype == 'mtime':
        try:
            if sort == 'desc':
                flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=True)
            if sort == 'asc':
                flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=False)
        except Exception as e:
            if sort == 'desc':
                flist = sorted(flist, key=lambda f: os.path.getctime(os.path.join(path,f)), reverse=True)
            if sort == 'asc':
                flist = sorted(flist, key=lambda f: os.path.getctime(os.path.join(path,f)), reverse=False)
        

    if ftype == 'size':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getsize(os.path.join(path,f)), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getsize(os.path.join(path,f)), reverse=False)

    if ftype == 'fname':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.join(path,f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.join(path,f), reverse=False)
    return flist

def sortAllFileList(path, ftype = 'mtime', sort = 'desc', search = '',limit = 3000):
    count = 0
    flist = []
    for d_list in os.walk(path):
        if count >= limit:
            break

        for d in d_list[1]:
            if count >= limit:
                break
            if d.lower().find(search) != -1:
                filename = d_list[0] + '/' + d
                if not os.path.exists(filename):
                    continue
                count += 1
                flist.append(filename)

        for f in d_list[2]:
            if count >= limit:
                break

            if f.lower().find(search) != -1:
                filename = d_list[0] + '/' + f
                if not os.path.exists(filename):
                    continue
                count += 1
                flist.append(filename)

    if ftype == 'mtime':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(f), reverse=False)

    if ftype == 'size':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getsize(f), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getsize(f), reverse=False)
    return flist

def getAllDirList(path, page=1, size=10, order = '', search=None):
    if page < 1:
        page == 1

    data = {}
    dirnames = []
    filenames = []
    
    max_limit = 3000
    order_split = order.split(' ')
    if len(order_split) < 2:
        flist = sortAllFileList(path, order_split[0],'',search, max_limit)
    else:
        flist = sortAllFileList(path, order_split[0], order_split[1], search, max_limit)

    count = len(flist)
    start = (page - 1) * size
    end = start + size
    if end > count:
        end = count

    plist = flist[start:end]
    for dst_file in plist:
        if not os.path.exists(dst_file):
            continue
        stat = mw.getFileStatsDesc(dst_file, path)
        if os.path.isdir(dst_file):
            dirnames.append(stat)
        else:
            filenames.append(stat)

    data['count'] = count
    data['dir'] = dirnames
    data['files'] = filenames
    data['path'] = path.replace('//', '/')
    return data

def getDirList(path, page=1, size=10, order = '', search=None):
    if page < 1:
        page == 1

    data = {}
    dirnames = []
    filenames = []

    count = getCount(path, search)
    order_split = order.strip().split(' ')
    if len(order_split) < 2:
        flist = sortFileList(path, order_split[0], '')
    else:
        flist = sortFileList(path, order_split[0], order_split[1])

    start = (page - 1) * size
    end = start + size
    if end > count:
        end = count

    
    if search or search != '':
        nlist = []
        for f in flist:
            if f.lower().find(search) == -1:
                continue
            nlist.append(f)
        plist = nlist[start:end]
    else:
        plist = flist[start:end]
    
    for filename in plist:
        abs_file = path + '/' + filename
        if not os.path.exists(abs_file):
            continue

        stats = mw.getFileStatsDesc(abs_file, path)
        if os.path.isdir(abs_file):
            dirnames.append(stats)
        else:
            filenames.append(stats)

    data['count'] = count
    data['dir'] = dirnames
    data['files'] = filenames
    data['path'] = path.replace('//', '/')
    return data

# 检测文件名
def checkFileName(filename):
    nots = ['\\', '&', '*', '|', ';']
    if filename.find('/') != -1:
        filename = filename.split('/')[-1]
    for n in nots:
        if n in filename:
            return False
    return True


# 获取目录大小
def getDirSize(filePath, size=0):
    for root, dirs, files in os.walk(filePath):
        for f in files:
            try:
                size += os.path.getsize(os.path.join(root, f))
            except Exception as e:
                pass
            # print(f)
    return size

# 获取目录大小(bash)
def getDirSizeByBash(path):
    tmp = mw.execShell('du -sh ' + path)
    return tmp[0].split()[0].lower()

# 计算文件数量
def getCount(path, search = None):
    i = 0
    for name in os.listdir(path):
        if name == '.' or name == '..':
            continue
        if search:
            if name.lower().find(search) == -1:
                continue
        i += 1
    return i

# 获取文件权限
def getAccess(fname):
    data = {}
    try:
        stat = os.stat(fname)
        data['chmod'] = str(oct(stat.st_mode)[-3:])
        data['chown'] = pwd.getpwuid(stat.st_uid).pw_name
    except Exception as e:
        # print(e)
        data['chmod'] = 755
        data['chown'] = 'www'
    return data

def setFileAccess(filename,user,access):
    sall = '-R'
    try:
        if not checkDir(filename):
            return mw.returnData(False, '请不要花样作死')

        if not os.path.exists(filename):
            return mw.returnData(False, '指定文件不存在!')

        os.system('chmod ' + sall + ' ' + access + " '" + filename + "'")
        os.system('chown ' + sall + ' ' + user + ':' + user + " '" + filename + "'")
        msg = mw.getInfo('设置[{1}]权限为[{2}]所有者为[{3}]', (filename, access, user,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '设置成功!')
    except Exception as e:
        return mw.returnData(False, '设置失败!'+str(e))

def getSysUserList():
    pwd_file = '/etc/passwd'
    if os.path.exists(pwd_file):
        content = mw.readFile(pwd_file)
        clist = content.split('\n')
        sys_users = []
        for line in clist:
            if line.find(":")<0:
                continue
            lines = line.split(":",1)
            sys_users.append(lines[0])
        return sys_users
    return ['root','mysql','www']

def fileDelete(path):
    if not os.path.exists(path):
        return mw.returnData(False, '指定文件不存在!')

    # 检查是否为.user.ini
    if path.find('.user.ini') >= 0:
        cmd = "which chattr && chattr -i {0}".format(path)
        mw.execShell(cmd)

    try:
        recycle_bin = thisdb.getOption('recycle_bin')
        if recycle_bin == 'open':
            if mvRecycleBin(path):
                return mw.returnData(True, '已将文件移动到回收站!')
            return mw.returnData(False, '移动到回收站失败!') 
        os.remove(path)
        mw.writeLog('文件管理', mw.getInfo('删除文件[{1}]成功!', (path,)))
        return mw.returnData(True, '删除文件成功!')
    except Exception as e:
        return mw.returnData(False, '删除文件失败!')

def dirDelete(path):
    if not os.path.exists(path):
        return mw.returnData(False, '指定文件不存在!')

    # 检查是否为.user.ini
    if path.find('.user.ini'):
        os.system("which chattr && chattr -i '" + path + "'")
    try:
        recycle_bin = thisdb.getOption('recycle_bin')
        if recycle_bin == 'open':
            if mvRecycleBin(path):
                return mw.returnData(True, '已将文件移动到回收站!')
        mw.execShell('rm -rf ' + path)
        mw.writeLog('文件管理', '删除{1}成功！', (path,))
        return mw.returnData(True, '删除文件成功!')
    except:
        return mw.returnData(False, '删除文件失败!')

# 关闭
def toggleRecycleBin():
    recycle_bin = thisdb.getOption('recycle_bin')
    if recycle_bin == 'open':
        thisdb.setOption('recycle_bin','close')
        mw.writeLog('文件管理', '已关闭回收站功能!')
        return mw.returnData(True, '已关闭回收站功能!')
    else:
        thisdb.setOption('recycle_bin','open')
        mw.writeLog('文件管理', '已开启回收站功能!')
        return mw.returnData(True, '已开启回收站功能!')

def getRecycleBin():
    rb_dir = mw.getRecycleBinDir()
    recycle_bin = thisdb.getOption('recycle_bin')

    data = {}
    data['dirs'] = []
    data['files'] = []
    data['status'] = False
    if recycle_bin == 'open': 
        data['status'] = True
    
    for file in os.listdir(rb_dir):
        try:
            tmp = {}
            fname = rb_dir+'/'+ file
            tmp1 = file.split('_mw_')
            tmp2 = tmp1[len(tmp1) - 1].split('_t_')
            tmp['rname'] = file
            tmp['dname'] = file.replace('_mw_', '/').split('_t_')[0]
            tmp['name'] = tmp2[0]
            tmp['time'] = int(float(tmp2[1]))
            if os.path.islink(fname):
                filePath = os.readlink(fname)
                link = ' -> ' + filePath
                if os.path.exists(filePath):
                    tmp['size'] = os.path.getsize(filePath)
                else:
                    tmp['size'] = 0
            else:
                tmp['size'] = os.path.getsize(fname)
            if os.path.isdir(fname):
                data['dirs'].append(tmp)
            else:
                data['files'].append(tmp)
        except Exception as e:
            continue

    return mw.returnJson(True, 'OK', data)

# 移动到回收站
def mvRecycleBin(path):
    rb_dir = mw.getRecycleBinDir()
    rb_file = rb_dir + '/' + path.replace('/', '_mw_') + '_t_' + str(time.time())
    try:
        import shutil
        shutil.move(path, rb_file)
        mw.writeLog('文件管理', mw.getInfo('移动[{1}]到回收站成功!', (path,)))
        return True
    except Exception as e:
        mw.writeLog('文件管理', mw.getInfo('移动[{1}]到回收站失败!', (path,)))
        return False

# 回收站文件恢复
def reRecycleBin(path):
    rb_dir = mw.getRecycleBinDir()
    dst_file = path.replace('_mw_', '/').split('_t_')[0]
    try:
        import shutil
        shutil.move(rb_dir + '/' + path, dst_file)
        msg = mw.getInfo('移动文件[{1}]到回收站成功!', (dst_file,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(True, '恢复成功!')
    except Exception as e:
        msg = mw.getInfo('从回收站恢复[{1}]失败!', (dst_file,))
        mw.writeLog('文件管理', msg)
        return mw.returnData(False, '恢复失败!')


def closeRecycleBin():
    rb_dir = mw.getRecycleBinDir()
    mw.execShell('which chattr && chattr -R -i ' + rb_dir)
    rlist = os.listdir(rb_dir)
    i = 0
    l = len(rlist)
    for name in rlist:
        i += 1
        path = rb_dir + '/' + name
        mw.writeSpeed(name, i, l)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    mw.writeSpeed(None, 0, 0)
    mw.writeLog('文件管理', '已清空回收站!')
    return mw.returnJson(True, '已清空回收站!')


# 设置文件和目录权限
def setMode(path):
    s_path = os.path.dirname(path)
    p_stat = os.stat(s_path)
    os.chown(path, p_stat.st_uid, p_stat.st_gid)
    os.chmod(path, p_stat.st_mode)


def closeLogs():
    log_file = mw.getLogsDir()
    os.system('rm -rf ' + log_file + '/*')
    mw.opWeb('reload')
    # os.system('kill -USR1 `cat ' + mw.getServerDir() +'/openresty/nginx/logs/nginx.pid`')
    mw.writeLog('文件管理', '网站日志已被清空!')
    tmp = getDirSizeByBash(log_file)
    return mw.returnData(True, tmp)
