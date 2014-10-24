import tornado.web
import builtins
import config

try:
    Web
except:
    Web = tornado.web.Application([(r'/static/(.*)$', tornado.web.StaticFileHandler, {'path': config.dataDirectory + '/web_static/'})]);
    builtins.Web = Web

