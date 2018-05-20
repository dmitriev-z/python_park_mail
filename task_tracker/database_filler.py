import sqlite3
import random

NUMBER_OF_WORKERS = 20


class DatabaseFiller:
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
        with open("last_names.txt", "r") as r:
            for line in r.readlines():
                last_names.append(line.strip())
        return last_names

    def _clean_up(self):
        self._cursor.execute("""DROP TABLE IF EXISTS tasks;""")
        self._cursor.execute("""DROP TABLE IF EXISTS workers;""")
        self._cursor.execute("""DROP TABLE IF EXISTS nested_tasks;""")
        self._cursor.execute("""DROP TABLE IF EXISTS worker_tasks;""")

    def _create_tasks_table(self):
        tasks = """
            CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name VARCHAR(255),
            status VARCHAR(11),
            worker VARCHAR(32),
            parent_task VARCHAR(32));
            """
        self._cursor.execute(tasks)

    def _create_workers_table(self):
        workers = """
            CREATE TABLE workers(worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(255),
            last_name VARCHAR(255));
            """
        self._cursor.execute(workers)

    def fill_tasks_table(self):
        tasks = [{"name": "clean", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "clean bedroom", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "clean bathroom", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "clean kitchen", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "cook cake", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "cook", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "cook dinner", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "cook soup", "status": "in queue", "worker": "", "parent_task": ""},
                 {"name": "cook meat", "status": "in queue", "worker": "", "parent_task": ""}]
        sql_query = """INSERT INTO tasks (task_name, status, worker, parent_task) VALUES """
        for task in tasks:
            task_name, status, worker, parent_task = task.values()
            values = """("{}", "{}", "{}", "{}")""".format(task_name, status, worker, parent_task)
            sql_query = sql_query + values + ", "
        sql_query = sql_query.rstrip(", ")
        sql_query += ";"
        self._cursor.execute(sql_query)

    def fill_workers_table(self):
        sql_query = """INSERT INTO workers (first_name, last_name) VALUES """
        for _ in range(self._number_of_workers):
            first_name = random.choice(random.choice(self._names))
            last_name = random.choice(self._last_names)
            values = """("{}", "{}")""".format(first_name, last_name)
            sql_query = sql_query + values + ", "
        sql_query = sql_query.rstrip(", ")
        sql_query += ";"
        self._cursor.execute(sql_query)


base = DatabaseFiller()
base.fill_tasks_table()
base.fill_workers_table()
