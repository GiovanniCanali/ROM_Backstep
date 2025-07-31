from pina.problem.zoo import SupervisedProblem
from model import PODRBF
import numpy as np
import argparse
import warnings
import random
import torch
import os

from utils import (
    mesh_to_numpy,
    get_training_data,
    plot_singular_values,
    compute_deformation,
    plot_test,
)


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--pod_rank", type=int, default=10)
args = parser.parse_args()

# Suppress warnings and create directories if they don't exist
warnings.filterwarnings("ignore")
os.makedirs("test", exist_ok=True)
os.makedirs("test/img", exist_ok=True)

# Load data for each simulation
vel, params, pts = get_training_data()

# Load the original mesh points, corresponding to mu = 0
path = "reference_simulation/constant/polyMesh/points"
original_pts = mesh_to_numpy(file=path)

# Compute and plot the singular values
plot_singular_values(vel=vel, pts=original_pts)

# Compute the mesh corresponding to a random mu sampled from [-1, 1]
random_mu = 2 * random.random() - 1
compute_deformation(
    mu=random_mu,
    pts=original_pts,
    img_dir="test/img",
    file="test/points",
    header_file=path,
)

# Reload the deformed mesh
test_mesh = mesh_to_numpy(file="test/points")
mu_tensor = torch.tensor(random_mu, dtype=torch.float32).reshape(-1, 1)

# Define the problem
problem = SupervisedProblem(input_=params, output_=vel)

# Loop over the rank values
for rank in range(1, args.pod_rank + 1):

    # Create the PODRBF model
    pod_rbf = PODRBF(pod_rank=rank, rbf_kernel="thin_plate_spline")
    pod_rbf.fit(p=params, x=vel)

    # Make the prediction for the random mu
    pred = pod_rbf(mu_tensor).detach().flatten().numpy()

    # Plot the predicted velocity magnitude for the random mu
    prediction_img = f"test/img/predicted_velocity_rank{rank}.png"
    plot_test(vel=pred, pts=test_mesh, file=prediction_img)

    # Save results to a file (param and velocity magnitude)
    filename = f"test/pod_results_rank{rank}.npz"
    np.savez(file=filename, param=mu_tensor.numpy(), velocity=pred)
