from smithers.io.openfoam import OpenFoamHandler
from .plotter import plot_mesh
from pygem import RBF
import numpy as np
import random
import shutil
import os
import re


def mesh_to_numpy(file):
    """
    Read a mesh from an OpenFOAM 'points' file and returns it as a NumPy array.

    :param str file: Path to the OpenFOAM points file.
    :return: NumPy array of mesh points.
    :rtype: np.ndarray
    :raises ValueError: If points cannot be parsed.
    """
    # Read the file
    with open(file, "r") as f:
        lines = f.readlines()

    # Skip header and find the number of points
    for i, line in enumerate(lines):
        line = line.strip()
        if line.isdigit():
            num_points = int(line)
            start_index = i + 2
            break
    else:
        raise ValueError("Could not find number of points in the file.")

    # Extract points
    points = []
    for line in lines[start_index : start_index + num_points]:
        line = line.strip().strip("()")
        if not line:
            continue
        coords = list(map(float, line.split()))
        if len(coords) != 3:
            raise ValueError(f"Invalid point line: {line}")
        points.append(coords)

    return np.array(points)


def setup_simulation(pts, header_file, n_deformations):
    """
    Setup the OpenFOAM simulation directories and create deformation parameters.

    :param np.ndarray pts: Mesh points as a NumPy array.
    :param str header_file: Path to the header file for OpenFOAM.
    :param int n_deformations: Number of deformations to create.
    """
    # Define the base directory and reference directory
    reference_dir = "reference_simulation"
    simulation_dir = "openfoam_simulations"
    img_dir = "openfoam_simulations/img"

    # Create required directories if they don't exist
    os.makedirs(simulation_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    # Create a list of 10 deformation parameters
    values = [random.uniform(-1, 1) for _ in range(n_deformations)] + [-1, 1]

    # Create the directories for the OpenFOAM simulations
    for mu in values:

        # Format the folder name
        format_value = f"{mu:.6f}"
        sim_dir = os.path.join(simulation_dir, f"simulation_mu_{format_value}")

        # Create the target directory if it doesn't exist
        if not os.path.exists(sim_dir):
            shutil.copytree(reference_dir, sim_dir)

        # Write the parameter
        with open(os.path.join(sim_dir, "parameter.txt"), "w") as f:
            f.write(f"Deformation parameter along the y direction: {mu}\n")

        # Compute and save the deformation
        file = os.path.join(sim_dir, "constant/polyMesh/points")
        compute_deformation(
            mu=mu, pts=pts, img_dir=img_dir, file=file, header_file=header_file
        )


def compute_deformation(mu, pts, img_dir, file, header_file):
    """
    Compute the deformation and save the deformed mesh.

    :param float mu: Deformation parameter to apply.
    :param np.ndarray pts: Mesh points as a NumPy array.
    :param str img_dir: Directory to save the deformation image.
    :param str file: Path to the target points file.
    :param str header_file: Path to the header file for OpenFOAM.
    """
    # Define the control points
    ctrl_pts = pts[get_mask(pts)]

    # Deformation parameters
    original_ctrl_pts = ctrl_pts.copy()
    deformed_ctrl_pts = ctrl_pts.copy()
    deformed_ctrl_pts[deformed_ctrl_pts[:, 1] == 5, 1] += mu

    # Define the RBF interpolator
    rbf = RBF(original_ctrl_pts, deformed_ctrl_pts, radius=100)

    # Compute the new mesh and plot the original and deformed meshes
    new_mesh = rbf(pts)
    image = f"{img_dir}/mesh_{mu}.png"
    plot_mesh(pts=new_mesh, clr="red", title="Deformed Mesh", file=image)

    # Create OpenFOAM handler and write the deformed mesh
    of_handler = OpenFoamHandler()
    of_handler.write_points(new_mesh, file, header_file)


def get_mask(pts):
    """
    Create a mask for horizontal boundaries.

    :param np.ndarray pts: Mesh points as a NumPy array.
    :return: Boolean mask for horizontal boundaries.
    :rtype: np.ndarray
    """
    bottom = pts[:, 1] == 0
    top = pts[:, 1] == 5
    left = (pts[:, 1] == 2) & ((pts[:, 0] >= 0) & (pts[:, 0] <= 4))

    # Combine all masks
    return bottom | top | left


def change_vertices(file, mu):
    """
    Move the upper vertices of the mesh by mu in the y-direction.

    :param str file: Path to the blockMeshDict file.
    :param float mu: Deformation parameter to apply.
    """
    # Open the blockMeshDict file and read its contents
    with open(file, "r") as f:
        lines = f.readlines()

    # Modify the vertices section to adjust the y-coordinate by mu
    new_lines = []
    in_vertices = False
    found_vertices = False

    # Iterate through the lines to find the vertices section
    for line in lines:

        # Look for the start of the vertices section
        if not in_vertices:

            # Start of the vertices block
            if "vertices" in line:
                found_vertices = True
                new_lines.append(line)
                continue

            if found_vertices and "(" in line:
                in_vertices = True
                found_vertices = False
                new_lines.append(line)
                continue

            # If not in the vertices section, just copy the line
            new_lines.append(line)

        else:
            # End of the vertices block
            if in_vertices and ");" in line:
                in_vertices = False
                new_lines.append(line)
                continue

            # If in the vertices section, modify the y-coordinate
            if in_vertices:
                # Match lines like: (x y z) and capture them
                m = re.match(
                    r"\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*\)(.*)",
                    line,
                )
                if m:
                    x = float(m.group(1))
                    y = float(m.group(2))
                    z = float(m.group(3))
                    rest = m.group(4)

                    # Add mu only if y == 5
                    if abs(y - 5) < 1e-9:
                        y_new = 5 + mu
                    else:
                        y_new = y

                    new_line = f"    ({x:.6f}   {y_new:.6f}   {z:.6f}){rest}\n"
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)

    # Write the modified lines back to the file
    with open(file, "w") as f:
        f.writelines(new_lines)
