
class Evaluate(object):
    class Op(object):
        class LessThan(object):
            def eval(self, scope):
                self.eval_leaves(scope)
                if self.ev_results[0] is float and self.ev_results[1] is float:
                    return self.ev_results[0] < self.ev_results[1]
                raise RunException()