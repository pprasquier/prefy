# prefy
A library to streamline and standardize preference/preferences management in Python projects

# What is it?
Prefy provides developpers with a systematic way to handle the preferences of their projects. 
It addresses the following pain points: 
- Losing/having to redefine one's own preferences when pulling the new version of a project 
- Differeniating the preferences across multiple environments
- Testing the project through different combinations of preferences (i.e., different LLMs, etc.)
- Finding the right preferences across different locations
- Differentiating between default and custom preferences
- etc.

# How does it work?
Prefy translates preferences into instances of **Preferences** objects where each individual setting is an attribute that can hold only one value at any given time.
In order to determine the list of preferences and their corresponding values, it will go through directories where the preferences are expressd in a fixed json format.   

## Defining a setting
Adding a setting to a project only requires adding a json object to a file placed in a preferences directory. 
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
- **key**: the identifier of the setting. This will ultimately be created and transformed into an attribute of the **Preferences** object instantiated by Prefy
- **value**: the value of the setting. This will ultimately be the value of the above attribute. 
- **description**: the description of the setting. This key is not handled by Prefy' code and is just used for human informational purposes. *Optional*.
- **type**: the type of the setting.  This key is used for human informational purposes except for the reserved word "Prefy", which indicates that this setting is for internal use of Prefy processes. *Optional*.
- **restricted**: when true, indicates that this setting cannot be overwritten by other versions of it. (TODO) *Optional* 
- **force_update**: when true, indicates that when accessing the setting, Prefy should always check its updated value in the preferences files. This allows to change the value of a setting live. (TODO) *Optional* 

## Defining different sets of preferences
The power of Prefy comes from its ability to determine the right value for a setting in the context of multiple potential scenarios/combinations.  In order to do so, Prefy expects the developers to specify those combinations through preferences files. 
Developers are free to choose the structure that best fits their needs provided that: 
- All the preferences to be attached to a single instance of a **Preferences** object are defined within a single parent directory
- Within a parent directory, a setting can be defined 1 or multiple times across different files. 
- When instantiating the **Preferences** object, Prefy will assign the last value found in the different files (sorted alphabeticaly) of a same directory to each setting

Here is a preferences file structure example:
```
- preferences
  - llm
    - 0.DefaultLLM.json
    - 1.Mistral.json
  - app
    - 0.Default_Preferences.json
    - 1.Production.json
    - 2.Test.json
    - 3.Dev1.json
    - 35.Speed-optimization.json
```

Such a structure allows the developer to define a set of standard preferences for how to work with LLMs and supersede them with their own preferences. 
For instance, assuming the following content of *0.DefaultLLM.json*, which is included in the project's git repository as the default preferences: 
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
If a contributor to the project wants to specify a different model, they could change 0.DefaultLLM.json, but then, when pushing to the git repository, their own preferences would become the standard preferences. Instead, by using Prefy, they can just supersede specific preferences by defining them in a new file within the same directory. For instance, this could be the content of *1.Mistral.json*:
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
Since *1.Mistral.json* comes alphabetically after *0.DefaultLLM.json*, Prefy will use its content as the updated value for the preferences *insights_rag_base_url* and *insights_rag_model_name*, while still maitaining the value for *insights_rag_temperature* defined in *0.DefaultLLM.json*. And by ignoring *1.Mistral.json* from the git sync, our developer guarantees that they will always be using their own version of the preferences.

## Accessing the preferences from the code
In order to access the current value of the preferences in your code, you need to instantiate a **Preferences** object for each of your preferences directories and then access them as values. 

For instance. 
### Import module
After importing prefy through your favorite package manager (poetry, pip...), you'll be able to import Prefy's classes in your code. 
```python
from prefy import Preferences
```

### Instantiate Preferences object
When you want to load the preferences from a specific directory, you'll just instantiate a **Preferences** class into a new object. 
```python
app_prefs=Preferences('preferences\\app')
```

Remember that you can instantiate as many **Preferences** objects as you want and that each of those instances will load all the settings of its directory. 
Which allows you to easily incorporate different sets of preferences within your code.

For instance, if you would like to pit different llms within your app, you would create two directories, each with the same keys but different values and load them in your code as such:
```python
llm1=Preferences('preferences\\llm1')
llm2=Preferences('preferences\\llm2')
```
You would then be able to have a single logic be applied to your different preferences combinations since those would be treated as variables in your code. And you'd maitain the ability to tweak the preferences without having to touch the code.  

### Access a setting value
From then on, whenever you need to access a setting value, you'll fetch it from your **Preferences** instance. 
```python
vector_store=VectorStore(store_path=app_prefs.embeddings_path,sentence_transformer=app_prefs.sentence_transformer)
```

# Addtional features
### Excluding files manually
Let's assume that I want to fix a bug that on occurs with a specific set of preferences. Instead of changing my preferred preferences to replicte the but, I can simply create a new file with the appropriate preferences and give it the highest priority by giving it a filename starting with "ZZZ", for instance. When I'm done working with this configuration, an easy way to go back to my preferred preferences without losing the option to come back to this configuration in the future and preventing it from interfering with my regular preferences is to exclude this file from the **Preferences** instantiation process. 
In order to do so, I'll add the following object to the file: 
 ```json
     {
        "type":"Prefy",
        "key": "deactivate_setting_file",
        "description": "When set to true, this file is not taken into account. Use it to easily juggle through different preferences configurations.",
        "value": true
    }
 ```   
### Restricing preferences changes
WIP

### Forcing updates
WIP

### Environment variables integration
WIP

# Best practices
Gitignore
0 is for unignored preferences

# Reserved key words
The following must not be used as keys for your preferences: 
- *deactivate_setting_file*
- *meta*