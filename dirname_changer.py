import re
import sys
import os

files = os.listdir()
for file in files:
    if re.search(r'.*\.inp', file):
        input_file = file

dirname=sys.argv[1]

with open(input_file, 'r') as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    if re.search(r'^name = ', line):
        dirname_idx = i

lines[dirname_idx] = "name = {}  propagation exact\n".format(dirname)

with open(input_file, 'w') as file:
    file.writelines(lines)
