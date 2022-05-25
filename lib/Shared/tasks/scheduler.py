
import asyncio
import time

import Shared

class Scheduler(object):
    @staticmethod
    def init(env):
        env.attr.scheduler.runnables = set()

    @staticmethod
    def deinit(env):
        for runnable in env.attr.scheduler.runnables:
            runnable.cleanup()

    @staticmethod
    def create_flow(env, runnable):
        pass

    @staticmethod 
    async def schedule(env, runnable):
        scheduler = env.prefix('.scheduler')

        if runnable in scheduler.runnables:
            raise Exception("runnable is already scheduled", runnable)

        scheduler.runnables.add( runnable )

    @staticmethod
    async def run(env):
        scheduler = env.prefix('.scheduler')
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
            for runnable in scheduler.runnables:
                runnable.refresh()
            running = False
            for runnable in scheduler.runnables:
                if not runnable.finished() and runnable.background is False:
                    running = True
