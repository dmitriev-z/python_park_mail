import os
import shutil
import random
import string

if not os.path.exists('/tmp/async_file_storage'):
    os.makedirs('/tmp/async_file_storage')
else:
    shutil.rmtree('/tmp/async_file_storage')
j = 0
for i in range(3):
    os.makedirs('/tmp/async_file_storage/{}'.format(i))
    for _ in range(10):
        text = ""
        for __ in range(10):
            text = text + ''.join(random.choices(list(string.ascii_letters), k=42)) + "\n"
        with open('/tmp/async_file_storage/{}/{}'.format(i, j), 'w') as w:
            w.write(text)
        j += 1
