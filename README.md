# Quantics-Tools
A range of python-based tools to be used with UCL's QUANTICS quantum dynamics program

quantics-tools.py contains a program "wf_loader" that reads QUANTICS output wavefunction density files such as psi and psi.ad, and converts them into compressed numpy arrays. 
The arrays can be loaded with numpy.load() and subsequently the wavefunction density can be plotted for each timestep in the simulation using maptlotlib or some other plotting software.

To generate the wavefunction density files in bulk. Put density_gen.py in a folder containing directories that have all quantics simulation outputs in them, run the "density_gen.py" script.

Running the scripts as in the Example folder should show a user exactly how these scripts are supposed to work. Also, the jupyter notebook there contains a number of useful tools for exctracting, plotting, and comparing expectation values for multiple simulations at once.

