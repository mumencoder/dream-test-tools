
import asyncio 
import time, os
import traceback
import inspect
import collections

import Shared

class Task(object):
    def __init__(self, penv, fn, ptags={}, stags={}, process_tags=None, background=False, unique=True):
        self.parent_task = None
        self.manual_finish = None
        self.halted = False

        self.name = None
        self.private_tags = dict(ptags)
        self.public_tags = dict(stags)
        self.process_tags = process_tags

        self.guarded_resources = []
        self.unguarded_resources = []

        self.background = background
        self.unique = unique

        self.set_fn( fn )
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
        return str(self.name)

    def set_fn(self, fn):
        if not inspect.iscoroutinefunction(fn):
            raise Exception('coroutine required')
        self.fn = fn

    def log(self, text):
        self.wf.log.append( {'type':'text', 'text':text} )

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

    def get_senv_parent(self):
        return list(self.backward_exec_links)[0]

    @staticmethod
    def link(task1, task2):
        task1 = task1.resolve_bottom()
        task2 = task2.resolve_top()

        task1.forward_exec_links.add(task2)
        task2.backward_exec_links.add(task1)

        if task1 is task2:
            raise Exception("self link")
        if len(task2.backward_senv_links) == 1:
            raise Exception(f"attempt to link multiple senvs\n{task1.task_location()}\n{task2.task_location()}\nExisting link: {list(task2.backward_senv_links)[0].task_location()}")

        task2.parent_task = task1
        task1.forward_senv_links.add(task2)
        task2.backward_senv_links.add(task1)

    @staticmethod
    def link_exec(task1, task2):
        task1 = task1.resolve_bottom()
        task2 = task2.resolve_top()

        task1.forward_exec_links.add(task2)
        task2.backward_exec_links.add(task1)

    def resolve_top(self):
        return self

    def resolve_bottom(self):
        return self

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

        self.create_tags()
        self.create_name()

    # TODO: make a link type for this behavior instead of overloading exec_link
    def merge_imports_and_tags(self, trunk):
        for env, prop in trunk.get_exports():
            self.senv.set_attr( prop, env.get_attr(prop) )
        self.public_tags.update( trunk.public_tags )

    def create_tags(self):
        self.tags = dict(self.public_tags)
        if self.process_tags is not None:
            self.tags.update( self.process_tags(self.penv, self.senv) )
        if self.parent_task is not None:
            self.tags.update(self.parent_task.public_tags)
        self.tags.update(self.private_tags)

        self.log( f"tags {self.tags}" )
        self.log( f"pubtag {self.public_tags}" )
        self.log( f"privtag {self.private_tags}" )
        if len(self.public_tags.keys() & self.private_tags.keys()) > 0:
            raise Exception("senv,cenv tag clash", self.public_tags, self.private_tags)

    def create_name(self):
        self.name = ":".join( [ f"{key}={self.tags[key]}" for key in sorted(self.tags.keys()) ] )
        if self.name == "":
            raise Exception(f"untagged task\n{self.task_location()}")
        if self.name in self.senv.attr.tasks.all_names and self.unique is True:
            msg = f"non unique Task name {self.name}\n"
            msg += f"Original {self.senv.attr.tasks.all_names[self.name].task_location()}\n"
            msg += f"New {self.task_location()}"
            raise Exception(msg)
        self.senv.attr.tasks.all_names[self.name] = self

    def start(self):
        if self.halted is True:
            self.state = "complete"
            self.finalize()
            return

        if self.name is None:
            raise Exception(f"task started without initialization\n{self.task_location()}")
        async def t():
            try:
                props = set(self.senv.unique_properties())

                self.penv.attr.self_task = self
                self.penv.attr.wf = self.wf
                self.senv.attr.wf = self.wf
                await self.fn(self.penv, self.senv)
                self.state = "complete"
            except:
                print( traceback.format_exc() )
                self.log( traceback.format_exc() )
                self.state = "exception"
                if self.halted is False:
                    self.halt()
                self.on_exception(self.penv, self.senv)
            new_props = set(self.senv.unique_properties()) 
            diff_props = props.symmetric_difference(new_props)
            self.log( f'new props: \n{diff_props}' )
            self.finalize()

        self.co = asyncio.create_task(t())
        self.state = "running"

    def finalize(self):
        for dep in self.forward_senv_links:
            if self.halted is True:
                dep.halted = True
        for dep in self.forward_exec_links:
            if self.halted is True and len( dep.backward_exec_links ) == 1:
                dep.halted = True
        for dep in self.forward_exec_links:
            dep.try_start()

    def try_start(self):
        if self.halted is True:
            self.state = "complete"
            self.finalize()
            return

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
        if self.manual_finish is None:
            return self.state in ["complete", "exception"] 
        else:
            return self.manual_finish

    def started(self):
        return self.state in ["running"]

    def cleanup(self):
        pass

    @staticmethod
    def bounded_tasks(*tasks):
        Shared.Task.chain(*tasks)
        return Shared.TaskBound(tasks[0], tasks[-1])

    def halt(self):
        self.log("halted")
        self.halted = True
        self.cleanup_resources()

    def guard_resource(self, source, resource):
        self.guarded_resources.append( (source, resource) )

    def unguard_resource(self, resource):
        self.unguarded_resources.append( resource )

    def cleanup_resources(self):
        resource_usage = collections.defaultdict(int)

        current_task = self
        while current_task is not None:
            for res in current_task.unguarded_resources:
                resource_usage[id(res)] -= 1
            for source, res in current_task.guarded_resources:
                resource_usage[id(res)] += 1
            current_task = current_task.parent_task

        current_task = self
        while current_task is not None:
            for source, res in current_task.guarded_resources:
                if resource_usage[id(res)] == 1:
                    source.release( res )
                    resource_usage[id(res)] -= 1
            current_task = current_task.parent_task

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
    def subtask_source(env, source_attr, subtask_proto, limit=0, tags={}):
        if limit == 0:
            raise Exception("limit not set")
        async def task(penv, senv):
            it = iter(senv.get_attr(source_attr))
            iter_group = Task(env, Task.empty_task_fn, ptags={'subtask_group':''}, stags=penv.attr.self_task.public_tags)
            Task.link( penv.attr.self_task.get_senv_parent(), iter_group )
            iter_group.try_start()

            penv.attr.self_task.log( f"{len(senv.get_attr(source_attr))}")
            try:
                tasks = set()
                rest_interval = 0.5
                while True:
                    while len(tasks) < limit:
                        value = next(it)
                        subtask = subtask_proto(env, value)
                        tasks.add(subtask)
                        Shared.Task.link( iter_group, subtask )
                        subtask.top.try_start()
                    await asyncio.sleep(rest_interval)
                    for task in list(tasks):
                        if task.finished():
                            tasks.remove(task)
                    penv.attr.self_task.log( f"rested {rest_interval} remaining_tasks: {len(tasks)} / {limit}" )
                    if len(tasks) > limit / 2:
                        rest_interval *= 1.2
                    if len(tasks) < limit / 2:
                        rest_interval /= 1.2
                    rest_interval = min(rest_interval, 2.0)
            except StopIteration:
                pass
            while len(tasks) > 0:
                for task in list(tasks):
                    if task.finished():
                        tasks.remove(task)
                await asyncio.sleep(1.0)
            iter_group.manual_finish = True
        return Task(env, task, ptags=tags )

    @staticmethod
    async def empty_task_fn(penv, senv):
        pass

    @staticmethod
    def group(env, group_name):
        async def pass_task(penv, senv):
            pass
        return Shared.Task(env, pass_task, ptags={'grouped_tasks':group_name} )

    @staticmethod
    def halt_on_condition(env, cond, _id):
        env = env.branch()
        async def task(penv, senv):
            if cond(penv,senv):
                penv.halted = True
        return Shared.Task(env, task, ptags={'action':f'halt_on_condition.{_id}'})

    @staticmethod 
    def set_senv(env, attr, value):
        async def task(penv, senv):
            senv.set_attr(attr, value)
        return Shared.Task(env, task, ptags={'action':'set_senv', 'attr':attr})

    @staticmethod
    def merge_into_senv(env, menv, ptags={}):
        async def task(penv, senv):
            senv.merge(menv, inplace=True)
        return Shared.Task(env, task, ptags={'action':'merge_into_senv'}, stags=tags )

    @staticmethod
    def debug_task(env, txt):
        env = env.branch()
        async def task(penv, senv):
            print(txt)
        return Shared.Task(env, task, ptags={'action':f'debug_task.{txt}'})

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
                    self.log( f'task {self.name} skipped due to run_once condition' )
            finally:
                if self.run_once_final is not None:
                    await self.run_once_final(penv, senv)

        self.run_once_final = final
        self.run_once_fn = self.fn
        self.set_fn( wrap_fn )

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
                self.log( f'task {self.name} skipped due to run_fresh condition' )

        self.run_fresh_fn = self.fn
        self.set_fn( wrap_fn )

        return self

class TaskBound(object):
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def resolve_top(self):
        return self.top.resolve_top()

    def resolve_bottom(self):
        return self.bottom.resolve_bottom()

    def finished(self):
        return self.bottom.finished()

class TaskResource(object):
    def __init__(self, attr, source):
        self.attr = attr
        self.source = source
        self.resource = None

    async def acquire(self, senv):
        while True:
            self.resource = await self.source.acquire()
            if self.resource is not None:
                break
            await asyncio.sleep(0.1)
        senv.set_attr(self.attr, self.resource)
        return self.resource

    def release(self, senv):
        self.source.release(self.resource)