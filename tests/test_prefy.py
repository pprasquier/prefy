import shutil
import unittest
import os
import json

from prefy.prefy import Preferences, PreferencesCollection

TEST_DIR_PATH='temp'

class TestSettings(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR_PATH, exist_ok=True)
    
    def test_invalid_directory(self):
        with self.assertRaises(expected_exception=OSError):
            Preferences('non_existent_directory')

    def test_empty_directory(self):
        with self.assertRaises(expected_exception=FileNotFoundError):
            Preferences(TEST_DIR_PATH)

 
    def test_default_directory_not_exists(self):
        with self.assertRaises(expected_exception=OSError): #Assumes the default directory doesn't exist
            Preferences()

                              
    def test_auto_settings(self):
    # Create temporary directory and JSON files

        tmpdirname = TEST_DIR_PATH
        # Create JSON files
        json_file1 = os.path.join(tmpdirname, "1.settings1.json")
        json_file2 = os.path.join(tmpdirname, "2.settings2.json")
        json_file3 = os.path.join(tmpdirname, "3.deactivated.json")
        json_file4 = os.path.join(tmpdirname, "4.invalid.json")
        
        with open(json_file1, "w") as file:
            json.dump([
                {"type": "Prefy", "key": "deactivate_setting_file", "value": False},
                {"type": "Embeddings", "key": "resume_dir_path", "value": "/path1"},
                {"type": "Embeddings", "key": "insight_dir_path", "value": "/path1"},
                {"type": "Embeddings", "key": "boolean", "value": True},  
                {"type": "Embeddings", "key": "number", "value": 4}                 
            ], file)
            with open(json_file2, "w") as file:  # Should be found and its settings should supersede those of file 1
                json.dump([
                    {"type": "Prefy", "key": "deactivate_setting_file", "value": False},
                    {"type": "Embeddings", "key": "insight_dir_path", "value": "/path2"},
                    {"force_update": True, "key": "updateable_value", "value": "Obsolete value"}
                ], file)
            with open(json_file3, "w") as file: # Should be found but not loaded since it is deactivated
                json.dump([
                    {"type": "Prefy", "key": "deactivate_setting_file", "value": True},
                    {"type": "Embeddings", "key": "resume_dir_path", "value": "/path3"}
                ], file)
            with open(json_file4, "w") as file: # Should be found but not loaded since it is not a valid json file
                file.write("Hello, World!\n")

        # Create .txt files
        txt_file1 = os.path.join(tmpdirname, "5_first_prompt.txt")
        txt_file2 = os.path.join(tmpdirname, "6_second_prompt.txt")
        with open(txt_file1, "w") as file:
            file.write("This is the first prompt.")
        with open(txt_file2, "w") as file:
            file.write("This is the second prompt.")

        # Call the function
        result = Preferences(directory_path=tmpdirname,system_instructions="Test system instructions",
    user_prompt="Test user prompt",str_output_parser='UnsupportedParser')
        self.assertEqual(result.system_instructions, 'Test system instructions',"Failed to retrieve kwarg value 1")
        self.assertEqual(result.str_output_parser, "UnsupportedParser","Failed to retrieve kwarg value 3")
        
        # Verify .txt file content
        self.assertEqual(result.first_prompt, "This is the first prompt.")
        self.assertEqual(result.second_prompt, "This is the second prompt.")

        # Verify the result
        self.assertEqual(result.insight_dir_path, "/path2")
        self.assertEqual(result.resume_dir_path, "/path1")
        self.assertEqual(result.meta.files_found, 6)
        self.assertEqual(result.meta.files_loaded, 4)
        self.assertTrue(result.boolean, "Failed to retrieve boolean value")
        self.assertEqual(result.number, 4, "Failed to retrieve number value")
        self.assertEqual(result.updateable_value, "Obsolete value")

        with open(json_file2, "w") as file:  # Updating the json file without explicitly refreshing result
            json.dump([
                {"force_update": False, "key": "updateable_value", "value": "Updated value"}
            ], file)
        print(result.updateable_value)
        self.assertEqual(result.updateable_value, "Updated value")
                
        with self.assertRaises(AttributeError):
            result.inexisting_setting
     
    def test_only_kwargs_passed(self):        
            result = Preferences(bypass_directory=True, ad_hoc_prefs={"system_instructions":"Test system instructions",
    "user_prompt":"Test user prompt","str_output_parser":'UnsupportedParser'})
            self.assertEqual(result.system_instructions, 'Test system instructions',"Failed to retrieve kwarg value 1")
            self.assertEqual(result.str_output_parser, "UnsupportedParser","Failed to retrieve kwarg value 3")
        
    def test_create_preferences_collection_non_string_directory_path(self):
        with self.assertRaises(expected_exception=OSError):
            PreferencesCollection(12345)  # Passing a non-string directory path
    
    def test_create_preferences_collection_correct_keys(self):
        # Set up test directories
        test_dirs = ['temp/dir1', 'temp/dir2']
        for dir_name in test_dirs:
            os.makedirs(dir_name, exist_ok=True)
        
        # Create dummy JSON files in each directory
        for dir_name in test_dirs:
            json_file = os.path.join(dir_name, "settings.json")
            with open(json_file, "w") as file:
                json.dump([{"type": "Embeddings", "key": "example_key", "value": "example_value"}], file)
        
        # Instantiate the PreferencesCollection
        collection = PreferencesCollection('temp')
        
        # Verify the result
        self.assertEqual(set(collection.settings_dict.keys()), {os.path.basename(d) for d in test_dirs})
        self.assertEqual(collection.get_by_key('dir1').example_key, "example_value")
        
        # Access the first item by index
        first_preferences = collection.get_by_index(0)
        self.assertEqual(first_preferences.example_key, "example_value")
 
        # Test the list_keys method
        expected_keys = {os.path.basename(d) for d in test_dirs}
        actual_keys = set(collection.list_keys())
        self.assertEqual(actual_keys, expected_keys)       
            

    def tearDown(self):
        shutil.rmtree(TEST_DIR_PATH)