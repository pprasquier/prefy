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
    # This class is used to load and manage settings from JSON files in a specified directory.
    # It allows for dynamic loading of settings and provides methods to access and update them.
    # It also supports automatic settings loading based on the presence of certain files and directories.
    def __iter__(self):
        # Return an iterator over the non-meta attributes
        attrs = {k: v for k, v in vars(self).items() if k != 'meta'}
        return iter(attrs.items())
    
    def __init__(self, directory_path=DEFAULT_DIR, bypass_directory=False, ad_hoc_prefs=None, allow_missing_attributes=False,**kwargs):
        """
        Initializes a Preferences instance, loading settings from JSON and txt files in the specified directory.

        Parameters:
        directory_path (str): The path to the directory containing the settings files. Defaults to 'settings_files'.
        bypass_directory (bool): If True, bypasses the directory and only loads the kwargs. Defaults to False.
        ad_hoc_prefs: A dictionary or list of tuples of ad-hoc preferences to set as attributes on the instance. Defaults to None.
        allow_missing_attributes: (bool): If True, allows missing attributes without raising an error. Defaults to False.
        **kwargs: Additional keyword arguments to set as attributes on the instance. Useful for testing purposes.

        Raises:
        OSError: If the specified directory path is invalid.
        Exception: For any other errors encountered during initialization.
        """
        try:    
            self.meta = Meta()        
            if not bypass_directory:
                if not os.path.isdir(directory_path):
                    logging.warning("Invalid directory: '{}'.".format(directory_path))
                    raise OSError("Invalid directory: '{}'.".format(directory_path))
                
                self.meta.directory_path = directory_path
                self.refresh(force_update=False)
            
            if ad_hoc_prefs is not None:
                self.set_ad_hoc_prefs(ad_hoc_prefs=ad_hoc_prefs)
                
            self.allow_missing_attributes = allow_missing_attributes
                
            if kwargs:
                for key, value in kwargs.items():
                    self.__setattr__(key, value)
                    self.meta.instantiated=True
            
                
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
        
    def set_ad_hoc_prefs(self, ad_hoc_prefs):
        # Set attributes from kwargs
        if not isinstance(ad_hoc_prefs, dict):
            for key, value in ad_hoc_prefs:
                self.__setattr__( key, value)
        else:
            for key, value in ad_hoc_prefs.items():
                self.__setattr__(key, value)
        self.meta.instantiated=True

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
            if name != 'meta' and name != 'check_attribute_updateable' and self.meta.instantiated==True:
                self.check_attribute_updateable(name)
            return super().__getattribute__(name)
        except Exception as e:
            logging.warning("{} - Unknown attribute with name '{}'. Add an element with this key to the list of attributes in a JSON file within directory '{}'.".format(e,name,self.meta.directory_path))
            if self.allow_missing_attributes:
                return None
            else:
                raise AttributeError

class CollectionItem:
    def __init__(self, name:str, preferences:Preferences):
        self.name = name
        self.preferences = preferences

class PreferencesCollection:
    def __init__(self, directory_path):
        if not os.path.isdir(directory_path):
            logging.error("Invalid directory: '{}'.".format(directory_path))
            raise OSError("Invalid directory: '{}'.".format(directory_path))
        
        self.items: list[CollectionItem] = []
        # Get all subdirectories in the parent directory
        for directory in [os.path.join(directory_path, d) for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]:
            if not os.path.isdir(directory):
                logging.error("Invalid directory: '{}'.".format(directory))
                raise OSError("Invalid directory: '{}'.".format(directory))
            
            preferences = Preferences(directory_path=directory)
            name = os.path.basename(directory)
            item=CollectionItem(name, preferences)
            self.items.append(item)

    def get_by_name(self, name):
        # Return a specific Preferences object by name
        for item in self.items:
            if item.name == name:
                return item.preferences
        logging.error("Preferences object not found with name '{}'.".format(name))
        raise KeyError("Preferences object not found with name '{}'.".format(name))

    def get_by_index(self, index):
        # Return a specific Preferences object by index
        if index < len(self.items):
            return self.items[index].preferences
        else:
            logging.error("Index out of range: '{}'.".format(index))
            raise IndexError("Index out of range: '{}'.".format(index))

    def list_names(self):
        # Return a list of names of all Preferences objects in the collection
        return [item.name for item in self.items]

    def __iter__(self):
        # Return an iterator over the Collection item objects in the collection
        for item in self.items:
            yield item

    def __len__(self):
        return len(self.items)

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
