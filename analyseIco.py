import re
import subprocess
import sys

file = sys.argv[1]

output = subprocess.check_output("identify " + file, shell=True)
icons = output.splitlines()

regex = b"\d+x\d+"
maxsize = 0
maxpos = 0
for i, file_line in enumerate(icons):
    resolution = re.findall(regex, file_line)[0].decode()  # e.g. 16x16
    size = int(resolution.split("x")[0])  # e.g. 16
    # "1-bit"-images are not very helpful
    if size >= maxsize and " 1-bit" not in str(file_line):
        maxsize = size
        maxpos = i
print(maxpos)
