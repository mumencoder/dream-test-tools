
    class ObjectVarDecl(object):
        def initialization_mode(self, config):
            dmobj = config['model'].ensure_object(self.path)

            for o in dmobj.parent_chain(include_self=False):
                if self.name in o.scope.vars:
                    override_decl = o.scope.vars[self.name]
                    return override_decl.initialization_mode(config)

            if "const" in self.flags:
                return "const"

            if str(self.path) == "/":
                return "dynamic"
            elif "static" in self.flags:
                return "dynamic"
            else:
                return "const"

    def compute_overrides(self):
        known_vars = {}
        known_procs = {}
        for decl in self.vars:
            decl.is_override = False
        for decl in self.procs:
            if decl.name in known_procs:
                decl.is_override = True
            else:
                decl.is_override = False 
            known_procs[decl.name] = decl

        for path, dmobj in self.objects_by_path.items():
            if dmobj.obj_trunk is None:
                dmobj.compute_overrides()