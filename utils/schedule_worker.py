from datetime import datetime
from database.repositories import find_task_definition_by_id, find_next_scheduled_task
from multiprocessing import Process
from schemas.task import Task
from functools import lru_cache
import time
from signal import signal
import threading


def invoke_task(tid: int):
    task_def = find_task_definition_by_id(tid)
    # maybe there are better ways, but who the fuck knows!
    print("task def is", task_def)
    exec(task_def)


class ScheduleWorker(threading.Thread):
    next_wake_up_time: datetime = datetime.max
    next_scheduled_task_id = -1

    def __init__(self):
        super().__init__(daemon=True)
        # flag to pause thread
        self.paused = False
        # Explicitly using Lock over RLock since the use of self.paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self.pause_cond = threading.Condition(threading.Lock())

    @staticmethod
    def get_time_diff_from_now_in_seconds(t: datetime):
        td = t - datetime.now()
        return td.total_seconds()

    @staticmethod
    def start_task(task_id: int):
        p = threading.Thread(target=invoke_task, args=(task_id,), daemon=True)
        p.start()

    def pause(self):
        self.paused = True
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self.pause_cond.acquire()

    # should just resume the thread
    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()

    def run(self) -> None:
        t_next = find_next_scheduled_task()
        if t_next is None:
            self.next_scheduled_task_id = -1
            self.next_wake_up_time = datetime.max
        else:
            self.next_wake_up_time = t_next.execution_time
            self.next_scheduled_task_id = t_next.id
        while True:
            try:
                s = self.get_time_diff_from_now_in_seconds(self.next_wake_up_time)
                time.sleep(s)
                print("after sleep")
                ScheduleWorker.start_task(self.next_scheduled_task_id)
                t_next = find_next_scheduled_task()
                if t_next is None:
                    self.next_scheduled_task_id = -1
                    self.next_wake_up_time = datetime.max
                else:
                    self.next_wake_up_time = t_next.execution_time
                    self.next_scheduled_task_id = t_next.id
            except InterruptedError as ie:
                print("inside interrupt error")


@lru_cache
def get_scheduler():
    return ScheduleWorker()


def decide_next_move(task: Task):
    sw = get_scheduler()
    if task.execution_time < datetime.now():
        return
    elif (task.execution_time - datetime.now()).total_seconds() < 1:
        # execute immediately
        ScheduleWorker.start_task(task.id)
        return
    elif task.execution_time < sw.next_wake_up_time:
        # recompute sleep time
        return
    else:
        # do nothing, it's turn will come later
        return
