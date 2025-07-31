from utils import get_mu, change_vertices


# Modify the blockMeshDict file with the mu parameter
change_vertices(file="test/foam_grid/system/blockMeshDict", mu=get_mu())