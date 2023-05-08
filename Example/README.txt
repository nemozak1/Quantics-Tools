To properly use all the scripts here, transfer the whole directory onto a HPC cluster. 

1. run bulk-submitter-advanced, adjusting parameters at the end of the file as desired, or adjusting some of the input parameters in tilt_input.inp

2. after 1 has finished running (may take days depending on the input parameters), run density_gen.py if you want to visualise the wavefunction density in matlab (script for doing this is not included, but should not be too hard to make)

3. Run through the notebook tilt-analysis-x if you want to analyse the expectation values and plot them