import numpy as np
import re


def get_data_shape_fromlog():
    """
    Gets the data shape by reading the log file,
    works for different x and y grid points
    """
    with open('log') as logfile:
        loglines = logfile.readlines()

    for line in loglines:
        if re.search(" x              1    FFT", line):
            x_grid_params = re.match(" x              1    FFT (\d+)\s+(-\d+\.\d+)\s+(\d+\.\d+).*", line)
            x_gridpoints = int(x_grid_params.group(1))
            xlims = (float(x_grid_params.group(2)), float(x_grid_params.group(3)))

        if re.search(" y              2    FFT", line):
            y_grid_params = re.match(" y              2    FFT\s+(\d+)\s+(-\d+\.\d+)\s+(\d+\.\d+).*", line)
            y_gridpoints = int(y_grid_params.group(1))
            ylims = (float(y_grid_params.group(2)), float(y_grid_params.group(3)))

    return xlims, ylims, x_gridpoints, y_gridpoints


def wf_loader(representation='adb', state=2, crop_x=None, crop_y=None, save=True):
    """
    Returns a numpy array for the wavefunction density progressing in time

    representation: 'adb' opens the adiabatic wf, 'diab opens the diabatic wf', default adb

    state: which state's wavefunction to look at 1 or 2, default 2

    save: saves the numpy array as a binary file for easier loading later,
    if this is turned on, function will not return the numpy array, use np.load() to load the saved array
    """

    if representation == 'adb':
        file = 'adb2d_x_y'
    elif representation == 'diab':
        file = 'dens2d_x_y'
    else:
        print('Unkown representation')
        return

    # Loads file into python
    with open(file) as di_data:
        print(di_data)
        lines = di_data.readlines()

    xlims, ylims, x_gridpoints, y_gridpoints = get_data_shape_fromlog()

    print('Grid points: X:{0}\n             Y:{1}\n'.format(x_gridpoints, y_gridpoints))
    print('Grid size: X: {0}\n           Y:{1}\n'.format(xlims, ylims))

    x = np.linspace(xlims[0], xlims[1], x_gridpoints)
    y = np.linspace(ylims[0], ylims[1], y_gridpoints)
    x, y = np.meshgrid(x, y)

    all_data_arr = np.empty((x_gridpoints, y_gridpoints, 1))
    times = []
    array_row = 0
    array_col = 0

    for line in lines:

        # Get the time steps
        if re.search("# Time:\s+\d+", line):
            # Gets the time whenever this line occurs
            time = float(re.search('\d+\.\d+', line).group(0))
            times.append(time)
            # Appends one_timestep_data to an array: 'all_data'
            if time != 0.0:
                # Stack the data for each timeslice in the array
                all_data_arr = np.dstack((all_data_arr, one_timestep_data))
            print(f'Time = {time} fs in progress')
            # Reset one timestep data to zero for every timestep
            one_timestep_data = np.empty((x_gridpoints, y_gridpoints))

            # Set the row and column counters to zero at every new timestep
            array_col = 0
            array_row = 0

        # Find lines that actually contain data, puts them into a 2D array one_timestep_data
        if re.search("^\s+-?\d", line):
            data_cols = line.split()
            # print(array_row, array_col)

            one_timestep_data[array_row, array_col] = data_cols[state + 1]
            array_row += 1

        # For every blank line in the datafile, increment the row in the 2D array timestep
        if re.search("^\s+$", line):
            array_col += 1
            array_row = 0

        if line == lines[-1]:
            print('Done')

    # get rid of empty timeslice used to initialise the array at the start
    all_data_arr = np.delete(all_data_arr, 0, axis=2)

    # Crop the data
    if crop_x is not None:
        xmin_diff = np.abs(x[0, :] - crop_x[0])
        i_xmin = np.where(xmin_diff == min(xmin_diff))[0][0]

        xmax_diff = np.abs(x[0, :] - crop_x[1])
        i_xmax = np.where(xmax_diff == min(xmax_diff))[0][0]

        all_data_arr = all_data_arr[int(i_xmin):int(i_xmax), :, :]

    if crop_y is not None:
        ymin_diff = np.abs(y[:, 0] - crop_y[0])
        i_ymin = np.where(ymin_diff == min(ymin_diff))[0][0]

        ymax_diff = np.abs(y[:, 0] - crop_y[1])
        i_ymax = np.where(ymax_diff == min(ymax_diff))[0][0]

        all_data_arr = all_data_arr[:, int(i_ymin):int(i_ymax), :]

    print(f'X crop: ({i_xmin}, {i_xmax})\nY crop: ({i_ymin}, {i_ymax})\n')

    if save:
        with open('{0}-wf-state{1}'.format(representation, state), 'wb') as arr:
            np.save(arr, all_data_arr)
        return

    return all_data_arr, times, (x, y), (xlims, ylims)


def v_polar(rho, psi, F, ax, ay, e):
    """
    The function that returns the PES for a conical intersection
    """
    vp = F*rho*(np.tan(ax)*np.cos(psi) + np.tan(ay)*np.sin(psi) +
                np.sqrt((np.cos(psi))**2 + e*(np.sin(psi))**2))
    vn = F*rho*(np.tan(ax)*np.cos(psi) + np.tan(ay)*np.sin(psi) -
                np.sqrt((np.cos(psi))**2 + e*(np.sin(psi))**2))
    return vn, vp



def momentum_solver(desired_energy, alpha_x, alpha_y, F, e, x_init, y_init, mass, state=2):
    '''
    Given a position x, y and parameters of the CI, returns components of the momentum required to
    bring energy of gwp up to a desired energy at CI point.

    desired_energy (float), Hartree:

        Kinetic energy desired at the CI point.


    alpha_x (float), degrees:

        Tilt anlge of CI in x direction.


    alpha_y (float), degrees:

        Tilt anlge of CI in y direction.


    F (float), Hartree per Bhor:

        Slope parameter of CI.


    e (float), unitless:

        Eccentricity of CI.


    x_init (float), Bhor:

        Starting x coordinate of gwp.


    y_init (float), Bhor:

        Starting y coordinate of gwp.


    mass (float), atomic units of mass:

        Mass of system.


    state (int):

        Which adiabatic state the gwp is initialised on.
    '''
    # Convert cartesian coordinates to polar
    rho = np.sqrt(x_init ** 2 + y_init ** 2)
    psi = np.arctan2(y_init, x_init)
    # Convert from polar parameters to cartesian
    ax = F * np.tan(alpha_x)
    ay = F * np.tan(alpha_y)
    bx = F ** 2
    by = e * F ** 2

    # State selection for use in pes_cartesian
    if state == 2:
        i = 1
    elif state == 1:
        i = 0
    else:
        print('Unknown state')
        return

    init_energy = v_polar(rho, psi, F, alpha_x, alpha_y, e)[i]

    direction = np.array([-1 * x_init, -1 * y_init]) / np.sqrt(x_init ** 2 + y_init ** 2)
    direction = 1
    magnitude = np.sqrt(2 * mass * (desired_energy - init_energy))
    momentum_vect = direction * magnitude

    return momentum_vect