import re
import subprocess
import sys

file = sys.argv[1]

output = subprocess.check_output("identify " + file, shell=True)
icons = output.splitlines()

regex = b"\d+x\d+"
maxsize = 0
maxpos = 0
for i, icon in enumerate(icons):
    resolution = re.findall(regex, icon)[0].decode()  # e.g. 16x16
    size = int(resolution.split("x")[0])  # e.g. 16
    if size >= maxsize:
        maxsize = size
        maxpos = i
print(maxpos)
