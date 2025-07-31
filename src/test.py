from utils import get_test_data, relative_error, split_by_label
import numpy as np

# Load PODRBF simulation
vel_pod = np.load(file="test/pod_results.npz")["velocity"]

# Load test data
vel_foam, vel_pygem, mesh_foam, mesh_pygem = split_by_label(*get_test_data())

# Compute relative errors
rel_error_pygem, rel_error_pod = relative_error(
    vel_foam=vel_foam, vel_pygem=vel_pygem, vel_pod=vel_pod
)

# Print the mean of relative errors
print(f"\nMean Relative Error (PyGeM vs Foam): {rel_error_pygem.mean()}")
print(f"Mean Relative Error (POD vs Foam): {rel_error_pod.mean()}")
