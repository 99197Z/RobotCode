import os
import subprocess
print("build started")
#os.environ["HOMEPATH"]+r"\Downloads\PortableGit\bin\git.exe"
result = subprocess.run(["git", 'rev-parse',"--short","HEAD"], stdout=subprocess.PIPE)
with open("src\\main.py","r") as f:
    with open("src\\out.py","w") as F:
<<<<<<< HEAD
        print(f"CODE VER: {result.stdout.decode().removesuffix("\n")}")
        t = f.read().replace('CODE_VER = "DEV"',f"CODE_VER = '{result.stdout.decode().removesuffix("\n")}'")
        print(f"Final Length: {str(len(t)):>7}")

        print("Writing...")
        F.write(t)
        print("DONE")
=======
        with open("atton.py","r") as fa:
            t = f.read().replace('CODE_VER = "DEV"',f"CODE_VER = '{result.stdout.decode().removesuffix("\n")}'")
            t = t.replace("a = '' #atton",f'a = "{fa.read().replace('\n',"\\n")}"')
            F.write(t)
>>>>>>> master
