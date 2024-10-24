import re

class RequestHandler:
    def __init__(self,prefixUrl,method,options):
        self.prefixUrl = prefixUrl
        self.method = method
        self.options = options

    def can_handle(self, method, path):
        return False

    def handle_path(self, method, path):
        return None

    def error404(self, resolvedPath):
        return {"resolved":resolvedPath, "status":404, "content-type":"text/plain", "content":bytes("404 Not Found","UTF-8")}