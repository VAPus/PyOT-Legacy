import tornado.web
import builtins

Web = tornado.web.Application([(r'/static/', tornado.web.StaticFileHandler)]);
builtins.Web = Web

