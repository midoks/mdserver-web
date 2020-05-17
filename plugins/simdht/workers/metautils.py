#coding: utf8
import os
import binascii

cats = {
    u'video': u'Videos',
    u'image': u'Images',
    u'document': u'Books',
    u'music': u'Musics',
    u'package': u'Packages',
    u'software': u'Softwares',
}

def get_label(name):
    if name in cats:
        return cats[name]
    return u'Others'

def get_label_by_crc32(n):
    for k in cats:
        if binascii.crc32(k)&0xFFFFFFFFL == n:
            return k
    return u'other'

def get_extension(name):
    return os.path.splitext(name)[1]

def get_category(ext):
    ext = ext + '.'
    cats = {
        u'video': '.avi.mp4.rmvb.m2ts.wmv.mkv.flv.qmv.rm.mov.vob.asf.3gp.mpg.mpeg.m4v.f4v.',
        u'image': '.jpg.bmp.jpeg.png.gif.tiff.',
        u'document': '.pdf.isz.chm.txt.epub.bc!.doc.ppt.',
        u'music': '.mp3.ape.wav.dts.mdf.flac.',
        u'package': '.zip.rar.7z.tar.gz.iso.dmg.pkg.',
        u'software': '.exe.app.msi.apk.'
    }
    for k, v in cats.iteritems():
        if ext in v:
            return k
    return u'other'

def get_detail(y):
    if y.get('files'):
        y['files'] = [z for z in y['files'] if not z['path'].startswith('_')]
    else:
        y['files'] = [{'path': y['name'], 'length': y['length']}]
    y['files'].sort(key=lambda z:z['length'], reverse=True)
    bigfname = y['files'][0]['path']
    ext = get_extension(bigfname).lower()
    y['category'] = get_category(ext)
    y['extension'] = ext


