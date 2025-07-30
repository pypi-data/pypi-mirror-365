import os

class SaltManager(object):
    def __init__(self, generate, path='.salt'):
        self.generate = generate
        self.path = path

    def get(self):
        if self.generate:
            return self._generate_and_store()
        return self._read()

    def _generate_and_store(self):
        salt = os.urandom(16)
        with open(self.path, 'wb') as f:
            f.write(salt)
        return salt

    def _read(self):
        with open(self.path, 'rb') as f:
            return f.read()