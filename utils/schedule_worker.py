from datetime import datetime
from database.repositories import (
    find_task_definition_by_id,
    find_next_scheduled_task,
    invalidate_task,
)
from multiprocessing import Process
from schemas.task import Task
from functools import lru_cache
import time
from signal import signal
import threading


def invoke_task(tid: int):
    try:
        task_def = find_task_definition_by_id(tid)
        # maybe there are better ways, but who the fuck knows!
        exec(task_def)
    except Exception as e:
        print("could not find task with id", tid)


class ScheduleWorker(threading.Thread):
    maximum_sleeping_time = 7 * 86400

    next_scheduled_task_id: int
    next_wake_up_time: datetime
    ev: threading.Event
    is_interrupted: bool

    def __init__(self):
        super().__init__(daemon=True)
        self.next_wake_up_time = datetime.max
        self.next_scheduled_task_id = -1
        self.ev = threading.Event()
        self.is_interrupted = False

    @staticmethod
    def get_time_diff_from_now_in_seconds(t: datetime):
        td = t - datetime.now()
        sec = td.total_seconds()
        return (
            ScheduleWorker.maximum_sleeping_time
            if sec > ScheduleWorker.maximum_sleeping_time
            else sec
        )

    @staticmethod
    def start_task(task_id: int):
        print("start task called with id", task_id, "at", datetime.now())
        p = threading.Thread(target=invoke_task, args=(task_id,), daemon=True)
        p.start()

    def run(self) -> None:
        t_next = find_next_scheduled_task()
        if t_next is not None:
            self.next_wake_up_time = t_next.execution_time
            self.next_scheduled_task_id = t_next.id

        print("hello", self.next_wake_up_time)
        while True:
            s = self.get_time_diff_from_now_in_seconds(self.next_wake_up_time)
            print("s =", s)
            s = s if s > 0 else 0
            self.ev.clear()
            self.ev.wait(timeout=s)

            if self.is_interrupted:
                print("after interrupt")
                t_next = find_next_scheduled_task()

                if t_next is not None:
                    self.next_wake_up_time = t_next.execution_time
                    self.next_scheduled_task_id = t_next.id
                self.is_interrupted = False
            else:
                print("after sleep")
                invalidate_task(self.next_scheduled_task_id)
                ScheduleWorker.start_task(self.next_scheduled_task_id)
                t_next = find_next_scheduled_task()
                if t_next is None:
                    print("no task available")
                    self.next_wake_up_time = datetime.max
                    self.next_scheduled_task_id = -1
                else:
                    print("task available with id", t_next.id)
                    self.next_wake_up_time = t_next.execution_time
                    self.next_scheduled_task_id = t_next.id

    def interrupt(self):
        self.is_interrupted = True
        self.ev.set()


@lru_cache
def get_scheduler():
    print("getting scheduler")
    return ScheduleWorker()


def decide_next_move(task: Task):
    sw = get_scheduler()
    if task.execution_time < datetime.now():
        return
    elif (task.execution_time - datetime.now()).total_seconds() < 1:
        # execute immediately
        print("inside epsilon bound")
        ScheduleWorker.start_task(task.id)
        return
    elif task.execution_time < sw.next_wake_up_time:
        # recompute sleep time
        sw.interrupt()
        return
    else:
        # do nothing, it's turn will come later
        return
