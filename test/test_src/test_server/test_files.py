# -*- coding: utf-8 -*-

"""Module that tests the module files."""

import unittest
from unittest.mock import patch
import io

import src.server.files as files

files.levels_folder_name = "test\\test_levels"



class TestFiles(unittest.TestCase):
    """Test case used to test functions in module files."""       
        
    def test_choose_level(self):
        """Tests the function files.choose_level."""
        name_test_level = 'ok'
        test_level_path = files.levels_folder_name + '\\' + name_test_level + files.levels_extension
        
        # Mock print to make sure all map names are shown except the one without extension.
        # We also test the function returns the path of the file.
        with patch('sys.stdout', new_callable=io.StringIO) as mock_output, patch('builtins.input', return_value = name_test_level):
            self.assertEqual(test_level_path, files.choose_level())
            self.assertEqual("These are the available maps:\n-> blank spaces and lines\n-> invalid borders\n-> non rectangular\n-> ok\n", mock_output.getvalue())
        
        
    def test_import_map(self):
        """Test the funtion files.import_map."""
        # Test for non rectangualr map.
        with self.assertRaises(RuntimeError):
            files.import_map("test/test_levels/non rectangular.txt")
            
        # Test for map with invalid borders.
        with self.assertRaises(RuntimeError):
            files.import_map("test/test_levels/invalid borders.txt")
        
        # Test for map with blankspaces and white lines.
        self.assertEqual(['OOOOOOOOOO',
                          'O O    O O',
                          'O . OO   O',
                          'O O O    O',
                          'O OOOO O.O',
                          'O O O    U',
                          'O OOOOO  O',
                          'O O   O  O',
                          'O O OOO  O',
                          'O . O    O',
                          'OOOOOOOOOO'], files.import_map("test/test_levels/blank spaces and lines.txt"),)
            
        # Test of working map.
        self.assertEqual(['OOOOOOOOOO',
                          'O O    O O',
                          'O . OO   O',
                          'O O O    O',
                          'O OOOO O.O',
                          'O O O    U',
                          'O OOOOO  O',
                          'O O   O  O',
                          'O O OOO  O',
                          'O . O    O',
                          'OOOOOOOOOO'], files.import_map("test/test_levels/ok.txt"))