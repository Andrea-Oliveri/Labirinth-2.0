# -*- coding: utf-8 -*-

"""Module that tests the module files."""

import unittest
import os
import src.server.files as files


class TestFiles(unittest.TestCase):
    """Test case used to test functions in module files."""
    
    def setUp(self):
        # Addition of temporary test maps to levels folder. These maps will be
        # deleted after execution of tests.
        
        
    def tearDown(self):
        # Deletion of all maps used for testing in this class.
        
        
        
    
    def test_choose_level(self):
        """Tests the function files.choose_level."""
        # Mock print to make sure all map names are shown except the one without extension.
        # Mock input to try several ways of inputting map name.
        
        
        
        
        
    def test_import_map(self):
        """Test the funtion files.import_map."""
        # Test for non rectangualr map.
        
        # Test for map with invalid borders.
        
        # Test for map with blankspaces and white lines.
        
        # Test of working map.