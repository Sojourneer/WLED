#!/usr/bin/env python3
import time
from http.server import HTTPServer
from server import WLEDServer, WLEDHandler
from response.simpleFileHandler import SimpleFileHandler

HOST_NAME = '127.0.0.1'
PORT_NUMBER = 80

if __name__ == '__main__':
    httpd = WLEDServer((HOST_NAME, PORT_NUMBER), WLEDHandler)

    httpd.on("/json/", "GET", SimpleFileHandler, {
        "mapper": lambda url: url.replace("/json/","I18N/data/") + ".json"
    })
    httpd.on("/presets.json", "GET", SimpleFileHandler, {"file":"I18N/data/presets.json"})
    httpd.on("/langs/", "GET", SimpleFileHandler, {"root":"I18N/langs/" })
    httpd.on("/settings/s.js", "GET", SimpleFileHandler, {"file":"scripts/s.js"})
    httpd.on("/settings/style.css", "GET", SimpleFileHandler, {"file":"data/style.css"})
    httpd.on("/settings/", "GET", SimpleFileHandler, {
        "mapper": lambda url: url.replace("/settings/","data/settings_") + ".htm"})
    httpd.on("/settings", "GET", SimpleFileHandler, {"file":"data/settings.htm"})
    httpd.on("/scripts/", "GET", SimpleFileHandler, {"root":"scripts/"})
    httpd.on("/", "GET", SimpleFileHandler, {"root":"data/", "default":"data/index.htm"})

    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))