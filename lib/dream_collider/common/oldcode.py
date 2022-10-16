
    class ObjectVarDecl(object):
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