import re
import subprocess
import os
from quantics_tools import wf_loader

cwd = os.getcwd()
experiment_name = os.path.split(cwd)[1]

items = os.listdir(cwd)

for item in items:
    if os.path.isdir(item) and re.search(r'^momentum_p.*', item):
        print(item)
        os.chdir(item)
        subprocess.run(["dengen", "-w", "-o", "./dens2d", "-step", "3", "x", "y"])
        subprocess.run(["di2ad", "-w", "-o", "./psi.ad"])
        subprocess.run(["dengen", "-w", "-f", "./psi.ad", "-o", "./adb2d", "-step",
                        "3", "x", "y"])

        # Load and save the data as binary numpy files
        wf_loader('adb', state=2, crop_x=(-5, 10), crop_y=(-5, 5))
        wf_loader('adb', state=1, crop_x=(-5, 10), crop_y=(-5, 5))
        wf_loader('diab', state=1, crop_x=(-5, 10), crop_y=(-5, 5))
        wf_loader('diab', state=2, crop_x=(-5, 10), crop_y=(-5, 5))

        # send data to onedrive
        subprocess.run(["rclone", "copy", "./adb-wf-state2",
                        "imp:/year-4/msci-project/data/{0}/{1}".format(experiment_name, item)])
        subprocess.run(["rclone", "copy", "./adb-wf-state1",
                        "imp:/year-4/msci-project/data/{0}/{1}".format(experiment_name, item)])
        subprocess.run(["rclone", "copy", "./diab-wf-state1",
                        "imp:/year-4/msci-project/data/{0}/{1}".format(experiment_name, item)])
        subprocess.run(["rclone", "copy", "./diab-wf-state2",
                        "imp:/year-4/msci-project/data/{0}/{1}".format(experiment_name, item)])
        #subprocess.run(["rclone", "copy", "./adb2d_x_y",
                        #"imp:/year-4/msci-project/data/momentum-experiment/{}".format(item)])
        subprocess.run(["rclone", "copy", "./log",
                        "imp:/year-4/msci-project/data/{0}/{1}".format(experiment_name, item)])
        os.chdir(cwd)

