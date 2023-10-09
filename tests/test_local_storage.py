import atexit
import os
import unittest

from loguru import logger

from local_storage import LocalStorage

NEW_LOCAL_FILENAME = 'new_local'


def clear_temp_file():  #
    print("clearing..")
    if os.path.exists(NEW_LOCAL_FILENAME):
        os.remove(NEW_LOCAL_FILENAME)


atexit.register(clear_temp_file)


class TestLocalStorage(unittest.TestCase):
    def test_1_create_new_localstorage(self):
        if os.path.exists(NEW_LOCAL_FILENAME):
            os.remove(NEW_LOCAL_FILENAME)
        _ = LocalStorage(NEW_LOCAL_FILENAME)

    def test_2_ops(self):
        if os.path.exists(NEW_LOCAL_FILENAME):
            os.remove(NEW_LOCAL_FILENAME)
        l = LocalStorage(NEW_LOCAL_FILENAME)
        l.put('1', '2')
        self.assertEqual(l.get('1'), '2')
        self.assertEqual(len(l), 1)
        self.assertIs(l.get('2'), None)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop('1'), '2')
        self.assertEqual(len(l), 0)

    def test_3_read(self):
        if os.path.exists(NEW_LOCAL_FILENAME):
            os.remove(NEW_LOCAL_FILENAME)
        l = LocalStorage(NEW_LOCAL_FILENAME)
        l.put('a', 'b')
        l.put('c', 'd')
        l.save()
        del l
        l1 = LocalStorage(NEW_LOCAL_FILENAME)
        self.assertEqual(l1.get('a'), 'b')
        self.assertEqual(l1.get('c'), 'd')

    def test_4_decrypt_fail(self):
        with open(NEW_LOCAL_FILENAME, 'wb') as f:
            f.write(b'12345' * 37)
        l = LocalStorage(NEW_LOCAL_FILENAME)
        self.assertLogs(logger, "WARNING")
