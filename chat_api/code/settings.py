
import os
from pathlib import Path
from typing import Union    
from dotenv import load_dotenv


#this file is used to load all variables from .env file with help of dotenv library 

def load_env_vars(root_dir: Union[str, Path]) -> dict:
    """ root_dir: Rood dir of .env file 
        returns dict with environment variables 
    """

    if isinstance(root_dir, str):
        root_dir = Path(root_dir)

    load_dotenv(dotenv_path=root_dir / ".env.default")
    load_dotenv(dotenv_path = root_dir / ".env", override=True)

    return dict(os.environ)
    
#we go back two level to get .env file
def get_root_dir(default_value: str='..') -> Path:
    return Path(os.getenv("ML_PIPELINE_ROOT_DIR", default_value))

ML_PIPELINE_ROOT_DIR = get_root_dir()

SETTINGS = load_env_vars(root_dir=ML_PIPELINE_ROOT_DIR)






