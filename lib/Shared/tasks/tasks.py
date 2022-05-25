
import asyncio 
import time
import traceback

import Shared

class Task(object):
    def __init__(self, penv, fn, tags={}, background=False):
        self.name = None
        self.extra_tags = tags

        self.fn = fn
        self.background = background

        self.co = None
        self.penv = penv.branch()
        self.senv = None

        Shared.Workflow.open(self.penv)
        self.penv.attr.wf.task = self

        self.deps_dag = penv.attr.deps_dag

        self.order = None

        self.state = "created"

        self.on_exception = lambda penv, senv: 0

    def __str__(self):
        return self.name

    def initialize(self, senv):
        senv.attr.wf = self.penv.attr.wf
        self.senv = senv
        self.tags = self.penv.get_dict('.tasks.base_tags')
        self.tags.update(senv.get_dict('.tasks.base_tags'))
        self.tags.update(self.extra_tags)
        self.name = "-".join( [ f"{key}-{self.tags[key]}" for key in sorted(self.tags.keys()) ] )
        if self.name in senv.attr.task_names:
            raise Exception("non unique Task name", self.name)
        senv.attr.task_names.add(self.name)

    def start(self):
        async def t():
            try:
                await self.fn(self.penv, self.senv)
                self.state = "complete"
            except:
                self.state = "exception"
                self.penv.attr.wf.log.append( {'type':'text', 'text':traceback.format_exc() })
                self.on_exception(self.penv, self.senv)
        self.co = asyncio.create_task(t())
        self.state = "running"

    def refresh(self):
        if self.co is None:
            for dep in self.deps_dag.back_links[self]:
                if not dep.finished():
                    return
            self.start()

    def get_awaitables(self):
        if self.state == "running":
            return [self.co]
        else:
            return []

    def finished(self):
        return self.state in ["complete", "exception"] 

    def cleanup(self):
        pass

    @staticmethod
    def tags(env, tags):
        if env.attr_exists('.tasks.base_tags', local=True):
            env.attr.tasks.base_tags.update( tags )
        else:
            env.attr.tasks.base_tags = tags

    @staticmethod
    def chain(tg, *tasks):
        prev_task = tasks[0]
        for task in tasks[1:]:
            tg.link( prev_task, task)
            prev_task = task

    @staticmethod
    def split(tg, root_task, *tasks):
        for task in tasks:
            tg.link( root_task, task )

    def run_once(self, final=None):
        async def wrap_fn(penv, senv):
            scheduler = penv.prefix('.scheduler')
            state_key = "run_once-" + self.name
            result = scheduler.task_state.get(state_key, None)

            if result is None:
                do_task = True
            else:
                do_task = False

            if result is not None:
                penv.attr.final_state = result["final_state"]
            else:
                penv.attr.final_state = {}

            try:
                if do_task:
                    await self.run_once_fn(penv, senv)
                    result = {"update_time":time.time(), "result":self.state, "final_state":penv.attr.final_state }
                    scheduler.task_state.set( state_key, result )
                else:
                    penv.attr.wf.log.append( {'type':'text', 'text':'task skipped due to run_once condition' } )
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
            state_key = "run_fresh-" + self.name
            result = scheduler.task_state.get(state_key, None)

            if result is None:
                do_task = True
            elif time.time() - result['update_time'] > t:
                do_task = True
            else:
                do_task = False

            if do_task:
                await self.run_fresh_fn(penv, senv)
                result = {"update_time":time.time()}
                scheduler.task_state.set(state_key, result )
            else:
                penv.attr.wf.log.append( {'type':'text', 'text':'task skipped due to run_fresh condition' } )

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
