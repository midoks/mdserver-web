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

import core.mw as mw

# 获取文件权限描述
def getFileStatsDesc(
    filename: str | None = None,
    path: str | None = None,
):
    if path is None or filename is None:
        return ';;;;;'
    filename = filename.replace('//', '/')
    try:
        stat = os.stat(filename)
        accept = str(oct(stat.st_mode)[-3:])
        mtime = str(int(stat.st_mtime))
        user = ''
        try:
            user = str(pwd.getpwuid(stat.st_uid).pw_name)
        except:
            user = str(stat.st_uid)
        size = str(stat.st_size)
        link = ''
        if os.path.islink(filename):
            link = ' -> ' + os.readlink(filename)

        if path:
            path_t = (path + '/').replace('//', '/')
            filename = filename.replace(path_t, '', 1)

        return filename + ';' + size + ';' + mtime + ';' + accept + ';' + user + ';' + link
    except Exception as e:
        print(str(e))
        return ';;;;;'


def sortFileList(path, ftype = 'mtime', sort = 'desc'):
    flist = os.listdir(path)
    if ftype == 'mtime':
        if sort == 'desc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=True)
        if sort == 'asc':
            flist = sorted(flist, key=lambda f: os.path.getmtime(os.path.join(path,f)), reverse=False)

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
        stat = getFileStatsDesc(dst_file, path)
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

        stats = getFileStatsDesc(abs_file, path)
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
            size += os.path.getsize(os.path.join(root, f))
            # print(f)
    return size

# 获取目录大小(bash)
def getDirSizeByBash(path):
    tmp = mw.execShell('du -sh ' + path)
    return tmp[0].split()[0]

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