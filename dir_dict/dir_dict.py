import os
from collections import MutableMapping


class DirDict(MutableMapping):
    def __init__(self, directory):
        self._directory = directory
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def __setitem__(self, key, value):
        with open(os.path.join(self._directory, key), 'w', encoding='utf8') as f:
            f.write(value if type(value) is str else repr(value))

    def __getitem__(self, key):
        if key not in os.listdir(self._directory):
            raise KeyError(key)
        with open(os.path.join(self._directory, key), 'r', encoding='utf8') as f:
            return f.read()

    def __delitem__(self, key):
        if key not in os.listdir(self._directory):
            raise KeyError(key)
        os.remove(os.path.join(self._directory, key))

    def __iter__(self):
        return iter(os.listdir(self._directory))

    def __len__(self):
        return len(os.listdir(self._directory))
