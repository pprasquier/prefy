import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -  %(filename)s - %(lineno)d - %(message)s')

DEFAULT_DIR='settings_files'
#JSON properties. Careful when changing as they are used in human-made documents
KEY="key"
VALUE="value"
TYPE="type"
FORCE_FIELD_UPDATE="force_update"
RESTRICTED="restricted"

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
            self.updateable_fields=[]
        
class Preferences:    
    def __iter__(self):
        # Return an iterator over the non-meta attributes
        attrs = {k: v for k, v in vars(self).items() if k != 'meta'}
        return iter(attrs.items())
    
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
            self.meta.files = sorted([f for f in os.listdir(self.meta.directory_path) if f.endswith('.json') or f.endswith('.txt')])
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
                for file_name in self.meta.files:
                    if file_name.endswith('.txt'):
                        filepath = os.path.join(self.meta.directory_path, file_name)
                        with open(filepath, 'r') as file:
                            content = file.read().strip()
                            # Extract key from the file name
                            base_name = os.path.basename(file_name)
                            key = base_name.split('_', 1)[-1].replace(' ', '_').lower().replace('.txt', '')
                            # Upsert the content as a preference
                            self.__setattr__(key, content)
                            self.meta.files_loaded +=1
                    elif file_name.endswith('.json'):
                        filepath=os.path.join(self.meta.directory_path,file_name)
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
                            
                            # Add updateable settings to a list
                            if check_boolean_property_value(record,FORCE_FIELD_UPDATE):
                                self.meta.updateable_fields.append(record.get(KEY))
                            else:
                                try:
                                    self.meta.updateable_fields.remove(record.get(KEY))
                                except ValueError:
                                    pass
                                
                            #Upsert settings to Preferences   
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
        
    def check_attribute_updateable(self, name):
        if name in self.meta.updateable_fields:
            self.refresh(force_update=True)
            return True
        else:
            return False

    def __repr__(self):
        # Filter out special methods and only include regular attributes
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items() 
                              if not (key.startswith('__') and key.endswith('__')))
        return f"{{{attributes}}}"
     
    def __getattribute__(self,name):
        try:
            if name != 'meta' and name != 'check_attribute_updateable':
                self.check_attribute_updateable(name)
            return super().__getattribute__(name)
        except Exception as e:
            logging.warning("{} - Unknown attribute with name '{}'. Add an element with this key to the list of attributes in a JSON file within directory '{}'.".format(e,name,self.meta.directory_path))
            raise AttributeError

class PreferencesCollection:
    def __init__(self, directory_path):
        if not os.path.isdir(directory_path):
            logging.error("Invalid directory: '{}'.".format(directory_path))
            raise OSError("Invalid directory: '{}'.".format(directory_path))
        
        self.settings_dict = {}
        # Get all subdirectories in the parent directory
        for directory in [os.path.join(directory_path, d) for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]:
            if not os.path.isdir(directory):
                logging.error("Invalid directory: '{}'.".format(directory))
                raise OSError("Invalid directory: '{}'.".format(directory))
            
            settings = Preferences(directory_path=directory)
            name = os.path.basename(directory)
            self.settings_dict[name] = settings

    def get_by_key(self, key):
        return self.settings_dict.get(key)

    def get_by_index(self, index):
        try:
            key = list(self.settings_dict.keys())[index]
            return self.settings_dict[key]
        except IndexError:
            logging.error("Index out of range.")
            raise IndexError("Index out of range.")

    def list_keys(self):
        return list(self.settings_dict.keys())

    def __iter__(self):
        return iter(self.settings_dict.items())

    def __len__(self):
        return len(self.settings_dict)

    def __getitem__(self, key):
        return self.settings_dict[key]

def check_boolean_property_value(object,key):
    if key in object:
        return object[key]
    else:
        return False

class PreferencesWrapper:
    #All classes should have a settings object
    def __init__(self, settings=None,directory_path=DEFAULT_DIR):
        if settings is None:
            settings=Preferences(directory_path=directory_path)
            
        self.settings=settings
    
    def refresh_settings(self):
        self.settings.refresh(force_update=True)
