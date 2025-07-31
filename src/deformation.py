from utils import mesh_to_numpy, setup_simulation
import argparse
import os


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--n_values", type=int, default=10)
args = parser.parse_args()

# Check that the reference simulation directory exists
if not os.path.exists("reference_simulation"):
    raise FileNotFoundError(f"Reference simulation directory does not exist.")

# Import the mesh from the original simulation
path = "reference_simulation/constant/polyMesh/points"
pts = mesh_to_numpy(file=path)

# Set up directories for OpenFOAM simulations
setup_simulation(pts=pts, header_file=path, n_deformations=args.n_values)
