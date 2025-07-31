import torch
from pina.model.block import PODBlock, RBFBlock


class PODRBF(torch.nn.Module):
    """
    Definition of the POD-RBF model that combines POD and RBF blocks.
    """

    def __init__(self, pod_rank, rbf_kernel):
        """
        Initialization of the POD-RBF model.
        """
        super().__init__()
        self.pod = PODBlock(pod_rank)
        self.rbf = RBFBlock(kernel=rbf_kernel)

    def forward(self, x):
        """
        Forward pass of the POD-RBF model.
        """
        coefficients = self.rbf(x)
        return self.pod.expand(coefficients)

    def fit(self, p, x):
        """
        Fit the POD-RBF model to the training data.
        """
        self.pod.fit(x)
        self.rbf.fit(p, self.pod.reduce(x))
