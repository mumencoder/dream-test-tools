
import time

class Scheduler(object):
    @staticmethod
    def hourly(env):
        schedule = env.prefix('.schedule')
        state = schedule.state.get(schedule.event_name, None)
        if state is None:
            state = {"update_time":0}
            schedule.state[schedule.event_name] = state
        if time.time() - state['update_time'] > 60*60:
            return True
        else:
            return False

    def update(env):
        state = env.attr.schedule.state[env.attr.schedule.event_name]
        state['update_time'] = time.time()
