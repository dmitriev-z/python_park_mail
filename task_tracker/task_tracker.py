import sqlite3
import random
import string


class TaskTracker:
    def __init__(self):
        self._connection = sqlite3.connect("task_tracker.db")
        self._cursor = self._connection.cursor()

    def __del__(self):
        self._connection.commit()
        self._connection.close()

    @staticmethod
    def _create_id():
        return ''.join(random.choices(list(string.ascii_letters + string.digits), k=32))

    def view_all_tasks(self):
        select = """SELECT * FROM tasks"""
        self._cursor.execute(select)
        result = self._cursor.fetchall()
        for task in result:
            task_id, task_name, status, worker, parent_task = task
            print("Task id: {}\nTask name: {}\nStatus: {}\nWorker: {}\nParent task: {}\n"
                  .format(task_id, task_name, status, worker, parent_task))

    def view_all_workers(self):
        select = """SELECT * FROM workers"""
        self._cursor.execute(select)
        result = self._cursor.fetchall()
        for worker in result:
            worker_id, first_name, last_name = worker
            print("Worker id: {}\nFirst name: {}\nLast name: {}\n".
                  format(worker_id, first_name, last_name))

    def add_new_task(self, task_name:str):
        task_id = self._create_id()
        sql_command = """INSERT INTO tasks VALUES('{}', '{}', '{}', '', '');""" \
            .format(task_id, task_name, 'in queue')
        self._cursor.execute(sql_command)
        print("New task created!\nTask id: {}\nTask name: {}\n".format(task_id, task_name))

    def add_new_worker(self, first_name:str, last_name:str):
        worker_id = self._create_id()
        sql_command = """INSERT INTO workers VALUES('{}', '{}', '{}');""" \
            .format(worker_id, first_name, last_name)
        self._cursor.execute(sql_command)
        print("New worker created!\nWorker id: {}\nWorker first name: {}\nWorker last name: {}\n"
              .format(worker_id, first_name, last_name))

    def take_task_to_work(self, task_id, worker_id):
        sql_command = """SELECT * FROM tasks WHERE task_id == '{}';""".format(task_id)
        self._cursor.execute(sql_command)
        result = self._cursor.fetchall()[0]
        task_id, task_name, status, worker, parent_task = result
        if status == 'in queue':
            sql_command = """UPDATE tasks SET worker = '{}', status = '{}' WHERE task_id == '{}';""" \
                .format(worker_id, 'in progress', task_id)
            self._cursor.execute(sql_command)
            print("Task with id '{}' now marked as 'in progress' by worker with id '{}'".format(task_id, worker_id))
            self._operate_nested_tasks(task_id, worker_id, to_work=True)
        else:
            print("Task with id '{}' already 'in progress' by worker with id '{}'".format(task_id, worker))

    def finish_task(self, task_id):
        sql_command = """SELECT * FROM tasks WHERE task_id == '{}';""".format(task_id)
        self._cursor.execute(sql_command)
        result = self._cursor.fetchall()[0]
        task_id, task_name, status, worker, parent_task = result
        if status == 'in progress':
            sql_command = """UPDATE tasks SET status = 'done' WHERE task_id == '{}';""".format(task_id)
            self._cursor.execute(sql_command)
            print("Task with id '{}' now marked as 'done'".format(task_id))
            self._operate_nested_tasks(task_id, finish=True)
        elif status == 'in queue':
            print("Cant finish task which is not in progress")
        elif status == 'done':
            print("Task is already finished")

    def _operate_nested_tasks(self, parent_task_id, worker_id=None, to_work=False, finish=False):
        sql_command = """SELECT * FROM tasks WHERE parent_task == '{}';""".format(parent_task_id)
        self._cursor.execute(sql_command)
        results = self._cursor.fetchall()
        if not results:
            return
        for result in results:
            child_task_id, task_name, status, worker, parent_task = result
            if to_work:
                self.take_task_to_work(child_task_id, worker_id)
            elif finish:
                self.finish_task(child_task_id)

    def get_task_status(self, task_id):
        sql_command = """SELECT * FROM tasks WHERE task_id == '{}';""".format(task_id)
        self._cursor.execute(sql_command)
        result = self._cursor.fetchall()[0]
        task_id, task_name, status, worker, parent_task = result
        print("Task with id '{}' is '{}'".format(task_id, status))

    def make_task_nested(self, child_task, parent_task):
        sql_command = """SELECT * FROM tasks WHERE task_id == '{}';""".format(child_task)
        self._cursor.execute(sql_command)
        result = self._cursor.fetchall()[0]
        task_id, task_name, status, worker, current_parent_task = result
        if current_parent_task == '':
            sql_command = """UPDATE tasks SET parent_task = '{}' WHERE task_id == '{}';"""\
                .format(parent_task, child_task)
            self._cursor.execute(sql_command)
            print("Task with id '{}' now nested to task with id '{}'".format(child_task, parent_task))
        elif current_parent_task != parent_task:
            print("Task with id '{}' is nested to another task with id '{}'".format(child_task, current_parent_task))
        elif current_parent_task == parent_task:
            print("Task with id '{}' already nested to task with id '{}'".format(child_task, parent_task))
