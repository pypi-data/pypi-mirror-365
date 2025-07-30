#bind_dataset.py Combine two .pt domains into unpaired dataset
from torch.utils.data import Dataset
from pathlib import Path
import torch
import random

class UnpairedPTDataset(Dataset):
    def __init__(self, domain_A_dir, domain_B_dir):
        """
        Load .pt tensor files to construct an unpaired image pair dataset.

        Args:
            domain_A_dir (str): Directory path for modern image .pt files
            domain_B_dir (str): Directory path for vintage image .pt files
        """
        self.data_A = sorted(Path(domain_A_dir).rglob("*.pt"))
        self.data_B = sorted(Path(domain_B_dir).rglob("*.pt"))
        self.len_A = len(self.data_A)
        self.len_B = len(self.data_B)
        assert self.len_A > 0 and self.len_B > 0, "Dataset is empty"

    def __len__(self):
        return max(self.len_A, self.len_B)

    def __getitem__(self, idx):
        path_A = self.data_A[idx % self.len_A]
        path_B = self.data_B[random.randint(0, self.len_B - 1)]

        tensor_A = torch.load(path_A)  # [3, H, W]
        tensor_B = torch.load(path_B)

        return {"A": tensor_A, "B": tensor_B}
