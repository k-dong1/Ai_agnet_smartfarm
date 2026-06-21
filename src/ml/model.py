import torch
import torch.nn as nn

class SmartFarmMLP(nn.Module):
    def __init__(self, input_dim: int, hidden1: int = 16, hidden2: int = 8, output_dim: int = 4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden1),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(hidden2, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)
