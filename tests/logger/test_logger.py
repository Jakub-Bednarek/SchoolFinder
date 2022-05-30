import pathlib
import sys
import os

sys.path.append(f"{pathlib.Path().absolute()}")

from src.helpers.logger import logger
    

def test_path_concatenation():
    sample_path = "logs/test/log.log"
    output_path = logger.create_log_path_str(sample_path)
    
    assert output_path == str(pathlib.Path().absolute()) + "/logs/test"
    
def test_path_creation():
    sample_path = "logs/test/log.log"
    full_path = str(pathlib.Path().absolute()) + "/logs/test/"
    print(full_path)
    
    if os.path.exists(full_path):
        os.rmdir(full_path)
        
    logger.create_paths(sample_path)
    
    assert os.path.exists(full_path)
    
    os.rmdir(full_path)