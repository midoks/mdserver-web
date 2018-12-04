# coding: utf-8

import sys
import json


def downloadFile(url, filename):
    import urllib
    urllib.urlretrieve(url, filename=filename, reporthook=downloadHook)


def downloadHook(count, blockSize, totalSize):
    speed = {'total': totalSize, 'block': blockSize, 'count': count}
    print speed
    print '%02d%%' % (100.0 * count * blockSize / totalSize)
    writeFile('/tmp/mdserver-web.log', json.dumps(speed))


def writeFile(filename, str):
    # 写文件内容
    try:
        fp = open(filename, 'w+')
        fp.write(str)
        fp.close()
        return True
    except:
        return False

if __name__ == "__main__":
    url = sys.argv[1]
    downloadFile(url, 'mdserver-web.zip')
