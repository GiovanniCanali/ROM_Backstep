from glob import glob
import numpy as np
import pyvista
import torch
import re
import os


def get_training_data():
    """
    Load the training data from the VTK files of the OpenFOAM simulations.
    It returns the velocity magnitudes and the corresponding mu parameters as
    tensors of shape [n_simulations, n_points] and [n_simulations, 1]
    respectively. It also returns the mesh points as a NumPy array.
    """
    # Define the base directory for OpenFOAM simulations
    base_dir = "openfoam_simulations"

    # Initialize lists to store data and parameters
    all_data = []
    all_points = []
    all_params = []

    # Find all VTK files in the directory
    vtu_paths = glob(
        f"{base_dir}/simulation_mu_*/VTK/simulation_mu_*_*/internal.vtu",
        recursive=True,
    )

    # Loop through each VTK file
    for vtu_path in vtu_paths:

        try:
            # Extract the mu parameter and append it to the list
            match = re.search(r"simulation_mu_(-?\d*\.?\d*)", vtu_path)
            all_params.append(np.array([[float(match.group(1))]]))

            # Load the mesh and the coordinates
            mesh = pyvista.read(vtu_path)
            all_points.append(mesh.points)

            # Compute the velocity magnitude and append it to the list
            velocity = mesh.point_data.get("U")
            vel_magnitude = np.linalg.norm(velocity[:, :2], axis=1)
            all_data.append(vel_magnitude)

        # If there's an error reading the file, print a message and continue
        except Exception as e:
            print(f"Error processing {vtu_path}: {e}")

    # Stack results
    params = torch.tensor(np.vstack(all_params), dtype=torch.float32)
    vel_magnitudes = torch.tensor(np.vstack(all_data), dtype=torch.float32)
    mesh_points = np.array(all_points)

    return vel_magnitudes, params, mesh_points


def get_test_data():
    """
    Load the test data from the VTK files of the test OpenFOAM simulations.
    It returns the velocity magnitudes and the corresponding mu parameters as
    tensors of shape [1, n_points] and [1, 1] respectively.
    """
    # Initialize lists to store data and parameters
    all_data = []
    all_points = []
    sim_labels = []

    # Find all VTK files in the directory
    vtu_paths = glob("test/*_grid/VTK/*_grid_*/internal.vtu", recursive=True)

    # Loop through each VTK file
    for vtu_path in vtu_paths:

        try:
            # Load the mesh and the coordinates
            mesh = pyvista.read(vtu_path)
            all_points.append(mesh.points)

            # Compute the velocity magnitude and append it to the list
            velocity = mesh.point_data.get("U")
            vel_magnitude = np.linalg.norm(velocity[:, :2], axis=1)
            all_data.append(vel_magnitude)

            # Extract simulation name (foam_grid or pygem_grid)
            sim_dir = vtu_path.split("/")[-4]
            sim_labels.append(sim_dir)

        # If there's an error reading the file, print a message and continue
        except Exception as e:
            print(f"Error processing {vtu_path}: {e}")

    # Stack results
    vel_magnitudes = torch.tensor(np.vstack(all_data), dtype=torch.float32)
    mesh_points = np.array(all_points)

    return vel_magnitudes, mesh_points, sim_labels


def get_mu(path):
    """
    Get the mu parameter from the mesh_<mu>.png file in the test directory.

    :param str path: Directory to search for the mesh_<mu>.png file.
    :return: The mu parameter as a float.
    :rtype: float
    :raises FileNotFoundError: If no mesh_<mu>.png file is found in the
        specified directory.
    """
    # Iterate through the files in the test directory
    for filename in os.listdir(path):
        match = re.match(r"mesh_(-?\d+\.\d+)\.png$", filename)
        if match:
            return float(match.group(1))

    # If no file is found, raise an error
    raise FileNotFoundError(f"No mesh_<mu>.png file found in {path}")
