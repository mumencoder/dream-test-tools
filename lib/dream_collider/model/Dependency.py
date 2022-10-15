
    # dependency analysis
    def dep_cycle_check(self, v1, v2):
        if v1 == v2: 
            return True

        checking_vars = set([v2])
        checked_vars = set()

        while len(checking_vars) > 0:
            for v in checking_vars:
                if v not in checked_vars:
                    next_var = v
                    break
            if v1 in self.decl_deps:
                return True
            for v in self.decl_deps[next_var]:
                if v in checked_vars:
                    continue
                checking_vars.add(v)
            checked_vars.add(next_var)
            checking_vars.remove(next_var)
        return False

    def add_dep(self, v1, v2):
        self.decl_deps[v1].add( v2 )

    def dep_id(self, decl):
        return f"{typeof(decl)}-{decl.path}-{decl.name}"