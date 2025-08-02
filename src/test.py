from matplotlib import pyplot as plt
import numpy as np
import argparse
from utils import (
    get_test_data,
    relative_error,
    split_by_label,
    mean_squared_error,
)


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--pod_rank", type=int, default=10)
args = parser.parse_args()

# Initialize lists to store errors
error_pod = []
error_pygem = []
mse_pod = []
mse_pygem = []

# Define the range of POD ranks to test
ranks = list(range(1, args.pod_rank + 1))

# Loop over the rank values
for rank in ranks:

    # Load PODRBF simulation
    v_pod = np.load(file=f"test/pod_results_rank{rank}.npz")["velocity"]

    # Load test data
    v_foam, v_pygem, mesh_foam, mesh_pygem = split_by_label(*get_test_data())

    # Compute relative errors
    rel_error_pygem, rel_error_pod = relative_error(
        vel_foam=v_foam, vel_pygem=v_pygem, vel_pod=v_pod
    )

    # Compute mean squared errors
    mse_pygem_i, mse_pod_i = mean_squared_error(
        vel_foam=v_foam, vel_pygem=v_pygem, vel_pod=v_pod
    )

    # Store the errors
    error_pod.append(rel_error_pod)
    error_pygem.append(rel_error_pygem)

    # Store the mean squared errors
    mse_pod.append(mse_pod_i)
    mse_pygem.append(mse_pygem_i)

# Plot the relative errors
plt.figure(figsize=(10, 6))
plt.semilogy(ranks, error_pod, label="POD error", c="r", marker="o")
plt.semilogy(ranks, error_pygem, label="Pygem error", c="b")
plt.title("Relative error of POD-RBF and Pygem")
plt.xlabel("POD rank")
plt.ylabel("Relative error")
plt.legend()
plt.grid()
plt.savefig("test/img/relative_error.png")

# Plot the mean squared errors
plt.figure(figsize=(10, 6))
plt.semilogy(ranks, mse_pod, label="POD MSE", c="r", marker="o")
plt.semilogy(ranks, mse_pygem, label="Pygem MSE", c="b")
plt.title("MSE of POD-RBF and Pygem")
plt.xlabel("POD rank")
plt.ylabel("MSE")
plt.legend()
plt.grid()
plt.savefig("test/img/mse.png")

# Print the errors
print("Errors:")
for rank, err_pod, err_pygem, msepod, msepygem in zip(
    ranks, error_pod, error_pygem, mse_pod, mse_pygem
):
    print(f"Rank {rank}:")
    print(f"    Relative error: POD = {err_pod:.2e}, Pygem = {err_pygem:.2e}")
    print(f"    MSE: POD = {msepod:.2e}, Pygem = {msepygem:.2e}\n")
