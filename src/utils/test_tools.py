import numpy as np


def relative_error(vel_foam, vel_pygem, vel_pod):
    """
    Compute and print the relative error of vel_pygem and vel_pod with respect
    to vel_foam.

    :param np.ndarray vel_foam: Velocity magnitudes from OpenFOAM.
    :param np.ndarray vel_pygem: Velocity magnitudes from PyGeM.
    :param np.ndarray vel_pod: Velocity magnitudes from POD.
    :return: The relative errors as a tuple.
    :rtype: tuple
    """
    rel_error_pygem = np.abs(vel_pygem - vel_foam) / (np.abs(vel_foam) + 1e-13)
    rel_error_pod = np.abs(vel_pod - vel_foam) / (np.abs(vel_foam) + 1e-13)

    return rel_error_pygem.mean(), rel_error_pod.mean()


def split_by_label(vel, mesh, labels):
    """
    Split velocity and mesh data by label.

    :param torch.Tensor vel: Velocity magnitudes tensor.
    :param np.ndarray mesh: Mesh points as a NumPy array.
    :param list labels: List of simulation labels.
    :return: Velocity magnitudes and mesh points for foam_grid and pygem_grid.
    :rtype: tuple
    """
    # Get indices for foam_grid and pygem_grid
    foam_idx = labels.index("foam_grid")
    pygem_idx = labels.index("pygem_grid")

    # Split the velocity and mesh data
    vel_foam = vel[foam_idx].numpy()
    vel_pygem = vel[pygem_idx].numpy()
    mesh_foam = mesh[foam_idx]
    mesh_pygem = mesh[pygem_idx]

    return vel_foam, vel_pygem, mesh_foam, mesh_pygem
