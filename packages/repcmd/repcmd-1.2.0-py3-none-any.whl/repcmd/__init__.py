import subprocess
import json
import os

__version__ = '1.2.0'


def execute(data):
    inp = json.dumps(data, ensure_ascii=False)
    cmd = f'{os.path.dirname(__file__)}/repcmd.sh'
    result = subprocess.run(
        [cmd],
        input=inp.encode(),
        stdout=subprocess.PIPE)
    return result.stdout
