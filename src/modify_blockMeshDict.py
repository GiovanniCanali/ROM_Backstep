from utils import get_mu, change_vertices


# Modify the blockMeshDict file with the mu parameter
mu = get_mu(path="test/img")
change_vertices(file="test/foam_grid/system/blockMeshDict", mu=mu)
