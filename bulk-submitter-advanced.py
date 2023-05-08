import numpy as np
import re
import subprocess
import time
import os
from quantics_tools import v_polar, momentum_solver


def change_and_submit(jobscript, param_value_dict):

    """
    Given the name of a jobscript you want to change, a dictionary of parameter names and their values,
    changes the parameters in the jobscript and submits the job for each value

    jobsctipt: str
    The title of the .pbs jobscript file that you are using

    param_value_dict: dict
    A dictionary with keys being the name of the value in the jobscript that is to be changed, and the values as the
    corresponding list of values.
    """
    with open(jobscript, 'r') as file:
        lines = file.readlines()

    # find lines in the jobscript containing parameters to be changed
    param_indices = {}
    for param_name in param_value_dict.keys():
        for i, line in enumerate(lines):
            if re.search(f'{param_name}=', line):
                param_indices[param_name] = i

    for i, line in enumerate(lines):
        if re.search('experiment_name=', line):
            experiment_name = re.search(r'.*=(.*)', line).group(1)
        if re.search(r'#?mkdir \$experiment_name', line):
            init_idx = [i, i + 1, i + 2, i + 3]

    # get length of value list:
    values_len = len(list(param_value_dict.items())[0][1])

    for i in range(values_len):
        for key in param_value_dict.keys():
            value = param_value_dict[key][i]
            print(key, ':', param_value_dict[key][i])
            lines[param_indices[key]] = f"{key}={value}\n"

        if not os.path.isdir(experiment_name):
            subprocess.run(["echo", "Creating Experiment Directory"])
            for j, line in enumerate([lines[k] for k in init_idx]):
                if line[0] == '#':
                    line = line[1:]
                    mkdir_idx = init_idx[j]
                    lines[mkdir_idx] = line
                else:
                    pass

        else:
            subprocess.run(["echo", "Experiment Directory Found"])
            for j, line in enumerate([lines[k] for k in init_idx]):
                if line[0] != '#':
                    mkdir_idx = init_idx[j]
                    lines[mkdir_idx] = '#' + line

        with open(jobscript, 'w') as file:
            file.writelines(lines)
        # print(*lines, sep='\n')
        subprocess.run(["qsub", f"{jobscript}"])

        # wait for experiment directory to be created
        while True:
            if os.path.isdir(experiment_name):
                break
            time.sleep(5)

        time.sleep(5)



#Testing the function here.
#Point to the jobscript file
jobscript_file = 'tilt.pbs'

# Make a list of values of the CI tilt in x
pi_fractions = [-0.375, -0.25, -0.125, -0.075, 0.0, 0.075, 0.125, 0.25]
alphas = list(map(lambda x: x*np.pi, pi_fractions))

# CI parameters
x_init = -1.8
y_init = 0
F = 0.04
mass = 15000
e = 1
alpha_x = -0.79
alpha_y = 0

# This is the energy with which we want the wavepackets to reach the CI in eV, then converted into hartree with the
# factor of 27.211
E = 9 / 27.21138386

# Calculate the momentum needed to have the same energy for every wavepacket
momenta = momentum_solver(E, alphas, alpha_y, F, e, x_init, y_init, mass, state=2)

# Get a list of directory names for simulations using different alphas
dirnames = list(map(lambda x: f'alpha-a{x}pi', pi_fractions))

# Declare the parameter dictionary
param_dict = {'alpha': alphas, 'momentum': momenta, 'dirname': dirnames}

change_and_submit(jobscript_file, param_dict)
