# ROM_Backstep

This repository contains the source code for the final project of the course 
_Computational Mechanics by ROM_, held at SISSA during the academic year
2024 - 2025.

## Description

This project focuses on building a reduced-order model (ROM) for simulating 2D
incompressible, steady, laminar flow past a backward-facing step. The geometry
is parameterized by smoothly deforming the inlet height using one scalar
parameter sampled from the range [−1,1]. These deformations produce variations
of the original domain, with inlet heights ranging between 2 and 4.

High-fidelity simulations are run using OpenFOAM for a set of training
geometries. Proper Orthogonal Decomposition (POD) is used to extract a reduced
basis from the simulation data, and Radial Basis Function (RBF) interpolation is
employed to predict flow fields for new, unseen parameter values. The ROM is
then tested by comparing its predictions with full-order simulations.

## Dependencies

This project requires the following software to be installed:

- **OpenFOAM 2112**: Used for full-order fluid flow simulations. Please ensure
this specific version is installed and properly configured on your system.


## Setup Instructions
Follow these steps to set up the environment:

1. **Clone the repository and navigate into it:**

```bash
git clone https://github.com/GiovanniCanali/ROM_Backstep.git
cd ROM_Backstep
```

2. **Create a Conda environment with Python 3.12:**

```bash
conda create --name rom python=3.12 -y
```

3. **Activate the environment:**

```bash
conda activate rom
```

4. **Install the package:**

```bash
python -m pip install .
```

## Running the Pipeline

Two scripts are provided to run the full ROM workflow. Each accepts a
command-line argument:

- **`run_setup.sh <N>`**

  Generates the training dataset by sampling `N` random deformation
  parameters. For each parameter, the inlet geometry is smoothly deformed, a
  corresponding mesh is generated, and a full-order simulation is performed
  using OpenFOAM.

  **Example:**
  ```bash
  ./run_setup.sh 10
  ```
  This runs simulations on 10 deformed geometries.


- **`run_test.sh <r>`**

  Tests the reduced-order model using a newly sampled deformation parameter and
  a POD basis of rank `r`. The script runs a high-fidelity OpenFOAM simulation
  as ground truth, predicts the corresponding flow field using the POD-RBF
  model, and computes the error between the ROM prediction and the full-order
  solution.
  
  **Example:**
  ```bash
  ./run_test.sh 5
  ```
  This evaluates the ROM using a POD basis of rank 5.