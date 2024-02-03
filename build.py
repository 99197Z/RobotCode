import os
import subprocess
#os.environ["HOMEPATH"]+r"\Downloads\PortableGit\bin\git.exe"
result = subprocess.run(["git", 'rev-parse',"--short","HEAD"], stdout=subprocess.PIPE)
with open("src\\main.py","r") as f:
    with open("src\\out.py","w") as F:
        t = f.read().replace('CODE_VER = "DEV"',f"CODE_VER = '{result.stdout.decode().removesuffix("\n")}'")
        F.write(t)