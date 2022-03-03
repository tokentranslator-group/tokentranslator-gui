from server.server_handlers_base import Handlers
import json

from tokentranslator.translator.main.parser_general import ParserGeneral
from tokentranslator.env.equation_net.equation import Equation
from tokentranslator.env.equation.data.terms.output.cpp.postproc import delay_postproc
from tokentranslator.env.clause.clause_main import Clause

from proposalsampler.sampling.vars.vars_extractor import Extractor
import proposalsampler.sampling.vars.vars_maps as vms

from proposalsampler.sampling.slambda import slambda_main as sm
# from tokentranslator.translator.sampling.slambda.data.stable import stable_fixed
# from tokentranslator.translator.sampling.slambda.data.stable import stable

from functools import reduce


class DialectHandlers(Handlers):

    def __init__(self, model, model_signatures, model_examples):
        
        Handlers.__init__(self, model, model_signatures, model_examples)

        self.create_dialect_handlers()
        # self.create_dialect_login_handlers()

    def get_parser_data(self, dialect_name):
        if dialect_name == "eqs":
            self.equation.parser.show_patterns()
        elif dialect_name == "cs":
            self.clause.parser.show_patterns()

    def create_dialect_handlers(self):
    
        # self.path_cs = "env/clause/data/terms/input/demo_dialect.db"
        # self.path_eqs = "env/equation_net/data/terms/input/demo_dialect.db"

        TableHandler = self.TableHandler
        model = self.model
        model_signatures = self.model_signatures

        model_examples = self.model_examples

        global_self = self
        
        # FOR parsers (for get_parser_data in other handlers besides parser):
        
        global_self.equation = Equation("2+2=4", db=global_self.model)
        global_self.clause = Clause("paralelogram(A)"
                                    + " \\and romb(A) => square(A)",
                                    db=global_self.model)
        # END FOR

        # FOR replacers:
        global_self.replacer_sources = {}
        # END FOR

        # FOR sampler:
        '''
        mid_terms = ["clause_where", "clause_for", "clause_into",
                     "def_0", "in_0",
                     "if", "if_only", "if_def",
                     "clause_or", "conj"]
        vars_terms = ["set", "var"]
        '''
        self.sampler = sm.Sampler()

        # self.sampler = sm.ValTableSampling(None, None,
        #                                    stable, stable_fixed,
        #                                    mid_terms, vars_terms)
        # END FOR

        class DialectTableHandler(TableHandler):

            def update_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    selected = model.select_pattern(entry["term_name"])
                    
                    if selected.count == 0:
                        model.add_pattern(dict([(key, entry[key])
                                                for key in entry
                                                if key != "id"]))
                    elif selected.count == 1:
                        model.edit_pattern(entry["term_name"],
                                           dict([(key, entry[key])
                                                 for key in entry
                                                 if key != "id"]))
                    else:
                        raise(BaseException("Too many elements with"
                                            + " same term_name in table"))

                data = model.show_all_entries()

                # delete entries, not contained in data
                # for entry in data[]:
                    
                return(data)

            def delete_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    model.del_pattern(entry["term_name"])

                data = model.show_all_entries()
                    
                return(data)

            def load_table(self, dialect=None):

                '''Method for get'''
                if dialect is not None:
                    model.change_dialect_db(dialect)
            
                data = model.show_all_entries()
                return(data)
                '''
                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
                '''

        self.DialectTableHandler = DialectTableHandler

        class NetHandlerParsing(self.BaseHandler):
            # @tornado.web.authenticated
            def post(self):
                
                '''Get data, define what to do (delete/update)
                return remained.'''

                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM NetHandlerParsing.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:

                global_self.get_parser_data(data_json["dialect"])

                data = self.parse(data_json["dialect"], [data_json["text"]],
                                  data_json["params"])
        
                # for save to examples_db:
                # data["text"] = data_json["text"]

                print("\ndata_to_send:")
                print(data)

                # data = {"lex": "hello from lex", "net": "hello from net"}
                # END FOR
                
                # send back new data:
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            def parse(self, dialect_name, sent_list, params):
                
                '''Parse data from client with use of ParserGeneral.
                
                Inputs:
                
                - ``dialect_name`` -- either "eqs" or "cs". Will be
                used for both lex pattern and grammar_fmw choicing.
                
                - ``sent_list`` list< containing one sent to parse.

                Outputs:
                
                out["lex"] is result of lex step.
                out["net"] serializable net data.
                '''

                # choice grammar for dialect:
                if dialect_name == "eqs":
                    
                    # in case it was changed:
                    global_self.model.change_dialect_db(dialect_name)

                    # parse and save:
                    eq = Equation(sent_list[0], db=global_self.model)
                    eq.parser.parse()
                    self.equation = eq
                    
                    # FOR params:
                    editor = eq.replacer.cpp.editor
                    editor.set_default()
                    print("params")
                    print(params)

                    editor.set_dim(dim=int(params["dim"]))

                    bn = int(params["blockNumber"])
                    editor.set_blockNumber(blockNumber=bn)

                    vidxs = eval(params["vars_idxs"])
                    editor.set_vars_indexes(vars_to_indexes=vidxs)

                    coeffs = eval(params["coeffs"])
                    editor.set_coeffs_indexes(coeffs_to_indexes=coeffs)

                    params["btype"] = int(params["btype"])
                    params["side"] = int(params["side"])
                    params["vertex_sides"] = eval(params["vertex_sides"])
                    params["firstIndex"] = int(params["firstIndex"])
                    params["secondIndexSTR"] = int(params["secondIndexSTR"])
                    eq.replacer.cpp.editor.set_diff_type(**params)
                    shape = eval(params["shape"])
                    eq.replacer.cpp.editor.set_shape(shape=shape)
                    # END FOR

                    # because we don't use system here,
                    # delays raplacment complying manualy:
                    eq.replacer.cpp.make_cpp()
                    nodes = [[node for node in eq.get_all_nodes()]]
                    replacers = [eq.replacer.cpp.gen]
                    delay_postproc(replacers, nodes)

                    eq.replacer.sympy.make_sympy()

                    net_out = eq.net_out
                    lex_out = eq.lex_out

                elif dialect_name == "cs":
                    parser = self.parse_cs(sent_list)
                    net_out = parser.net_out

                    # for vtable:
                    global_self.sampler.set_parsed_net(net_out)
                    try:
                        net_out, nodes_idds = global_self.sampler.editor_step()
                        vtable_skeleton = (global_self.sampler
                                           .get_vtable_skeleton())
                    except:
                        vtable_skeleton = None
                    # lex_out = parser.parsers["hol"].lex_out
                    lex_out = parser.lex_out
                    
                vars_extractor = Extractor(dialect_name)
                net_vars = vms.get_args(str(["s"]), net_out,
                                        vars_extractor)

                print("lex_out:")
                print(lex_out)
                print("\nget_args:")
                print(net_vars)
                # print('D.node[str(["s"])]["vars"]')
                # print(D.node[str(["s"])]["vars"])
                if dialect_name == "eqs":
                    vms.subs(net_out, net_vars, a=7, c=8)
                elif dialect_name == "cs":
                    vms.subs(net_out, net_vars, G="s(3)")

                # generate json out again:
                if dialect_name == "eqs":
                    json_out = eq.json_out
                elif dialect_name == "cs":
                    # refill json since sampler update:
                    parser.parser.gen_json(net_out)
                    json_out = parser.json_out
                print("\nparser.json_out:")
                print(json_out)

                # print("\nparser.json_out:")
                # print(parser.json_out)
                out = {"lex": reduce(lambda acc, x: acc + " " + str(x),
                                     lex_out, ""),
                       "net": json_out,
                       "vars": net_vars}

                # add replacer data:
                if dialect_name == "eqs":
                    out["eq_cpp"] = eq.replacer.cpp.get_cpp()
                    out["eq_sympy"] = eq.eq_sympy
                
                out["slambda"] = {}
                # add slambda data:
                if dialect_name == "cs":
                    out["slambda"]["vtable_skeleton"] = vtable_skeleton
                return(out)

            def parse_cs(self, sent_list):

                global_self.model.change_dialect_db("cs")
                clause = Clause(sent_list[0], db=global_self.model)
                clause.parser.parse()
                self.clause = clause
                return(clause)

        self.NetHandlerParsing = NetHandlerParsing

        class NetHandler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM NetHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_net.htm", username="default")
                # self.redirect("/login")

        self.NetHandler = NetHandler

        class SamplingHandler(self.NetHandlerParsing):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM SamplingHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:
                mode = data_json["mode"]
                if mode == "parse":
                    global_self.sent_list = [data_json["text"]]
                    data = self.parse(data_json["dialect"],
                                      [data_json["text"]],
                                      data_json["params"])
                
                    stable_send = global_self.sampler.get_stable()
                    # for entry_key in stable:
                    #     stable_send[entry_key] = [str(sign)
                    #                               for sign in stable[entry_key]]
                    data["slambda"]["stable"] = stable_send
                    
                elif mode == "sampling":
                    print("data_json")
                    print(data_json)

                    # FOR reinit net_out and nodes_idds:
                    parser = self.parse_cs(global_self.sent_list)
                    net_out = parser.net_out
                    global_self.sampler.set_parsed_net(net_out)
                    # net_out, nodes_idds = global_self.sampler.editor_step()
                    # END FOR

                    # data = self.run_sampling(data_json[""])
                    vtnames = data_json["vtnames"]
                    vtvalues = data_json["vtvalues"]
                    init_ventry = dict([(vtnames[idx], eval(vtvalues[idx]))
                                        if vtvalues[idx] != ""
                                        else (vtnames[idx], None)
                                        for idx in range(len(vtnames))])
                    print("init_ventry:")
                    print(init_ventry)
                    global_self.sampler.set_init_ventry(init_ventry)
                    out = global_self.sampler.run()
                    # print("\nsampling json (for cy) result:")
                    # print(out)
    
                    print("\nsampling successors:")
                    print(global_self.sampler.get_successors())

                    data = {}

                    # transform values to str:
                    successors = [dict([(idx, str(successor[idx]))
                                        for idx in successor])
                                  for successor in global_self.sampler.get_successors()]
                    data["successors"] = successors
                    data["vesnet"] = out
                else:
                    print("unknown mode")
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)

                # for save to examples_db:
                # data["text"] = data_json["text"]

                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):

                print("FROM SamplingHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_sampling.htm", username="default")
                # self.redirect("/login")
                
        self.SamplingHandler = SamplingHandler

        class SamplingDeskHandler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM SamplingDeskHandler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_sampling_desk.htm", username="default")
                # self.redirect("/login")

        self.SamplingDeskHandler = SamplingDeskHandler

        class ReplacerHandler(self.BaseHandler):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM ReplacerHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:
                action = data_json["action"]
                dialect_name = data_json["dialect_name"]

                # like ('br_left', [True, False, False]) |-> True:
                brackets = eval(data_json["brackets"])[0] in ["br_left", "br_right"]
                # print("brackets:")
                # print(brackets)

                term_name = data_json["term_name"]
                replacer = global_self.equation.replacer

                if action == "set":
                    code = data_json["code"]
                    replacer.set_pattern(dialect_name, term_name,
                                         code, brackets)
                    sources = replacer.load_patterns_source(dialect_name, brackets)
                    global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = sources[term_name]

                elif action == "load":
                    # check if alredy loaded:
                    if (dialect_name, brackets) in global_self.replacer_sources:
                        sources = global_self.replacer_sources[(dialect_name, brackets)]
                    else:
                        sources = replacer.load_patterns_source(dialect_name, brackets)
                        global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = sources[term_name]

                elif action == "remove":
                    replacer.remove_patterns(dialect_name, [term_name])
                    sources = replacer.load_patterns_source(dialect_name, brackets)
                    global_self.replacer_sources[(dialect_name, brackets)] = sources
                    term_source = "# term %s removed successfuly\n" % (term_name)
                    term_source += "# check terms list for shure"

                else:
                    print("no such action: %s" % (action))

                print("aveilable_terms:")
                aveilable_terms = list(sources.keys())
                print(list(sources.keys()))
                available_terms_str = " ".join(aveilable_terms)
                if brackets:
                    available_terms_str += " (for brackets only)"
                data = {"source": term_source,
                        "available_terms": available_terms_str}
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM ReplacerHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.ReplacerHandler = ReplacerHandler

        class SignaturesHandler(TableHandler):

            def update_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    selected = (model_signatures
                                .select_pattern(entry["predicate"],
                                                entry["signature"]))
                    print("selected:")
                    print(selected)
                    if selected.count == 0:
                        model_signatures.add_pattern(dict([(key, entry[key])
                                                           for key in entry
                                                           if key != "id"]))
                    elif selected.count == 1:
                        model_signatures.edit_pattern(entry["predicate"],
                                                      entry["signature"],
                                                      dict([(key, entry[key])
                                                            for key in entry
                                                            if key != "id"]))
                    else:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))

                data = model_signatures.show_all_entries()

                # delete entries, not contained in data
                # for entry in data[]:
                    
                return(data)

            def delete_action(self, data: dict)->dict:

                '''Method for post'''

                for entry in data:
                    model_signatures.del_pattern(entry["predicate"],
                                                 entry["signature"])

                data = model_signatures.show_all_entries()
                    
                return(data)

            def load_table(self, dialect=None):

                '''Method for get'''

                if dialect is not None:
                    print("dialect: ", dialect)
                    model_signatures.change_dialect_db(dialect)
            
                data = model_signatures.show_all_entries()
                
                return(data)
                '''
                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
                '''

        self.SignaturesHandler = SignaturesHandler

        class SignaturesCodeHandler(self.BaseHandler):

            # @tornado.web.authenticated
            def post(self):
                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM ReplacerHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                
                # FOR data update:
                action = data_json["action"]
                dialect_name = data_json["dialect_name"]
                                
                predicate = data_json["predicate"]
                signature = data_json["signature"]

                if action == "set":
                    # save new code:
                    code = data_json["code"]
                    model_signatures.edit_pattern(predicate, signature,
                                                  {"code": code})

                    # take it back:
                    res = model_signatures.select_pattern(predicate, signature)
                    if res.count > 1:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))
                    term_source = res.res[0]['code']

                elif action == "load":

                    res = model_signatures.select_pattern(predicate, signature)
                    if res.count > 1:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))
                    term_source = res.res[0]['code']

                elif action == "remove":
                    term_source = "must alredy be removed in SignaturesHandler"

                else:
                    print("no such action: %s" % (action))
                '''
                print("aveilable_terms:")
                aveilable_terms = list(sources.keys())
                print(list(sources.keys()))
                available_terms_str = " ".join(aveilable_terms)
                '''
                data = {"source": term_source}
                '''
                data = {"source": term_source,
                        "available_terms": available_terms_}
                '''
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM ReplacerHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.SignaturesCodeHandler = SignaturesCodeHandler

        '''
        def make_examples_handler():
            def decorator(hclass):
                @functools.wraps(hclass)
                def wrapper(*args):
                    hclass(*args, table_name)
                # make callback for button
                fState.buttons[button_name].on_click(wrapper)
                return(wrapper)
            return(decorator)
            
        @functools.wraps(ExamplesDBTableHandler)
        def SamplerExamplesHandler(*args):
            return(hclass(*args, table_name))
        '''

        class ExamplesDBTableHandler(TableHandler):

            def update_action(self, data: dict)->dict:

                '''Method for post'''
                
                # this must be overridden in ancestors:
                # model_examples = self.model_examples

                for entry in data:
                    selected = (model_examples
                                .select_pattern(entry["id"]))
                    print("selected:")
                    print(selected)
                    if selected.count == 0:
                        model_examples.add_pattern(dict([(key, entry[key])
                                                         for key in entry
                                                         if key != "id"]))
                    elif selected.count == 1:
                        model_examples.edit_pattern(entry["id"],
                                                    dict([(key, entry[key])
                                                          for key in entry
                                                          if key != "id"]))
                    else:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))

                data = model_examples.show_all_entries()

                # delete entries, not contained in data
                # for entry in data[]:
                    
                return(data)

            def delete_action(self, data: dict)->dict:

                '''Method for post'''

                # this must be overridden in ancestors:
                # model_examples = self.model_examples

                for entry in data:
                    model_examples.del_pattern(entry["id"])

                data = model_examples.show_all_entries()
                    
                return(data)

            def load_table(self, dialect=None):

                '''Method for get'''
                # this must be overridden in ancestors:
                # model_examples = self.model_examples

                if dialect is not None:
                    print("dialect: ", dialect)
                    model_examples.change_dialect_db(dialect)
            
                data = model_examples.show_all_entries()
                
                return(data)
                '''
                return({'table':
                        [{"id": 0, "ptype:": "Th", "name": "Th_1",
                          "kernel": "first theorem", "kop": ""},
                         {"id": 1, "ptype:": "Def", "name": "Def_1",
                          "kernel": "first def", "kop": ""}]})
                '''
        self.ExamplesDBTableHandler = ExamplesDBTableHandler

        '''
        class SamplerDBTableHandler(ExamplesDBTableHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_sampler
                ExamplesDBTableHandler.__init__(self, *args)

        self.SamplerDBTableHandler = SamplerDBTableHandler
        # self.SamplerDBExamplesTableHandler = TableHandler

        class EqsDBTableHandler(ExamplesDBTableHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_eqs
                ExamplesDBTableHandler.__init__(self, *args)

        self.EqsDBTableHandler = EqsDBTableHandler
        
        class CsDBTableHandler(ExamplesDBTableHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_cs
                ExamplesDBTableHandler.__init__(self, *args)

        self.CsDBTableHandler = CsDBTableHandler
        '''
        class ExamplesDBEditorHandler(self.BaseHandler):

            # @tornado.web.authenticated
            def post(self):
                
                # this must be overridden in ancestors:
                # model_examples = self.model_examples

                # data = self.get_argument('proposals', 'No data received')
                data_body = self.request.body
                data_json = json.loads(data_body)
           
                print("\nFROM ReplacerHandler.post")
                print("\ndata_json_recived:")
                print(data_json)
                print(type(data_json))

                # FOR data update:
                action = data_json["action"]
                _id = data_json["id"]

                if action == "save":
                    
                    tabs_ids = data_json["tabs_ids"]
                    tabs_contents = data_json["tabs_contents"]
                    # content0 = "server save content 0"
                    entry = dict(zip(tabs_ids, tabs_contents))
                    # save new code:
                    # code = data_json["code"]
                    model_examples.edit_pattern(_id, entry)

                    # take it back:
                    res = model_examples.select_fields_for_editor(_id)
                    if res.count > 1:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))
                    tabs_ids = list(res.res[0].keys())
                    tabs_contents = [res.res[0][key] for key in tabs_ids]
                    
                    # term_source = res.res[0]['code']
                    
                elif action == "load":
                    
                    content0 = "server load content 0"
                
                    res = model_examples.select_fields_for_editor(_id)
                    if res.count > 1:
                        raise(BaseException("Too many elements with"
                                            + " same keys in table"))
                    tabs_ids = list(res.res[0].keys())
                    tabs_contents = [res.res[0][key] for key in tabs_ids]
                    # term_source = res.res[0]['code']
                    
                elif action == "remove":
                    term_source = "must alredy be removed in SignaturesHandler"

                else:
                    print("no such action: %s" % (action))
                '''
                print("aveilable_terms:")
                aveilable_terms = list(sources.keys())
                print(list(sources.keys()))
                available_terms_str = " ".join(aveilable_terms)
                '''
                data = {"tabs_ids": tabs_ids,
                        "tabs_contents": tabs_contents}
                
                '''
                data = {"tabs_ids": ["server tab 0", "server tab 1"],
                        "tabs_contents": [content0,
                                          "server content 1"]}
                '''
                '''
                data = {"source": term_source,
                        "available_terms": available_terms_}
                '''
                # END FOR

                # send back new data:
                # print("\ndata_to_send:")
                # print(data)
                response = data  # {"": data_json}
                self.write(json.dumps(response))

            # @tornado.web.authenticated
            def get(self):
                # not used

                print("FROM ReplacerHandler.get")

                data = {}
                response = data  # {"": data_json}
                self.write(json.dumps(response))
                
        self.ExamplesDBEditorHandler = ExamplesDBEditorHandler
        '''
        class SamplerDBEditorHandler(ExamplesDBEditorHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_sampler
                ExamplesDBEditorHandler.__init__(self, *args)

        self.SamplerDBEditorHandler = SamplerDBEditorHandler
        # self.SamplerDBExamplesTableHandler = TableHandler

        class EqsDBEditorHandler(ExamplesDBEditorHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_eqs
                ExamplesDBEditorHandler.__init__(self, *args)

        self.EqsDBEditorHandler = EqsDBEditorHandler
        
        class CsDBEditorHandler(ExamplesDBEditorHandler):
            def __init__(self, *args):
                self.model_examples = model_examples_cs
                ExamplesDBEditorHandler.__init__(self, *args)

        self.CsDBEditorHandler = CsDBEditorHandler
        '''

        class LexTut0Handler(self.BaseHandler):
            # @tornado.web.authenticated
            def get(self):
                print("FROM LexTut0Handler.get")
                print("self.current_user")
                print(self.current_user)
                # try:
                #     name = tornado.escape.xhtml_escape(self.current_user)
                #     self.render("index_net.html", title="", username=name)
                # except TypeError:
                print("self.current_user is None")
                # TODO: users methods
                self.render("index_tut_replacer.htm", username="default",
                            var="{{var}}", int="{{int}}",
                            base_dep_vars="{{base_dep_vars}}", arg_time="{{arg_time}}")
                # self.redirect("/login")

        self.LexTut0Handler = LexTut0Handler
        
