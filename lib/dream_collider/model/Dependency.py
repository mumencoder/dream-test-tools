
class Dependency(object):
    class Toplevel(object):
        def check_usage_cycle(self, define_user, define_usee):
            print(define_user, define_usee)
            if define_user.get_storage_id() == define_usee.get_storage_id(): 
                return True

            checking = set([define_usee.get_storage_id()])
            checked = set()

            while len(checking) > 0:
                for defn in checking:
                    if defn not in checked:
                        next_check = defn
                        break
                if define_user.get_storage_id() == next_check:
                    return True

                for defn in self.decl_deps[next_check]:
                    if defn in checked:
                        continue
                    checking.add(defn)
                checked.add(next_check)
                checking.remove(next_check)
            return False

        def add_dependency(self, define_user, define_usee):
            self.decl_deps[define_user.get_storage_id()].add( define_usee.get_storage_id() )
