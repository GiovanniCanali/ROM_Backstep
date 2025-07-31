#!/bin/bash

# Capture the first argument as the pod rank
POD_RANK=${1:-10}

# Run the POD analysis
echo -n "Running the POD analysis..."
python src/pod.py --pod_rank "$POD_RANK"
echo " done."

# Create the test_simulations directory
echo -n "Setting up simulations directories..."
cp -r reference_simulation test/foam_grid
cp -r reference_simulation test/pygem_grid
echo " done."

# Modify the vertices in the blockMeshDict for the foam_grid
echo -n "Modifying vertices in blockMeshDict for foam_grid..."
python src/modify_blockMeshDict.py
echo " done."

# Run blockMesh in the two subdirectories
echo -n "Running blockMesh in foam_grid and pygem_grid..."
cd test/foam_grid
blockMesh > /dev/null 2>&1
cd - > /dev/null
cd test/pygem_grid
blockMesh > /dev/null 2>&1
cd - > /dev/null
echo " done."

# Copy points from test/points to pygem_grid/constant/polyMesh/points
echo -n "Copying deformed points to pygem_grid..."
cp test/points test/pygem_grid/constant/polyMesh/points
echo " done."

# Run the tests
echo "Running the tests:"

# Loop through all directories matching the pattern
for test_dir in test/*_grid; do

    if [ -d "$test_dir" ]; then
        cd "$test_dir" || { echo "Failed to enter $test_dir"; exit 1; }

        touch case.foam
        echo -n "    Running simpleFoam in $test_dir..."
        simpleFoam > /dev/null 2>&1
        echo " done."

        echo -n "    Converting results to VTK format in $test_dir..."
        foamToVTK -latestTime > /dev/null 2>&1
        echo " done."

        cd - > /dev/null
    fi
done

# Run the test script
echo -n "Running the test script..."
python src/test.py
echo " done."

# Print completion message
echo
echo "All tests completed successfully."

# Clean up
rm -rf src/utils/__pycache__ src/model/__pycache__
