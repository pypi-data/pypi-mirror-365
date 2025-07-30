import subprocess
from typing import Tuple


def run(cmd:str ,cwd:str=None, env:dict = None)->Tuple[int,str,str]:
    """Run a shell command and return the return code, stdout and stderr"""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")