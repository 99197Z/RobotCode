import os
import subprocess
result = subprocess.run([r"C:\Users\38302008\Downloads\PortableGit\bin\git.exe", 'rev-parse',"--short","HEAD"], stdout=subprocess.PIPE)
with open("src\\main.py","r") as f:
    with open("src\\out.py","w") as F:
        t = f.read().replace('CODE_VER = "DEV"',f"CODE_VER = {result.stdout}")
        F.write(t)