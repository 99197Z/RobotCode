import os
import subprocess
#os.environ["HOMEPATH"]+r"\Downloads\PortableGit\bin\git.exe"
result = subprocess.run(["git", 'rev-parse',"--short","HEAD"], stdout=subprocess.PIPE)
with open("src\\main.py","r") as f:
    with open("src\\out.py","w") as F:
        t = f.read().replace('CODE_VER = "DEV"',f"CODE_VER = '{result.stdout.decode().removesuffix("\n")}'")
        with open("atton.py","r") as fa:
            t = t.replace("a = '' #atton",f'a = "{fa.read().replace('\n',"\\n")}"')
        with open("skills_atton.py","r") as fa:
            t = t.replace("a = '' #skills",f'a = "{fa.read().replace('\n',"\\n")}"')
        F.write(t)