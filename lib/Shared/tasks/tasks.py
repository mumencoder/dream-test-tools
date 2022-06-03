
import asyncio 
import time, os
import traceback
import inspect

import Shared

class Task(object):
    def __init__(self, penv, fn, tags={}, background=False):
        self.name = None
        self.creation_tags = tags

        self.background = background

        self.fn = fn
        self.co = None

        self.penv = penv.branch()
        self.senv = None

        self.exports = []

        self.wf = Shared.Workflow(penv)
        self.wf.task = self
        penv.attr.workflows.append(self.wf)

        self.forward_senv_links = set()
        self.backward_senv_links = set()

        self.forward_exec_links = set()
        self.backward_exec_links = set()

        self.order = None

        self.state = "created"

        self.on_exception = lambda penv, senv: 0

        self.init_from = inspect.stack()

    def __str__(self):
        return self.name

    def view(self):
        import jaal
        import pandas as pd
        data = {"to":[], "from":[]}
        self.add_links(data)
        edge_df = pd.DataFrame(data)
        jaal.Jaal(edge_df).plot()

    def add_links(self, data):
        for node in self.forward_exec_links:
            data["from"].append( self.task_node_id() )
            data["to"].append( node.task_node_id() )
            node.add_links(data)

    @staticmethod
    def link(task1, task2):
        if isinstance(task1, TaskBound):
            task1 = task1.bottom
        if isinstance(task2, TaskBound):
            task2 = task2.top
        if isinstance(task1, TaskBound) and isinstance(task2, TaskBound):
            raise Exception("attempt to link TaskBound internally")

        task1.forward_exec_links.add(task2)
        task2.backward_exec_links.add(task1)

        if len(task2.backward_senv_links) == 1:
            raise Exception(f"attempt to link multiple senvs\n{task1.task_location()}\n{task2.task_location()}\nExisting link: {list(task2.backward_senv_links)[0].task_location()}")

        task1.forward_senv_links.add(task2)
        task2.backward_senv_links.add(task1)

    @staticmethod
    def link_exec(task1, task2):
        if isinstance(task1, TaskBound):
            task1 = task1.bottom
        if isinstance(task2, TaskBound):
            task2 = task2.top
        if isinstance(task1, TaskBound) and isinstance(task2, TaskBound):
            raise Exception("attempt to link TaskBound internally")

        task1.forward_exec_links.add(task2)
        task2.backward_exec_links.add(task1)

    def get_exports(self):
        return self.exports

    def export(self, env, prop):
        self.exports.append( (env, prop) )

    def task_node_id(self):
        f1 = os.path.basename(self.init_from[1].filename)
        f2 = os.path.basename(self.init_from[2].filename)
        return f"{id(self)},{f1}:{self.init_from[1].lineno},{f2}:{self.init_from[2].lineno}"

    def task_location(self):
        return f"{self.init_from[1].filename}:{self.init_from[1].lineno},{self.init_from[2].filename}:{self.init_from[2].lineno}"

    def initialize(self, senv):
        if self.senv is not None:
            raise Exception(f"task initialized twice\n{self.task_location()}")
        self.senv = senv.branch()
        Task.tags( self.senv, self.penv.get_dict( '.tasks.base_tags') )
        self.create_tags()
        self.create_name()

    def merge_imports_and_tags(self, trunk):
        for env, prop in trunk.get_exports():
            print("import ", self.name, prop)
            self.senv.set_attr( prop, env.get_attr(prop) )
        Task.tags( self.penv, trunk.penv.get_dict( '.tasks.base_tags') )

    def create_tags(self):
        sd = self.senv.get_dict('.tasks.base_tags')
        cd = self.creation_tags

        if len(sd.keys() & cd.keys()) > 0:
            raise Exception("senv,cenv tag clash", sd.keys() & cd.keys())

        self.tags = sd
        self.tags.update(cd)

    def create_name(self):
        self.name = ":".join( [ f"{key}={self.tags[key]}" for key in sorted(self.tags.keys()) ] )
        if self.name == "":
            raise Exception(f"untagged task\n{self.task_location()}")
        if self.name in self.senv.attr.tasks.all_names:
            msg = f"non unique Task name {self.name}\n"
            msg += f"Original {self.senv.attr.tasks.all_names[self.name].task_location()}\n"
            msg += f"New {self.task_location()}"
            raise Exception(msg)
        self.senv.attr.tasks.all_names[self.name] = self

    def start(self):
        if self.name is None:
            raise Exception(f"task started without initialization\n{self.task_location()}")
        print("start ", self.name)
        async def t():
            try:
                props = set(self.senv.unique_properties())

                self.penv.attr.self_task = self
                self.penv.attr.wf = self.wf
                self.senv.attr.wf = self.wf
                await self.fn(self.penv, self.senv)
                self.state = "complete"
            except:
                self.state = "exception"
                self.penv.attr.wf.log.append( {'type':'text', 'text':traceback.format_exc() })
                self.on_exception(self.penv, self.senv)
            new_props = set(self.senv.unique_properties()) 
            diff_props = props.symmetric_difference(new_props)
            self.penv.attr.wf.log.append( {'type':'text', 'text':f'new props: \n{diff_props}' })

            for dep in self.forward_exec_links:
                dep.try_start()

        self.co = asyncio.create_task(t())
        self.state = "running"

    def try_start(self):
        if self.co is not None:
            raise Exception("Attempt to start a task that has been started")

        for dep in self.backward_exec_links:
            if not dep.finished():
                return

        if len(self.backward_senv_links) == 0:
            pass
        elif len(self.backward_senv_links) == 1:
            trunk = list(self.backward_senv_links)[0]
            self.initialize(trunk.senv)
        else:
            raise Exception(f"attempt to link multiple senvs\n{self.task_location()}\n")

        if self.name is None:
            raise Exception(f"task started without initialization\n{self.task_location()}")

        for trunk in self.backward_exec_links:
            self.merge_imports_and_tags(trunk)
        self.penv.attr.scheduler.pending.add(self)

        self.start()

    def get_awaitables(self):
        if self.state == "running":
            return [self.co]
        else:
            return []

    def finished(self):
        return self.state in ["complete", "exception"] 

    def started(self):
        return self.state in ["running"]

    def cleanup(self):
        pass

    @staticmethod
    def tags(env, tags):
        if env.attr_exists('.tasks.base_tags', local=True):
            env.attr.tasks.base_tags.update( tags )
        else:
            env.set_attr( '.tasks.base_tags', tags)

    @staticmethod
    def chain(*tasks):
        prev_task = tasks[0]
        for next_task in tasks[1:]:
            Shared.Task.link( prev_task, next_task )
            prev_task = next_task

    @staticmethod
    def split(root_task, *tasks):
        for task in tasks:
            Shared.Task.link( root_task, task )

    @staticmethod
    def meet(env, name, linker, tasks):
        bottom = Task.task_group(env, name)
        for task in tasks:
            linker( task, bottom )
        return bottom

    @staticmethod
    def task_group(env, group_name):
        async def pass_task(penv, senv):
            pass       
        return Task(env, pass_task, tags={'grouped_tasks':group_name} )

    @staticmethod
    def add_leaf(env, task):
        Shared.Task.link( env.attr.self_task, task )

    def run_once(self, final=None):
        async def wrap_fn(penv, senv):
            scheduler = penv.prefix('.scheduler')
            state = penv.prefix('.state')
            state_key = "run_once-" + self.name
            result = state.tasks.get(state_key, None)

            if result is None:
                do_task = True
            else:
                do_task = False

            if result is not None:
                penv.attr.final_state = result["final_state"]
            else:
                penv.attr.final_state = {}

            try:
                self.penv.attr.wf = self.wf
                self.senv.attr.wf = self.wf
                if do_task:
                    await self.run_once_fn(penv, senv)
                    result = {"update_time":time.time(), "result":self.state, "final_state":penv.attr.final_state }
                    state.tasks.set( state_key, result )
                else:
                    self.wf.log.append( {'type':'text', 'text':f'task {self.name} skipped due to run_once condition' } )
            finally:
                if self.run_once_final is not None:
                    await self.run_once_final(penv, senv)

        self.run_once_final = final
        self.run_once_fn = self.fn
        self.fn = wrap_fn

        return self

    def run_fresh(self, minutes=None):
        t = minutes*60
        async def wrap_fn(penv, senv):
            scheduler = penv.prefix('.scheduler')
            state = penv.prefix('.state')
            state_key = "run_fresh-" + self.name
            result = state.tasks.get(state_key, None)

            if result is None:
                do_task = True
            elif time.time() - result['update_time'] > t:
                do_task = True
            else:
                do_task = False

            self.penv.attr.wf = self.wf
            self.senv.attr.wf = self.wf
            if do_task:
                await self.run_fresh_fn(penv, senv)
                result = {"update_time":time.time()}
                state.tasks.set(state_key, result )
            else:
                self.wf.log.append( {'type':'text', 'text':f'task {self.name} skipped due to run_fresh condition' } )

        self.run_fresh_fn = self.fn
        self.fn = wrap_fn

        return self

    # todo: finish
    def run_with_resource(self, resource=None):
        async def wrap_fn(penv, senv):
            try:
                while True:
                    r = await resource.acquire()
                    if r is not None:
                        break
                    await asyncio.sleep(0.2)
            finally:
                resource.release(r)

class TaskBound(object):
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom