import shutil
import unittest
import tempfile
import os
import json

from pyprefs.pyprefs import Settings

TEST_DIR_PATH='temp'

class TestSettings(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR_PATH, exist_ok=True)
    
    def test_invalid_directory(self):
        with self.assertRaises(expected_exception=OSError):
            Settings('non_existent_directory')

    def test_empty_directory(self):
        with self.assertRaises(expected_exception=FileNotFoundError):
            Settings(TEST_DIR_PATH)

 
    def test_default_directory_not_exists(self):
        with self.assertRaises(expected_exception=OSError): #Assumes the default directory doesn't exist
            Settings()

                              
    def test_auto_settings(self):
    # Create temporary directory and JSON files

        tmpdirname=TEST_DIR_PATH
        # Create JSON files
        json_file1 = os.path.join(tmpdirname, "1.settings1.json")
        json_file2 = os.path.join(tmpdirname, "2.settings2.json")
        json_file3 = os.path.join(tmpdirname, "3.deactivated.json")
        json_file4 = os.path.join(tmpdirname, "4.invalid.json")
        
        with open(json_file1, "w") as file:
            json.dump([
                {"type": "Settings", "key": "deactivate_setting_file", "value": False},
                {"type": "Embeddings", "key": "resume_dir_path", "value": "/path1"},
                {"type": "Embeddings", "key": "insight_dir_path", "value": "/path1"},
            ], file)
        with open(json_file2, "w") as file:  # Should be found and its settings should supersde those of file 1
            json.dump([
                {"type": "Settings", "key": "deactivate_setting_file", "value": False},
                {"type": "Embeddings", "key": "insight_dir_path", "value": "/path2"}
            ], file)
        with open(json_file3, "w") as file: # Should be found but not loaded since it is deactivated
            json.dump([
                {"type": "Settings", "key": "deactivate_setting_file", "value": True},
                {"type": "Embeddings", "key": "resume_dir_path", "value": "/path3"}
            ], file)
        with open(json_file4, "w") as file: # Should be found but not loaded since it is not a valid json file
            file.write("Hello, World!\n")

        # Call the function
        result = Settings(tmpdirname)

        # Verify the result
        self.assertEqual(result.insight_dir_path, "/path2")
        self.assertEqual(result.resume_dir_path,"/path1")
        self.assertEqual(result.meta.files_found,4)
        self.assertEqual(result.meta.files_loaded,2)       
    def tearDown(self):
        shutil.rmtree(TEST_DIR_PATH)