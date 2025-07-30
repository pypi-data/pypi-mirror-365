import os

def Cwd() -> str:
    return os.path.abspath('.')

def FileCwd(file) -> str:
    return os.path.dirname(os.path.realpath(file))

def FileParentDirectory() -> str:
    return os.path.dirname(FileCwd())