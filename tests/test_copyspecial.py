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
from io import StringIO

# devs: change this to soln.copyspecial to test solution
PKG_NAME = 'copyspecial'
SPL_REGEX = re.compile(r'__(\w+)__')


class Capturing(list):
    """Context Mgr helper for capturing stdout from a function call"""
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class RandomFileSet:
    """Creates a set of special/notspecial files in a random temp dir"""
    def __init__(self):
        self.tmp_dir, self.file_list = self.random_fileset()
        self.abs_file_list = [
            os.path.abspath(os.path.join(self.tmp_dir, f))
            for f in self.file_list
        ]
        self.spl_file_list = list(filter(SPL_REGEX.search, self.abs_file_list))

    def __del__(self):
        """Clean up our own dir"""
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def random_filename(self):
        """helper method to generate a random special/notspecial filename"""
        prefix = random.choice(("", "_", "__", "___"))
        suffix = random.choice(("", "_", "__", "___"))
        size = random.randint(1, 21)
        filename = (
            prefix
            + "".join(random.sample(string.ascii_lowercase, size))
            + suffix
            )
        return filename

    def random_fileset(self):
        """helper to create a set of mixed files in a temp folder"""
        tmp_dir = tempfile.mkdtemp(prefix='kenzie-copyspec-')
        # guarantee at least one
        file_list = ['__example_special_file__']
        open(os.path.join(tmp_dir, file_list[0]), 'w').close()
        for _ in range(random.randint(43, 314)):  # arbitrary
            filename = self.random_filename()
            open(os.path.join(tmp_dir, filename), 'w').close()
            file_list.append(filename)
        return tmp_dir, file_list


class TestCopyspecial(unittest.TestCase):
    """Main test fixture for copyspecial module"""
    @classmethod
    def setUpClass(cls):
        """Performs module import and suite setup at test-runtime"""
        # check for python3
        cls.assertGreaterEqual(cls, sys.version_info[0], 3)
        # This will import the module to be tested
        cls.module = importlib.import_module(PKG_NAME)
        # make a dictionary of each function in the test module
        cls.funcs = {
            k: v for k, v in inspect.getmembers(
                cls.module, inspect.isfunction
                )
            }
        # check the funcs for required functions
        assert "get_special_paths" in cls.funcs, \
            "Missing the get_special_paths() function"
        assert "zip_to" in cls.funcs, "Missing the zip_to() function"
        assert "copy_to" in cls.funcs, "Missing the copy_to() function"

    def setUp(self):
        self.rfs = RandomFileSet()

    def tearDown(self):
        del self.rfs

    def test_get_special_paths_1(self):
        """Checking for list of absolute special paths"""
        actual_path_list = self.module.get_special_paths('.')
        expected_path_list = [
            os.path.abspath(os.path.join(os.getcwd(), f))
            for f in(os.listdir('.'))
            if SPL_REGEX.search(f)
            ]
        self.assertIsInstance(
            actual_path_list, list,
            "get_special_paths is not returning a list"
            )
        self.assertListEqual(actual_path_list, expected_path_list)

    def test_get_special_paths_2(self):
        """Checking against hard-coded path names"""
        actual_path_list = self.module.get_special_paths(self.rfs.tmp_dir)
        self.assertIsInstance(
            actual_path_list, list,
            "get_special_paths is not returning a list"
            )
        a = sorted(actual_path_list)
        b = sorted(self.rfs.spl_file_list)
        self.assertListEqual(
            a, b,
            "Returned path list does not match expected path list"
            )

    def test_copy_to(self):
        """Checking the copy_to function"""
        # Their function should use os.makedirs() to create destination
        # directory if it does not yet exist.
        # Call the test module's copy_to() function
        dest_dir = "/tmp/kenzie-copyto"
        shutil.rmtree(dest_dir, ignore_errors=True)
        self.module.copy_to(self.rfs.abs_file_list, dest_dir + "/dest")
        # check if dest_dir was created and all files got copied
        a = sorted(os.listdir(dest_dir + "/dest"))
        b = sorted(self.rfs.file_list)
        shutil.rmtree(dest_dir, ignore_errors=True)
        self.assertEqual(a, b, "The copy_to function is not working")

    def test_zip_to_1(self):
        """Checking whether special files get zipped"""
        zip_name = "kenzie-copyspecial-ziptest.zip"
        self.clean(zip_name)
        self.module.zip_to(self.rfs.abs_file_list, zip_name)
        assert os.path.exists(zip_name), "The zipfile was not created."
        # open zipfile and verify
        with zipfile.ZipFile(zip_name) as z:
            dest_files = list(z.NameToInfo.keys())
        self.assertEqual(
            sorted(dest_files), sorted(self.rfs.file_list),
            "original files are not being zipped"
            )
        self.clean(zip_name)

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

    def test_main_print(self):
        """Check if the main function is printing the special files list"""
        args = [self.rfs.tmp_dir]
        with Capturing() as output:
            self.module.main(args)
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), len(self.rfs.spl_file_list))

    def test_main_copy_to(self):
        """Check if main() function performs a copy_to operation"""
        to_dir = "/tmp/kenzie-copyspl-copyto"
        args = ["--todir", to_dir, self.rfs.tmp_dir]
        shutil.rmtree(to_dir, ignore_errors=True)
        self.module.main(args)
        expected = list(filter(SPL_REGEX.search, os.listdir(to_dir)))
        self.assertListEqual(
            os.listdir(to_dir), expected,
            "The copy_to() function is not being called from main()")
        shutil.rmtree(to_dir, ignore_errors=True)

    @staticmethod
    def clean(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

    def test_main_zip_to(self):
        """Check if main() function performs a zip compression"""
        to_zip = "/tmp/kenzie-copyspl-zipfile.zip"
        self.clean(to_zip)
        args = ["--tozip", to_zip, self.rfs.tmp_dir]
        self.module.main(args)
        self.assertTrue(os.path.exists(to_zip))
        self.clean(to_zip)


if __name__ == '__main__':
    unittest.main()
