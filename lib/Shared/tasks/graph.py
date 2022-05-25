
import collections

import Shared

class DirectedGraph(object):
    def __init__(self):
        self.forward_links = collections.defaultdict(list)
        self.back_links = collections.defaultdict(list)
        self.sorted_nodes = collections.defaultdict(list)
        self.orders = {}

    def assign_order(self, node, order):
        if node in self.orders:
            raise Exception("node already assigned to graph")
        else:
            self.orders[node] = order
            self.sorted_nodes[order].append( node )

    def add_root(self, root):
        self.assign_order(root, 1)

    def forward_nodes(self, node):
        for fnode in self.forward_links[node]:
            yield fnode
            yield from self.forward_nodes(fnode)

    def link(self, before, after):
        if before not in self.orders:
            raise Exception("before node not assigned to graph")

        if after not in self.orders:
            self.assign_order(after, self.orders[before]+1)

        if self.orders[after] <= self.orders[before]:
            raise Exception("cycle detected")

        self.forward_links[before].append( after )
        self.back_links[after].append( before )

    def stringify(self):
        s = ""
        for before, afters in self.forward_links.items():
            s += f"{before} -> {' '.join([str(after) for after in afters])}\n"
        return s

class TaskGraph(object):
    def __init__(self, name, creation_env, root_task):
        if name in creation_env.attr.task_names:
            raise Exception("non unique TaskGraph name", name)
        creation_env.attr.task_names.add(name)
        self.name = name
        self.started = False
        self.background = False

        self.creation_env = creation_env
        self.senv = None

        self.deps_dag = creation_env.attr.deps_dag

        self.root_task = root_task

        self.active_tasks = set()
        self.finished_tasks = set()

        self.dag = DirectedGraph()
        self.dag.add_root(self.root_task)

        self.exports = {}

    def __str__(self):
        return f"TaskGraph:{self.name}"

    def initialize(self, senv):
        self.senv = senv
        self.senv.attr.tg = self
        self.root_task.initialize(senv.branch())

    def start(self):
        print("start", self.name)
        self.active_tasks.add( self.root_task )
        self.root_task.start()
        self.started = True

    def cleanup(self):
        pass

    def refresh(self):
        if not self.started:
            for dep in self.deps_dag.back_links[self]:
                if not dep.finished():
                    return
            self.start()
        for task in list(self.active_tasks):
            task.refresh()
            if task.finished():
                self.active_tasks.remove(task)
                self.finished_tasks.add(task)
                self.activate_next_tasks(task)

    def all_tasks(self):
        return [self.root_task] + list(self.dag.forward_nodes(self.root_task))

    def finished(self):
        for task in self.all_tasks():
            if not task.finished():
                if len(self.active_tasks) == 0 and self.started is True:
                    raise Exception(self.name, "unfinished TaskGraph with no active tasks")
                return False
        return True

    def get_awaitables(self):
        awaitables = []
        for task in self.active_tasks:
            for awaitable in task.get_awaitables():
                awaitables.append( awaitable )
        return awaitables

    def activate_next_tasks(self, root_task):
        for task in self.dag.forward_links[root_task]:
            if not task.finished():
                self.active_tasks.add(task)
                if "senv" in self.exports:
                    print("YA!!!!!!!!!!!!!!!!!!!!!!")
                    senv = self.exports["senv"]
                else:
                    senv = root_task.senv
                task.initialize(senv.branch())

    def link(self, before, after):
        self.dag.link(before, after)

    def export(self, key, value):
        self.exports[key] = value

    class Build(object): 
        @staticmethod
        def open(env, task_graph, log=None):
            if type(task_graph) is Shared.Task:
                task_graph = Shared.TaskGraph( task_graph )

            env.attr.tg_builder.task_graph = task_graph

        def link(env, before, after):
            env.attr.tg_builder.task_graph.link( before, after )