"""
Unit test cases for copyspecial.py
Students should not need to modify this file.
"""

__author__ = "madarp"

import sys
import re
import os
import unittest
import importlib
import inspect
import tempfile
import random
import string
import shutil
import zipfile

PKG_NAME = 'copyspecial'  # devs: change this to soln.copyspecial to test solution


class TestCopyspecial(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # check for python3
        cls.assertGreaterEqual(cls, sys.version_info[0], 3)
        cls.module = importlib.import_module(PKG_NAME)
        # a dictionary of the functions in the module
        cls.funcs = {k: v for k, v in inspect.getmembers(cls.module, inspect.isfunction)}
        # check for required functions
        assert "get_special_paths" in cls.funcs, "Missing the get_special_paths() function"
        assert "zip_to" in cls.funcs, "Missing the zip_to() function"
        assert "copy_to" in cls.funcs, "Missing the copy_to() function"

    def random_string(self, size=10):
        return "".join(random.sample(string.ascii_lowercase, size))

    def test_get_special_paths(self):
        """Checking for list of absolute special paths"""
        abs_path_list = self.module.get_special_paths(".")
        self.assertIsInstance(
            abs_path_list, list, 
            "get_special_paths is not returning a list"
            )
        # should not return an empty list
        self.assertNotEqual(len(abs_path_list), 0)
        for p in abs_path_list:
            # is it a 'special' path?
            self.assertIsNotNone(re.search(r'__(\w+)__', p))
            # is it an 'absolute path?
            self.assertTrue(os.path.isabs(p))

    def test_no_hardcoded_paths(self):
        """Checking against hard-coded path names"""
        with tempfile.TemporaryDirectory() as dirname:
            # temp dir and its files will be auto-deleted
            filenames = []
            filenames.append("__" + self.random_string() + "__")
            filenames.append(self.random_string() + "__")
            filenames.append("__" + self.random_string())
            filenames.append(filenames[2] + "__" + filenames[1])

            # 'touch' each file
            for f in filenames:
                full_path = os.path.join(dirname, f)
                open(full_path, "w").close()

            abs_path_list = self.module.get_special_paths(dirname)
            self.assertIsInstance(
                abs_path_list, list, 
                "get_special_paths is not returning a list"
                )
            self.assertEqual(len(abs_path_list), 2)
            for p in abs_path_list:
                # is it a 'special' path?
                self.assertIsNotNone(re.search(r'__(\w+)__', p))
                # is it an 'absolute path?
                self.assertTrue(os.path.isabs(p))

    def test_copy_to(self):
        """Checking the copy_to function"""
        # Their function should use os.makedirs() to create destination
        # directory if it does not yet exist.
        with tempfile.TemporaryDirectory(prefix='kenzie-') as src_dir:
            # create some random binary files in src_dir
            file_count = range(random.randint(3, 18))
            src_files = [self.random_string() for _ in file_count]
            for f in src_files:
                with open(os.path.join(src_dir, f), 'wb') as fout:
                    fout.write(os.urandom(1024))

            # call the test module's copy_to() function
            dest_dir = "/tmp/kenzie-" + self.random_string() + "/copyspecial"
            src_list = [os.path.join(src_dir, f) for f in src_files]
            self.module.copy_to(src_list, dest_dir)

            # check if dest_dir was created and all files got copied
            dest_files = os.listdir(dest_dir)
            self.assertEqual(sorted(dest_files), sorted(src_files))

            # cleanup destination folder
            shutil.rmtree(dest_dir, ignore_errors=True)

    def test_zip_to_1(self):
        """Checking whether special files get zipped"""
        with tempfile.TemporaryDirectory(prefix='kenzie-') as src_dir:
            # create some random binary files in src_dir
            file_count = range(random.randint(3, 18))
            src_files = [self.random_string() for _ in file_count]
            for f in src_files:
                with open(os.path.join(src_dir, f), 'wb') as fout:
                    fout.write(os.urandom(1024))
            src_list = [os.path.join(src_dir, f) for f in src_files]

            zip_name = "kenzie-copyspecial-ziptest.zip"
            if os.path.exists(zip_name):
                os.remove(zip_name)
            self.module.zip_to(src_list, zip_name)
            assert os.path.exists(zip_name), "The zipfile was not created."
            # open zipfile and verify
            with zipfile.ZipFile(zip_name) as z:
                dest_files = list(z.NameToInfo.keys())
            self.assertEqual(
                sorted(dest_files), sorted(src_files),
                "original files are not being zipped"
                )

    def test_doc_strings(self):
        """Checking for docstrings on all functions"""
        self.assertTrue(self.funcs, "Module functions are missing")
        for func_name, func in self.funcs.items():
            self.assertIsNotNone(
                func.__doc__,
                f'function "{func_name}" is missing a docstring'
                )
            # arbitrary length test of at least 10 chars
            self.assertGreaterEqual(
                len(func.__doc__), 10,
                "How about a bit more docstring?"
                )


if __name__ == '__main__':
    unittest.main()
