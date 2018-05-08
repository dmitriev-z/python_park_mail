import os
import sys
import socket
import json
import random
import string
import re
import signal

from collections import OrderedDict
from datetime import datetime


class ReceiveTimeOut(Exception):
    pass


class Server:

    def __init__(self, port=8080):
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()

    def run(self):
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection.bind(('0.0.0.0', self.port))
        self.connection.listen(10)
        self._main()

    def _main(self):
        while True:
            current_connection, address = self.connection.accept()
            connection = OperateConnection(current_connection)
            connection.operate_connection()


class OperateConnection:

    def __init__(self, connection):
        self.current_connection = connection
        self.TIMEOUT = 60
        self.BUFFSIZE = 4
        self.commands = Commands()

    @staticmethod
    def _handler(signum, frame):
        raise ReceiveTimeOut()

    def _receive_data(self):
        full_received_data = ""
        while True:
            signal.signal(signal.SIGALRM, self._handler)
            if full_received_data:
                signal.setitimer(signal.ITIMER_REAL, 0.004)
            try:
                received_data = self.current_connection.recv(self.BUFFSIZE).decode()
            except (ReceiveTimeOut, socket.timeout, UnicodeDecodeError):
                break
            else:
                full_received_data += received_data
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        return full_received_data.rstrip('\n').strip()

    def operate_connection(self):
        self.commands.check_tasks_in_work()
        self.current_connection.settimeout(self.TIMEOUT)
        full_received_data = self._receive_data()
        command, data = self._parse_shell_data(full_received_data)
        if not command:
            return self.current_connection.close()
        if command == 'ADD':
            new_queue_work_id = self.commands.operate_add_command(data)
            if new_queue_work_id:
                self.current_connection.send(bytes('{}\n'.format(new_queue_work_id), 'utf8'))
            return self.current_connection.close()
        elif command == 'GET':
            received_task = self.commands.operate_get_command(data)
            if received_task:
                self.current_connection.send(bytes('{} {} {}\n'.format(received_task['id'],
                                                                       received_task['length'],
                                                                       received_task['data']), 'utf8'))
            else:
                self.current_connection.send(b'NONE\n')
            return self.current_connection.close()
        elif command == 'ACK':
            response = self.commands.operate_ack_command(data)
            if response:
                self.current_connection.send(b"OK\n")
            else:
                self.current_connection.send(b"NOT_OK\n")
            return self.current_connection.close()
        elif command == 'IN':
            response = self.commands.operate_in_command(data)
            if response:
                self.current_connection.send(b"YES\n")
            else:
                self.current_connection.send(b"NO\n")
            return self.current_connection.close()

    @staticmethod
    def _parse_shell_data(data):
        pattern = re.compile(r"^ *(?P<command>[a-zA-Z]*)? *(?P<ext_data>.*)?$")
        parsed_shell_data = pattern.match(data).groupdict()
        command = parsed_shell_data['command'].upper() if parsed_shell_data['command'] else None
        ext_data = parsed_shell_data['ext_data'].split() if parsed_shell_data['ext_data'] else None
        return command, ext_data


class Commands:

    def __init__(self):
        self.BASE, self.QUEUES, self.TASKS_IN_WORK = self._preconditions()

    @staticmethod
    def _random_string():
        return ''.join(random.choices(list(string.ascii_letters + string.digits), k=32))

    def operate_add_command(self, data):
        if not data or len(data) != 3:
            return
        queue_name, length, task_data = data
        try:
            int(length)
        except ValueError:
            return
        if int(length) > 10 ** 6 or len(task_data) != int(length):
            return
        new_queue = OrderedDict()
        new_queue_name = queue_name
        new_queue['tasks'] = []
        new_task = OrderedDict()
        new_task['id'] = self._random_string()
        new_task['length'] = length
        new_task['data'] = task_data
        new_task['state'] = 'in queue'
        queue = self.QUEUES.get(new_queue_name)
        if queue:
            queue['tasks'].append(new_task)
            self._write_data_to_base(self.BASE)
            return new_task['id']
        new_queue['tasks'].append(new_task)
        self.QUEUES[new_queue_name] = new_queue
        self._write_data_to_base(self.BASE)
        return new_task['id']

    def operate_get_command(self, data):
        if not data or len(data) != 1:
            return
        queue_name = data[0]
        queue = self.QUEUES.get(queue_name)
        if not queue:
            return
        if not queue['tasks']:
            return
        for task in queue['tasks']:
            if task['state'] == 'in progress':
                continue
            task['state'] = 'in progress'
            new_task_in_work = OrderedDict()
            new_task_in_work['queue'] = queue_name
            start_time = datetime.now()
            new_task_in_work['start_time'] = start_time.strftime("%H:%M:%S %d-%m-%Y")
            new_task_in_work.update(task)
            self.TASKS_IN_WORK.append(new_task_in_work)
            self._write_data_to_base(self.BASE)
            return task

    def operate_ack_command(self, data):
        if not data or len(data) != 2:
            return
        queue_name, task_id = data
        task_found = False
        queue = self.QUEUES.get(queue_name)
        if not queue:
            return
        for task in queue['tasks']:
            if task['id'] != task_id:
                continue
            if task['state'] == 'in progress':
                queue['tasks'].remove(task)
                task_found = True
        if not task_found:
            return
        for task in self.TASKS_IN_WORK:
            if task['queue'] == queue_name and task['id'] == task_id:
                self.TASKS_IN_WORK.remove(task)
                self._write_data_to_base(self.BASE)
                return True

    def operate_in_command(self, data):
        if not data or len(data) != 2:
            return
        queue_name, task_id = data
        queue = self.QUEUES.get(queue_name)
        if not queue:
            return
        for task in queue['tasks']:
            if task['id'] != task_id:
                continue
            return True
        return False

    @staticmethod
    def _preconditions():
        if not os.path.isfile('queue.json'):
            data = {"queues": {}, "tasks in work": []}
            with open('queue.json', 'w') as w:
                json.dump(data, w, indent='\t')
            return data, data["queues"], data["tasks in work"]
        else:
            with open('queue.json', 'r') as r:
                data = OrderedDict(json.loads(r.read()))
            return data, data["queues"], data["tasks in work"]

    @staticmethod
    def _write_data_to_base(data):
        with open('queue.json', 'w') as j:
            json.dump(data, j, indent='\t')

    def check_tasks_in_work(self):
        current_time = datetime.now()
        if not self.TASKS_IN_WORK:
            return
        uncompleted_tasks = []
        for task_in_work in self.TASKS_IN_WORK:
            task_start_time = datetime.strptime(task_in_work['start_time'], "%H:%M:%S %d-%m-%Y")
            time_delta = current_time - task_start_time
            if time_delta.seconds >= 5 * 60:
                uncompleted_tasks.append(task_in_work)
                self.TASKS_IN_WORK.remove(task_in_work)
        for uncompleted_task in uncompleted_tasks:
            queue = self.QUEUES.get(uncompleted_task['queue'])
            if not queue:
                continue
            for task in queue['tasks']:
                if task['id'] != uncompleted_task['id']:
                    continue
                task['state'] = 'in queue'
                self._write_data_to_base(self.BASE)


if __name__ == "__main__":
    try:
        server = Server(int(sys.argv[1]))
        server.run()
    except (IndexError, ValueError):
        server = Server()
        server.run()
