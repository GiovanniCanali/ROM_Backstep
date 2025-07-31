from pina.model.block import PODBlock
from matplotlib import pyplot as plt
import numpy as np
import torch
import math
import os


def plot_mesh(pts, clr="blue", title="Mesh", file="mesh.png"):
    """
    Plot the mesh.

    :param np.ndarray pts: Mesh points as a NumPy array.
    :param str clr: Color for the mesh points.
    :param str title: Title of the plot.
    :param str file: Name of the file to save the plot.
    """
    # Get the floor of the max y-coordinate for y-ticks
    max_y = math.floor(np.max(pts[:, 1]))

    # Plot
    plt.figure(figsize=(12, 8))
    plt.title(title)
    plt.plot(pts[:, 0], pts[:, 1], "o", markersize=0.5, color=clr)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.xticks(np.arange(0, 23, 2))
    plt.yticks(np.arange(0, max_y + 1, 1))
    plt.grid()
    plt.show()
    plt.savefig(file)


def plot_singular_values(vel, pts):
    """
    Compute and plot the singular values of the velocity magnitudes.

    :param torch.Tensor vel: Velocity magnitudes tensor.
    :param np.ndarray pts: Mesh points as a NumPy array.
    """
    # Initialize the POD block and fit it to the velocity magnitudes
    pod = PODBlock(vel.shape[0])
    pod.fit(vel)

    # Compute the normalized singular values
    singular_values = pod.singular_values
    normalized_singular_values = singular_values / torch.max(singular_values)

    # Create the directory for saving the plot
    img_dir = "/scratch/gcanali/ROM/img"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # Plot the singular values
    plt.semilogy(normalized_singular_values, marker="o")
    plt.grid()
    plt.xlabel("Latent dimension")
    plt.ylabel("Singular value")
    plt.savefig(f"{img_dir}/singular_values.png")

    # Compute the POD modes
    modes = pod.basis.detach().cpu().numpy()

    # Plotting loop for the POD modes
    for i, mode in enumerate(modes):
        plt.figure(figsize=(8, 6))
        plt.scatter(pts[:, 0], pts[:, 1], c=mode, cmap="coolwarm", s=1)
        plt.colorbar()
        plt.title(f"POD Mode {i+1}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")
        plt.tight_layout()
        plt.savefig(f"{img_dir}/pod_mode_{i+1}.png")


def plot_test(vel, pts, file):
    """
    Plot the predicted velocity magnitude for the random mu.

    :param torch.Tensor vel: Predicted velocity magnitudes.
    :param np.ndarray pts: Mesh points as a NumPy array.
    :param str file: Path to save the plot.
    """
    plt.figure(figsize=(8, 6))
    plt.scatter(pts[:, 0], pts[:, 1], c=vel, cmap="coolwarm", s=1)
    plt.colorbar()
    plt.title("Predicted Velocity Magnitude")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(file)
