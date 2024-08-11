import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -  %(filename)s - %(lineno)d - %(message)s')

DEFAULT_DIR='settings_files'
#JSON properties. Careful when changing as they are used in human-made documents
KEY="key"
VALUE="value"
TYPE="type"

#JSON values. Careful when changing as they are used in human-made documents
INTERNAL_SETTINGS="Prefy"

#Reserved keys
DEACTIVATE="deactivate_setting_file"

class Meta: #Info about this instance
        def __init__(self): 
            self.directory_path=None
            self.instantiated=False
            self.files=[]
            self.files_found=0
            self.files_loaded=0
        
class Settings:    
    def __init__(self,directory_path=DEFAULT_DIR):
        try:
            if not os.path.isdir(directory_path):
                logging.error("Invalid directory: '{}'.".format(directory_path))
                raise OSError   
            self.meta=Meta()
            self.meta.directory_path=directory_path
            self.refresh(force_update=False)
          
        except OSError:
            raise
        
        except Exception as e:
            logging.error('Error {} .'.format(e))
            raise Exception      

    #Finds the json files in the given directory and loads them into the instance's meta object
    def load_files(self):
        try:
            self.meta.files = sorted([f for f in os.listdir(self.meta.directory_path) if f.endswith('.json')])
            self.meta.files_found = len(self.meta.files)
            if self.meta.files_found == 0:
                logging.info("No JSON files found in '{}'.".format(self.meta.directory_path))
                raise FileNotFoundError
        except FileNotFoundError:
            raise
            
        except Exception as e:
            logging.error('Error {} .'.format(e))
            raise Exception                   
    
    def refresh(self,force_update=True):
        try:
            if force_update or self.meta.instantiated==False:     
                # Get a list of JSON files in the directory
                self.load_files()

                # Loop through each JSON file
                for json_file_name in self.meta.files:
                    filepath=os.path.join(self.meta.directory_path,json_file_name)
                    targetFile=open(file=filepath, mode='r')
                    content=targetFile.read()
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        logging.warning("Invalid JSON format in file '{}'.".format(filepath))
                        continue
                    
                    # Check if the file should be skipped
                    deactivate_setting = any(record.get(KEY) == DEACTIVATE and record.get(VALUE) == True
                                            for record in data)
                    if deactivate_setting:
                        continue

                    self.meta.files_loaded +=1
                    # Process records other than type "Settiings"
                    # TODO: Add logic to prevent overwriting existing settings when restricted=true 
                    # TODO: Add logic to force update when force_update=true 
                    for record in data:
                        if record.get(TYPE) != INTERNAL_SETTINGS: 
                            key = record.get(KEY)
                            value = record.get(VALUE)
                            self.__setattr__(key, value)
                    self.meta.instantiated=True
        except FileNotFoundError:
            raise
        
        except Exception as e:
            logging.error('Error {} .'.format(e))
            raise Exception
    
    def check_setting_value(self,setting_name):
        #Display the current value of a setting
         try:
            current_value=getattr(self, setting_name)
            return current_value
         except AttributeError as e:
             logging.warning("Unknown attribute with name '{}'.".format(e,setting_name))
             raise AttributeError
         
         except Exception as e:
            logging.error('Error {} .'.format(e))
            raise Exception
    
    def __repr__(self):
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{{{attributes}}}"

class SettingsWrapper:
    #All classes should have a settings object
    def __init__(self, settings=None,directory_path=DEFAULT_DIR):
        if settings is None:
            settings=Settings(directory_path=directory_path)
            
        self.settings=settings
    
    def refresh_settings(self):
        self.settings.refresh(force_update=True)
