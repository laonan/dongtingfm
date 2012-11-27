# coding=utf-8
import httplib, urllib
from urlparse import urlparse

def downloadMp3(self, mp3url):
    params = {}
    parts = urlparse(mp3url)
    useragent = 'podcast-fetcher-example'
    allowedmimes = ['text/html']
    allowedextns = ['', '.mp3']
    maxcontentbytes = 40000
 
    headers = {
               'Host': parts.netloc,
               'User-agent': useragent,
               'Accept': ','.join(allowedmimes),
               'Range': 'bytes=0-%(maxcontentbytes)d' %locals()
               }
 
    try:
        conn = httplib.HTTPConnection(parts.netloc)
        path = parts.path
        conn.request('GET', path, params, headers)
        response = conn.getresponse()
        # To read real file size
        contentLen = 0
 
       # If Range is not supported, just download first max bytes
        if response.status == 200 :
            if response.getheader("content-length") != None :
                contentLen = int(response.getheader("content-length"))
 
       # Handle Redirect
        elif response.status == 302 :
            newurl = response.getheader("location")
            self.downloadMp3(newurl)
       # Range response
        elif response.status == 206 :
 
            """ Response example 'content-range', 'bytes 0-40000/3796992"""
            field = response.getheader("content-range")
            contentLen = int( field[field.find("/")+1:] )
 
       # We are not handling errors here
        if response.status > 299 :
            conn.close()
            return False
 
        # Size if not big enough to calculate bitrate
        if contentLen < maxcontentbytes:
            conn.close()
            return False
 
        data = response.read(maxcontentbytes)
        # create/open temporary file
        file = open('tmp/temp.mp3', 'wb')
        # truncate if exists already
        file.truncate(0)
        file.write(data)
 
        # make space for ID3v1 if any
        file.seek(contentLen - 128, 0)
        response.close()
 
        # if supports partial request we read last 128 bytes for ID3v1
        if response.status == 206 :
            conn = httplib.HTTPConnection(parts.netloc)
            # Range: bytes=-128 will read is last 128 bytes
 
            headers2 = {
                   'User-agent': useragent,
                   'Accept': ','.join(allowedmimes),
                   'Range': 'bytes=-128' %locals()
            }
 
            conn.request("GET", path, params, headers2)
            response2 = conn.getresponse()
            file.write(response2.read(128))
            response2.close()
 
           # otherwise just append 128 to file
        else :
            file.seek(128, 1)
 
        file.close()
        conn.close()
 
    except Exception, msg :
        conn.close()
        #print self.name + "Error downloading info: " + str(msg)
        return False
 
    return True

