import sqlite3
import random
import string

NUMBER_OF_WORKERS = 20


class DatabaseFiller():
    def __init__(self):
        self._connection = sqlite3.connect("task_tracker.db")
        self._cursor = self._connection.cursor()
        self._clean_up()
        self._create_tasks_table()
        self._create_workers_table()
        self._number_of_workers = NUMBER_OF_WORKERS
        self._names = self._load_names()
        self._last_names = self._load_last_names()

    def __del__(self):
        self._connection.commit()
        self._connection.close()

    @property
    def cursor(self):
        return self._cursor

    @staticmethod
    def _load_names():
        male_names = []
        with open("male_first_names.txt", "r") as r:
            for line in r.readlines():
                male_names.append(line.strip())
        female_names = []
        with open("female_first_names.txt", "r") as r:
            for line in r.readlines():
                female_names.append(line.strip())
        return [male_names, female_names]

    @staticmethod
    def _load_last_names():
        last_names = []
        with open("last_names.txt", 'r') as r:
            for line in r.readlines():
                last_names.append(line.strip())
        return last_names

    @staticmethod
    def _create_id():
        return ''.join(random.choices(list(string.ascii_letters + string.digits), k=32))

    def _clean_up(self):
        self._cursor.execute("""DROP TABLE IF EXISTS tasks;""")
        self._cursor.execute("""DROP TABLE IF EXISTS workers;""")
        self._cursor.execute("""DROP TABLE IF EXISTS nested_tasks;""")
        self._cursor.execute("""DROP TABLE IF EXISTS worker_tasks;""")

    def _create_tasks_table(self):
        tasks = """
            CREATE TABLE tasks(task_id VARCHAR(32) NOT NULL PRIMARY KEY,
            task_name VARCHAR(255),
            status VARCHAR(11),
            worker VARCHAR(32),
            parent_task VARCHAR(32));
            """
        self._cursor.execute(tasks)

    def _create_workers_table(self):
        workers = """
            CREATE TABLE workers(worker_id VARCHAR(32) NOT NULL PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255));
            """
        self._cursor.execute(workers)

    def fill_tasks_table(self):
        tasks = [{'id': self._create_id(), 'name': 'clean', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'clean bedroom', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'clean bathroom', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'clean kitchen', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'cook cake', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'cook', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'cook dinner', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'cook soup', 'status': 'in queue', 'worker': '', 'parent_task': ''},
                 {'id': self._create_id(), 'name': 'cook meat', 'status': 'in queue', 'worker': '', 'parent_task': ''}]
        for task in tasks:
            task_id, task_name, status, worker, parent_task = task.values()
            sql_command = """INSERT INTO tasks VALUES('{}', '{}', '{}', '{}', '{}');"""\
                .format(task_id, task_name, status, worker, parent_task)
            self._cursor.execute(sql_command)

    def fill_workers_table(self):
        for _ in range(self._number_of_workers):
            worker_id = self._create_id()
            first_name = random.choice(random.choice(self._names))
            last_name = random.choice(self._last_names)
            sql_command = """INSERT INTO workers VALUES('{}', '{}', '{}');"""\
                .format(worker_id, first_name, last_name)
            self._cursor.execute(sql_command)


base = DatabaseFiller()
base.fill_tasks_table()
base.fill_workers_table()
