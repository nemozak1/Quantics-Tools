import numpy as np
import re
import subprocess
import time
import os
from quantics_tools import v_polar, momentum_solver

def change_and_submit(jobscript, parameter_name, value_list):
    """
    Given the name of a jobscript you want to change, a list of values, and a variable in the jobscript that you want to
    assign the values to, changes the variable and submits the job
    """

    for index, value in enumerate(value_list):
        with open(jobscript, 'r') as file:
            lines = file.readlines()

        # find lines containing parameter to be changed
        for i, line in enumerate(lines):
            if re.search(f'{parameter_name}=', line):
                dirname_idx = i

            # Check if the experiment directory has been created, if not get indexes of the lines in jobscript that
            # create directory
            if re.search('experiment_name=', line):
                experiment_name = re.search(r'.*=(.*)', line).group(1)
            if re.search(r'#?mkdir \$experiment_name', line):
                init_idx = [i, i + 1, i + 2, i + 3]

        # Uncomment the lines that create the experiment directory if it is not created already, if it is then make sure
        # the lines are commented out
        if not os.path.isdir(experiment_name) and (index == 0):
            subprocess.run(["echo", "Creating Experiment Directory"])
            for j, line in enumerate([lines[i] for i in init_idx]):
                if line[0] == '#':
                    line = line[1:]
                    mkdir_idx = init_idx[j]
                    lines[mkdir_idx] = line
                else:
                    pass

        else:
            subprocess.run(["echo", "Experiment Directory Found"])
            for j, line in enumerate([lines[i] for i in init_idx]):
                if line[0] != '#':
                    mkdir_idx = init_idx[j]
                    lines[mkdir_idx] = '#' + line

        lines[dirname_idx] = f"{parameter_name}={value}\n"

        #print(*lines, sep='\n')

        with open(jobscript, 'w') as file:
            file.writelines(lines)

        subprocess.run(["qsub", f"{jobscript}"])

        # Check for existance of experiment directory, if it doesen't exist, wait till it is created before continuing
        # the loop
        while True:
            if os.path.isdir(experiment_name):
                break
            time.sleep(5)


jobscript_file = 'tilt.pbs'
values = [-3*np.pi/8, -2*np.pi/8, -1*np.pi/8, 0.0, np.pi/8, 2*np.pi/8, 3*np.pi/8]

change_and_submit(jobscript_file, 'sigma', values)


