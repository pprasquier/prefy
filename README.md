# prefy
A library to streamline and standardize preference/settings management in Python projects

# What is it?
Prefy provides developpers with a systematic way to handle the settings of their projects. 
It addresses the following pain points: 
- Losing/having to redefine one's own settings when pulling the new version of a project 
- Differeniating the settings across multiple environments
- Testing the project through different combinations of settings (i.e., different LLMs, etc.)
- Finding the right settings across different locations
- Differentiating between default and custom settings
- etc.

# How does it work?
Prefy translates settings into instances of **PyPClass** objects where each individual setting is an attribute that can hold only one value at any given time.
In order to determine the list of settings and their corresponding values, it will go through directories where the settings are expressd in a fixed json format.   

## Defining a setting
Adding a setting to a project only requires adding a json object to a file placed in a settings directory. 
Here is an example of a json object defining a setting. Note that the keys of this object are fixed and reserved. 
```json
    {
        "key":"resume_dir_path",
        "value":"private\\embeddings\\resume\\",
        "description":"Parent path to the folder where resume embeddings are stored.",
        "type":"Embeddings",
        "restricted":true,
        "force_update":true,
    }
```
### Keys of the setting json object
- **key**: the identifier of the setting. This will ultimately be created and transformed into an attribute of the **PyPClass** object instantiated by Prefy
- **value**: the value of the setting. This will ultimately be the value of the above attribute. 
- **description**: the description of the setting. This key is not handled by Prefy' code and is just used for human informational purposes. *Optional*.
- **type**: the type of the setting.  This key is used for human informational purposes except for the reserved word "Prefy", which indicates that this setting is for internal use of Prefy processes. *Optional*.
- **restricted**: when true, indicates that this setting cannot be overwritten by other versions of it. (TODO) *Optional* 
- **force_update**: when true, indicates that when accessing the setting, Prefy should always check its updated value in the settings files. This allows to change the value of a setting live. (TODO) *Optional* 

## Defining different sets of settings
The power of Prefy comes from its ability to determine the right value for a setting in the context of multiple potential scenarios/combinations.  In order to do so, Prefy expects the developers to specify those combinations through settings files. 
Developers are free to choose the structure that best fits their needs provided that: 
- All the settings to be attached to a single instance of a **PyPClass** object are defined within a single parent directory
- Within a parent directory, a setting can be defined 1 or multiple times across different files. 
- When instantiating the **PyPClass** object, Prefy will assign the last value found in the different files (sorted alphabeticaly) of a same directory to each setting

Here is a settings file structure example:
```
- settings
  - llm
    - 0.DefaultLLM.json
    - 1.Mistral.json
  - app
    - 0.Default_Settings.json
    - 1.Production.json
    - 2.Test.json
    - 3.Dev1.json
    - 35.Speed-optimization.json
```

Such a structure allows the developer to define a set of standard settings for how to work with LLMs and supersede them with their own settings. 
For instance, assuming the following content of *0.DefaultLLM.json*, which is included in the project's git repository as the default settings: 
``` json
    {
        "type":"Models",
        "key":"insights_rag_base_url",
        "description":"LLM model's url.",
        "value":null
    },
    {
        "type":"Models",
        "key":"insights_rag_temperature",
        "description":"Temperature of the model.",
        "value":0.3
    },
    {
        "type":"Models",
        "key":"insights_rag_model_name",
        "description":"Name of the model used for generating insights.",
        "value":"gpt-3.5-turbo"
    }
```
If a contributor to the project wants to specify a different model, they could change 0.DefaultLLM.json, but then, when pushing to the git repository, their own settings would become the standard settings. Instead, by using Prefy, they can just supersede specific settings by defining them in a new file within the same directory. For instance, this could be the content of *1.Mistral.json*:
 ``` json
    {
        "key":"insights_rag_base_url",
        "value":"http://localhost:1234/v1"
    },
    {
        "key":"insights_rag_model_name",
        "value":"TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q2_K.gguf"
    }
```
Since *1.Mistral.json* comes alphabetically after *0.DefaultLLM.json*, Prefy will use its content as the updated value for the settings *insights_rag_base_url* and *insights_rag_model_name*, while still maitaining the value for *insights_rag_temperature* defined in *0.DefaultLLM.json*. And by ignoring *1.Mistral.json* from the git sync, our developer guarantees that they will always be using their own version of the settings.

## Accessing the settings from the code
In order to access the current value of the settings in your code, you need to instantiate a **PyPClass** object for each of your settings directories and then access them as values. 

For instance. 
### Import module
TODO

### Instantiate PyPClass object
TODO

### Access a setting value
TODO

# Addtional features
### Excluding files
Let's assume that I want to fix a bug that on occurs with a specific set of settings. Instead of changing my preferred settings to replicte the but, I can simply create a new file with the appropriate settings and give it the highest priority by giving it a filename starting with "ZZZ", for instance. When I'm done working with this configuration, an easy way to go back to my preferred settings without losing the option to come back to this configuration in the future and preventing it from interfering with my regular settings is to exclude this file from the **PyPClass** instantiation process. 
In order to do so, I'll add the following object to the file: 
 ```json
     {
        "type":"Settings",
        "key": "deactivate_setting_file",
        "description": "When set to true, this file is not taken into account. Use it to easily juggle through different settings configurations.",
        "value": true
    }
 ```   
### Restricing settings changes
TODO

### Forcing updates
TODO


# How to install

# Best practices
Gitignore
0 is for unignored settings

# Reserved key words
The following must not be used as keys for your settings: 
- *deactivate_setting_file*
- *meta*