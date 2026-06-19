import torch
from torch.utils.data import Dataset
import numpy as np

class SmartFarmDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        """
        X: np.ndarray of shape (num_samples, input_dim)
        y: np.ndarray of shape (num_samples,) containing integer targets (0-3)
        """
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
