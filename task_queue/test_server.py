import os
import unittest
import time
import socket
import subprocess
import json

from unittest import TestCase


class ServerBaseTest(TestCase):
    def setUp(self):
        if os.path.isfile('queue.json'):
            self.save_previous_base_data()
            self.clear_data_base()
            self.restore = True
        else:
            self.restore = False
        self.host = '127.0.0.1'
        self.port = 1234
        self.server = subprocess.Popen(['python3', 'server.py', str(self.port)])
        # даем серверу время на запуск
        time.sleep(0.5)

    def tearDown(self):
        self.restore_base_data()
        self.server.terminate()
        self.server.wait()

    def save_previous_base_data(self):
        with open('queue.json', 'r') as j:
            self.previous_data = json.loads(j.read())

    def restore_base_data(self):
        if self.restore:
            with open('queue.json', 'w') as j:
                j.write(json.dumps(self.previous_data))
        else:
            self.clear_data_base()

    @staticmethod
    def clear_data_base():
        clear_data = {"queues": [], "tasks in work": []}
        with open('queue.json', 'w') as j:
            j.write(json.dumps(clear_data))

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_base_scenario(self):
        task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' 5 12345\n', self.send(b'GET 1'))
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + task_id))
        self.assertEqual(b'OK\n', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NOT_OK\n', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO\n', self.send(b'IN 1 ' + task_id))

    def test_two_tasks(self):
        first_task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        second_task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + second_task_id))

        self.assertEqual(first_task_id + b' 5 12345\n', self.send(b'GET 1'))
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES\n', self.send(b'IN 1 ' + second_task_id))
        self.assertEqual(second_task_id + b' 5 12345\n', self.send(b'GET 1'))

        self.assertEqual(b'OK\n', self.send(b'ACK 1 ' + second_task_id))
        self.assertEqual(b'NOT_OK\n', self.send(b'ACK 1 ' + second_task_id))


class ServerAddCommandTest(TestCase):
    def setUp(self):
        if os.path.isfile('queue.json'):
            self.save_previous_base_data()
            self.clear_data_base()
            self.restore = True
        else:
            self.restore = False
        self.host = '127.0.0.1'
        self.port = 1234
        self.server = subprocess.Popen(['python3', 'server.py', str(self.port)])
        # даем серверу время на запуск
        time.sleep(0.5)

    def tearDown(self):
        self.restore_base_data()
        self.server.terminate()
        self.server.wait()

    def save_previous_base_data(self):
        with open('queue.json', 'r') as j:
            self.previous_data = json.loads(j.read())

    def restore_base_data(self):
        if self.restore:
            with open('queue.json', 'w') as j:
                j.write(json.dumps(self.previous_data))
        else:
            self.clear_data_base()

    @staticmethod
    def clear_data_base():
        clear_data = {"queues": [], "tasks in work": []}
        with open('queue.json', 'w') as j:
            j.write(json.dumps(clear_data))

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_normal_command(self):
        task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)

    def test_command_with_spaces(self):
        task_id = self.send(b'    ADD     1   5      12345     ').strip(b'\n')
        self.assertTrue(task_id)

    def test_lower_command(self):
        task_id = self.send(b'add 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)

    def test_mixed_command(self):
        task_id = self.send(b'aDd 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)

    def test_command_with_incorrect_length_parameter(self):
        task_id = self.send(b'ADD 1 5.0 12345').strip(b'\n')
        self.assertFalse(task_id)

    def test_command_with_incorrect_parameters_amount(self):
        task_id = self.send(b'ADD 1 2 5 12345').strip(b'\n')
        self.assertFalse(task_id)
        task_id = self.send(b'ADD').strip(b'\n')
        self.assertFalse(task_id)
        task_id = self.send(b'ADD 1').strip(b'\n')
        self.assertFalse(task_id)
        task_id = self.send(b'ADD 1 5').strip(b'\n')
        self.assertFalse(task_id)

    def test_command_with_length_parameter_more_than_1000000(self):
        data = ''.join('0123456789' for _ in range(10 ** 5 + 1)).encode('utf8')
        command = b'ADD 1 ' + str(len(data)).encode('utf8') + b' ' + data
        task_id = self.send(command).strip(b'\n')
        self.assertFalse(task_id)

    def test_command_with_data_more_than_length(self):
        task_id = self.send(b'ADD 1 5 123456').strip(b'\n')
        self.assertFalse(task_id)

    def test_command_with_data_less_than_length(self):
        task_id = self.send(b'ADD 1 5 1234').strip(b'\n')
        self.assertFalse(task_id)


class ServerGetCommandTest(TestCase):
    def setUp(self):
        if os.path.isfile('queue.json'):
            self.save_previous_base_data()
            self.clear_data_base()
            self.restore = True
        else:
            self.restore = False
        self.host = '127.0.0.1'
        self.port = 1234
        self.server = subprocess.Popen(['python3', 'server.py', str(self.port)])
        # даем серверу время на запуск
        time.sleep(0.5)
        self.task_id = self.preconditions()

    def tearDown(self):
        self.restore_base_data()
        self.server.terminate()
        self.server.wait()

    def save_previous_base_data(self):
        with open('queue.json', 'r') as j:
            self.previous_data = json.loads(j.read())

    def restore_base_data(self):
        if self.restore:
            with open('queue.json', 'w') as j:
                j.write(json.dumps(self.previous_data))
        else:
            self.clear_data_base()

    @staticmethod
    def clear_data_base():
        clear_data = {"queues": [], "tasks in work": []}
        with open('queue.json', 'w') as j:
            j.write(json.dumps(clear_data))

    def preconditions(self):
        # create queue and task:
        task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)
        return task_id

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_command_with_incorrct_queue_name(self):
        get_result = self.send(b'GET 2').strip(b'\n')
        self.assertEqual(get_result, b'NONE')

    def test_command_with_incorrect_paramters_amount(self):
        get_result = self.send(b'GET 2 2').strip(b'\n')
        self.assertEqual(get_result, b'NONE')
        get_result = self.send(b'GET').strip(b'\n')
        self.assertEqual(get_result, b'NONE')

    def test_normal_command(self):
        get_result = self.send(b'GET 1').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

    def test_lower_command(self):
        get_result = self.send(b'get 1').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

    def test_mixed_command_with_spaces(self):
        get_result = self.send(b'     GeT   1 ').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

    def test_get_when_all_tasks_are_in_work(self):
        self.test_normal_command()
        get_result = self.send(b'GET 1').strip(b'\n')
        self.assertEqual(get_result, b'NONE')

    def test_undone_tasks_returns_to_queue_after_5_minutes(self):
        self.test_normal_command()
        time.sleep(60 * 5)
        get_result = self.send(b'GET 1').strip(b'\n')
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        get_result = self.send(b'GET 1').strip(b'\n')


class ServerAckCommandTest(TestCase):
    def setUp(self):
        if os.path.isfile('queue.json'):
            self.save_previous_base_data()
            self.clear_data_base()
            self.restore = True
        else:
            self.restore = False
        self.host = '127.0.0.1'
        self.port = 1234
        self.server = subprocess.Popen(['python3', 'server.py', str(self.port)])
        # даем серверу время на запуск
        time.sleep(0.5)
        self.task_id = self.preconditions()

    def tearDown(self):
        self.restore_base_data()
        self.server.terminate()
        self.server.wait()

    def save_previous_base_data(self):
        with open('queue.json', 'r') as j:
            self.previous_data = json.loads(j.read())

    def restore_base_data(self):
        if self.restore:
            with open('queue.json', 'w') as j:
                j.write(json.dumps(self.previous_data))
        else:
            self.clear_data_base()

    @staticmethod
    def clear_data_base():
        clear_data = {"queues": [], "tasks in work": []}
        with open('queue.json', 'w') as j:
            j.write(json.dumps(clear_data))

    def preconditions(self):
        # create queue and tasks:
        task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)

        # issue tasks in work
        get_result = self.send(b'GET 1').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

        return task_id

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_command_with_incorrect_queue_name(self):
        ack_result = self.send(b'ACK 2 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')

    def test_command_with_incorrect_task_name(self):
        ack_result = self.send(b'ACK 1 ' + self.task_id.upper()).strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')

    def test_command_with_incorrect_parameters_amount(self):
        ack_result = self.send(b'ACK 1 ' + self.task_id + b' 2').strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')
        ack_result = self.send(b'ACK').strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')
        ack_result = self.send(b'ACK 1').strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')

    def test_normal_command(self):
        ack_result = self.send(b'ACK 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'OK')

    def test_lower_command(self):
        ack_result = self.send(b'ack 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'OK')

    def test_mixed_command_with_spaces(self):
        ack_result = self.send(b'  aCk        1   ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'OK')

    def test_end_task_that_was_already_ended(self):
        self.test_normal_command()
        ack_result = self.send(b'ACK 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')

    def test_end_task_that_was_returned_to_queue_after_5_minutes(self):
        time.sleep(60 * 5)
        ack_result = self.send(b'ACK 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'NOT_OK')


class ServerInCommandTest(TestCase):
    def setUp(self):
        if os.path.isfile('queue.json'):
            self.save_previous_base_data()
            self.clear_data_base()
            self.restore = True
        else:
            self.restore = False
        self.host = '127.0.0.1'
        self.port = 1234
        self.server = subprocess.Popen(['python3', 'server.py', str(self.port)])
        # даем серверу время на запуск
        time.sleep(0.5)
        self.task_id = self.preconditions()

    def tearDown(self):
        self.restore_base_data()
        self.server.terminate()
        self.server.wait()

    def save_previous_base_data(self):
        with open('queue.json', 'r') as j:
            self.previous_data = json.loads(j.read())

    def restore_base_data(self):
        if self.restore:
            with open('queue.json', 'w') as j:
                j.write(json.dumps(self.previous_data))
        else:
            self.clear_data_base()

    @staticmethod
    def clear_data_base():
        clear_data = {"queues": [], "tasks in work": []}
        with open('queue.json', 'w') as j:
            j.write(json.dumps(clear_data))

    def preconditions(self):
        # create queue and tasks:
        task_id = self.send(b'ADD 1 5 12345').strip(b'\n')
        self.assertTrue(task_id)

        return task_id

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_command_with_incorrect_queue_name(self):
        in_result = self.send(b'IN 2 ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'NO')

    def test_command_with_incorrect_task_name(self):
        in_result = self.send(b'IN 1 ' + self.task_id.upper()).strip(b'\n')
        self.assertEqual(in_result, b'NO')

    def test_command_with_incorrect_parameters_amount(self):
        in_result = self.send(b'IN 1 ' + self.task_id + b' 2').strip(b'\n')
        self.assertEqual(in_result, b'NO')
        in_result = self.send(b'IN').strip(b'\n')
        self.assertEqual(in_result, b'NO')
        in_result = self.send(b'IN 1').strip(b'\n')
        self.assertEqual(in_result, b'NO')

    def test_normal_command(self):
        in_result = self.send(b'IN 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'YES')

    def test_lower_command(self):
        in_result = self.send(b'in 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'YES')

    def test_mixed_command_with_spaces(self):
        in_result = self.send(b'    iN     1    ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'YES')

    def test_tasks_in_work(self):
        get_result = self.send(b'GET 1').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

        in_result = self.send(b'IN 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'YES')

    def test_ended_task(self):
        get_result = self.send(b'GET 1').strip(b'\n')
        self.assertTrue(get_result)
        get_result = get_result.split()
        self.assertEqual(get_result[0], self.task_id)
        self.assertEqual(int(get_result[1]), len(get_result[2]))

        ack_result = self.send(b'ACK 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(ack_result, b'OK')

        in_result = self.send(b'IN 1 ' + self.task_id).strip(b'\n')
        self.assertEqual(in_result, b'NO')


if __name__ == '__main__':
    unittest.main()
