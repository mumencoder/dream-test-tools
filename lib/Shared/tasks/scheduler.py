
import asyncio
import time

import Shared

class Scheduler(object):
    @staticmethod
    def init(env):
        env.attr.scheduler.runnables = set()
        env.attr.scheduler.pending = set()

    @staticmethod
    def deinit(env):
        for runnable in env.attr.scheduler.runnables:
            runnable.cleanup()

    @staticmethod
    def create_flow(env, runnable):
        pass

    @staticmethod 
    def schedule(env, runnable):
        scheduler = env.prefix('.scheduler')

        if runnable.started():
            raise Exception("runnable already started", runnable.name)
        if runnable in scheduler.runnables:
            raise Exception("runnable is already scheduled", runnable)

        runnable.start()
        scheduler.runnables.add( runnable )

    @staticmethod
    async def run(env):
        scheduler = env.prefix('.scheduler')

        scheduler.running = True
        running = True

        while running:
            awaitables = []
            for runnable in scheduler.runnables:
                for awaitable in runnable.get_awaitables():
                    awaitables.append( awaitable )
            try:
                for awaitable in asyncio.as_completed( awaitables, timeout=1.0 ):
                    await awaitable
            except asyncio.TimeoutError:
                pass

            for pending in scheduler.pending:
                scheduler.runnables.add( pending )
            scheduler.pending = set()

            running = False
            new_runnables = set()
            for runnable in scheduler.runnables:
                if not runnable.finished():
                    new_runnables.add(runnable)
            for runnable in new_runnables:
                if runnable.background is False:
                    running = True

            scheduler.runnables = new_runnables

        scheduler.running = False
        finished = False
        while not finished:
            finished = True
            for runnable in scheduler.runnables:
                if runnable.finished() is False:
                    finished = False
            await asyncio.sleep(0.2)

        print("normal exit")