#!/bin/bash

# Capture the first argument as the number of deformations
N_VALUES=${1:-10}

# Move into the newly created/copied directory
cd reference_simulation

# Copy 0.orig to 0
if [ -e "0.orig" ]; then
    cp -r 0.orig 0
else
    echo "Error: 0.orig does not exist in reference_simulation directory."
    exit 1
fi

# Generate the mesh using blockMesh
echo -n "Running blockMesh..."
blockMesh > /dev/null 2>&1
echo " done."

# Setup the simulation directories
echo -n "Setting up simulation directories..."
cd ..
python src/deformation.py --n_values "$N_VALUES"
echo " done."

# Run the simulations
echo "Running the simulations:"

# Loop through all directories matching the pattern
for sim_dir in "openfoam_simulations"/simulation_mu_*; do
    
    if [ -d "$sim_dir" ]; then
        cd "$sim_dir" || { echo "Failed to enter $sim_dir"; exit 1; }

        touch case.foam
        echo -n "    Running simpleFoam in $sim_dir..."
        simpleFoam > /dev/null 2>&1
        echo " done."

        echo -n "    Converting results to VTK format in $sim_dir..."
        foamToVTK -latestTime > /dev/null 2>&1
        echo " done."

        cd - > /dev/null
    fi
done

# Print completion message
echo
echo "Setup completed successfully."

# Clean up
rm -rf src/utils/__pycache__
