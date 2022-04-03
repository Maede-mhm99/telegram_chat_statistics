import json
from pathlib import Path
from typing import Union

def read_file(file_path: Union[str, Path]):
    """read text file and return file content as a str 
    """
    with open(file_path) as f:
        return f.readlines()

def read_json(file_path: Union[str, Path]):
    """reads a json file and returns a dict
    """
    with open(file_path,encoding='utf-8') as f:
        return json.load(f)

def dump_json(data_obj,file_path: Union[str, Path]):
    """dump a data object in a file
    """
    with open(file_path,'w') as f:
        json.dump(data_obj,f,indent=4,sort_keys=True)
