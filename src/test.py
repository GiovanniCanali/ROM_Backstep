from utils import get_test_data, relative_error, split_by_label
from matplotlib import pyplot as plt
import numpy as np
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--pod_rank", type=int, default=10)
args = parser.parse_args()

error_pod = []
error_pygem = []
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

    # Store the errors
    error_pod.append(rel_error_pod)
    error_pygem.append(rel_error_pygem)

# Plot the relative errors
plt.figure(figsize=(10, 6))
plt.semilogy(ranks, error_pod, label="POD-RBF error", c="r", marker="o")
plt.semilogy(ranks, error_pygem, label="Pygem error", c="b")
plt.title("Relative Errors of POD-RBF and Pygem")
plt.xlabel("POD rank")
plt.ylabel("Relative error")
plt.legend()
plt.grid()
plt.savefig("test/img/relative_error.png")
