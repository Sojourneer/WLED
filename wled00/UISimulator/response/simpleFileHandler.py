import re
import os
from response.requestHandler import RequestHandler

#TBD paths relative or not how they are specified etc.

class SimpleFileHandler(RequestHandler):
    def __init__(self, prefixUrl, method, options):
        super().__init__(prefixUrl, method, options),
        self.extensions = {
            ".htm":  {"ct": "text/html", "enc":lambda text: bytes(text,"UTF-8"), "mode":"r"},
            ".html": {"ct": "text/html", "enc":lambda text: bytes(text,"UTF-8"), "mode":"r"},
            ".css": {"ct": "text/css", "enc":lambda text: bytes(text,"UTF-8"), "mode":"r"},
            ".json": {"ct": "application/json", "enc":lambda text: bytes(text,"UTF-8"), "mode":"r"},
            ".js":   {"ct": "text/javascript", "enc":lambda text: bytes(text,"UTF-8"), "mode":"r"},
            ".ico":  {"ct": "image/vnd.microsoft.icon", "enc": lambda d: d, "mode":"rb"},
            ".icon":  {"ct": "image/vnd.microsoft.icon", "enc": lambda d: d, "mode":"rb"}
        }
        # { "root":folder, "file":relativePath}

    def can_handle(self, method, path):
        #print("can_handle",method,url,self.prefixUrl,self.method)
        if not path.startswith(self.prefixUrl): return False
        if self.method != "*" and self.method != method: return False
        return True

    def handle_path(self, method, parsedUrl):
        path = parsedUrl.path
        if not self.can_handle(method, path): return None

        if path == "/":
            fpath = self.options["root"] + "index.htm"
            if not os.path.exists(fpath): return self.error404()
            return self.respondFile(fpath)

        if "file" in self.options:
            fpath = self.options["file"] # directory???
            print(path, self.options, fpath)
            if not os.path.exists(fpath): return self.error404()
            return self.respondFile(fpath)

        elif "root" in self.options:
            fpath = path.replace(self.prefixUrl,self.options["root"],1)
            print(path, self.options, fpath)
            if not os.path.exists(fpath): return self.error404(path)
            return self.respondFile(fpath)

        elif "mapper" in self.options:
            fpath = self.options["mapper"](path)
            print(path, self.options, fpath)
            return self.respondFile(fpath)

        
    def respondFile(self, fpath):
        extension = os.path.splitext(fpath)[1]
        if extension in self.extensions:
            spec = self.extensions[extension]
        else:
            spec = {"ct":None, "enc":lambda x: x, "mode":"r"}

        try:
            #print("1")
            content = open(fpath, spec["mode"]).read()
            #print("2")
            content = spec["enc"](content)
            #print("3")
            return {"resolved":fpath, "status":200, "content-type":spec["ct"], "content":content}
        except Exception as err:
            print("Exception for path {}: {}".format(fpath, err), spec)
            return {"resolved":fpath, "status":500, "content-type":"text/plain", "content":bytes("500 Internal Server Error","UTF-8")}
