#!/usr/bin/env python

import requests

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    pass

import httplib, mimetypes, urlparse, json, time
import traceback

class YDMHttp:

    apiurl = 'http://api.yundama.com/api.php'
    
    def __init__(self, username, password, appid, appkey):
        self.username = username  
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=None):
        try:
            response = post_url(self.apiurl, fields, files)
            response = json.loads(response)
        except Exception as e:
            print traceback.format_exc()
            response = None
        return response
    
    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001
        
    def report(self, captcha_id):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey,
                'cid': str(captcha_id), 'flag': '0' 
                }
        response = self.request(data)
        return response.get('ret') if response and 'ret' in response else -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, content, codetype, timeout):
        data = {'method': 'upload', 'username': self.username,
                'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        stream = {'file': content}
        response = self.request(data, stream)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid, 'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, content, codetype, timeout):
        cid = self.upload(content, codetype, timeout)
        if cid > 0:
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

######################################################################

def post_url(url, fields, files=None):
    urlparts = urlparse.urlsplit(url)
    return post_multipart(urlparts[1], urlparts[2], fields, files)

def post_multipart(host, selector, fields, files):
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('Host', host)
    h.putheader('Content-Type', content_type)
    h.putheader('Content-Length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files=None):
    BOUNDARY = 'WebKitFormBoundaryJKrptX8yPbuAJLBQ'

    CRLF = '\r\n' 

    L = [] 
    for field in fields:

        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"' % field) 
        L.append('') 
        L.append(fields[field]) 

    files = files if files else [] 
    fn = 'verify.jpg'
    for field in files:

        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (field, fn))
        L.append('Content-Type: %s' % get_content_type(fn)) 
        L.append('')
        L.append(files[field])

    L.append('--' + BOUNDARY + '--') 
    L.append('')

    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

    return content_type, body 

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
