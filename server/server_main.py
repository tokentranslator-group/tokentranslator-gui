# python3 -m server.server_main

import tornado
import tornado.ioloop
import tornado.web
import os
import json
from model.model_main import TokenizerDB
from model.model_main import SignaturesDB
from model.model_main import ExamplesDB

from server.server_handlers_special import DialectHandlers


class MyStaticFileHandler(tornado.web.StaticFileHandler):

    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control',
                        ('no-store, no-cache,'
                         + ' must-revalidate, max-age=0'))
            

def make_app(handlers):
    settings = {
        "template_path": os.path.join(os.path
                                      .dirname(os.path
                                               .dirname(__file__)),
                                      "client", "templates"),
        "static_path": os.path.join(os.path
                                    .dirname(os.path
                                             .dirname(__file__)),
                                    "client"),
        "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        "login_url": "/login",
        "xsrf_cookies": False,
        "debug": True,
    }
    print("template_path:")
    print(settings["template_path"])

    return tornado.web.Application([
        #html
        (r"/", handlers.MainHandler),
        (r"/net", handlers.NetHandler),
        (r"/sampling", handlers.SamplingHandler),
        (r"/sampling_desk", handlers.SamplingDeskHandler),
        (r"/lex_tutorial_0", handlers.LexTut0Handler),
        (r"/login", handlers.SignInHandler),
        (r"/logout", handlers.LogoutHandler),
        (r"/signup", handlers.SignUpHandler),
        
        #api
        # (r"/api/tree", TreeHandler),
        # (r"/api/editor", EditorHandler),
        
        (r"/api/net_parsing", handlers.NetHandlerParsing),
        (r"/api/tables/path", handlers.PathHandler),
        (r"/api/tables/dialect", handlers.DialectTableHandler),
        (r"/api/tables/replacer", handlers.ReplacerHandler),
        (r"/api/tables/signatures", handlers.SignaturesHandler),
        (r"/api/tables/signatures_code", handlers.SignaturesCodeHandler),
        
        (r"/api/tables/examples_db_table", handlers.ExamplesDBTableHandler),
        # (r"/api/tables/examples_db_sampler_table", handlers.SamplerDBTableHandler),
        # (r"/api/tables/examples_db_eqs_table", handlers.EqsDBTableHandler),
        # (r"/api/tables/examples_db_cs_table", handlers.CsDBTableHandler),

        (r"/api/tables/examples_db_editor", handlers.ExamplesDBEditorHandler),
        # (r"/api/tables/examples_db_sampler_editor", handlers.SamplerDBEditorHandler),
        # (r"/api/tables/examples_db_eqs_editor", handlers.EqsDBEditorHandler),
        # (r"/api/tables/examples_db_cs_editor", handlers.CsDBEditorHandler),

        (r"/api/tables/user", handlers.UsersTableHandler),

        # statics from /client folder
        (r"/static/", MyStaticFileHandler,
         dict(path=settings['static_path'])), ], **settings)


def run():
    model = TokenizerDB()
    model.load_all_tables()

    model_signatures = SignaturesDB()
    model_signatures.load_all_tables()

    model_examples_sampler = ExamplesDB("examples_sampler")

    handlers = DialectHandlers(model, model_signatures, model_examples_sampler)

    app = make_app(handlers)
    port = 8888
    print("http://localhost:" + str(port) + "/")
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
