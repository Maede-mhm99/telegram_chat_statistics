import functools
import os

from src.data import DATA_DIR


def reshape_fa(func):
    
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        text_content = func(*args,**kwargs)
        temp_file_path  = DATA_DIR / 'file.txt'
        open(temp_file_path,'w').write(text_content)
        text_content = open(temp_file_path,'r',encoding='utf-8').read()
        os.remove(temp_file_path)
        return text_content
    
    return wrapper
