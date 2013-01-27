from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File
import game.scriptsystem

class Default(Resource):
    def render_GET(self, request):
        return 'No page'

default = Default()

class Page(Resource):
    def getChild(self, path, request):
        req = game.scriptsystem.get("webPage").runSync(path, None, request=request)
        if req:
            return req

class Web(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("static", File("data/web_static"))

    def getChild(self, path, request):
        req = game.scriptsystem.get("webPage").runSync(path, None, request=request)
        if req:
            return req
        else:
            return default

class WebFactory(Site):
    pass
