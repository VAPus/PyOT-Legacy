from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.static import File

class Web(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.putChild("static", File("data/web_static"))

class WebFactory(Site):
    pass
