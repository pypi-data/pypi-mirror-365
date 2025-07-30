# optimize_loss.py
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import chain

class optimize_loss(nn.Module):
    """
    Only retains three interfaces:
        __init__         —— Initialize networks, loss functions, and optimizers
        _disc_loss()     —— Discriminator adversarial loss
        update_parameters() —— One complete parameter update (D first, then G)
    """
    def __init__(self, G_A2B, G_B2A, D_A, D_B,
                 lr=2e-4, betas=(0.5, 0.999)):
        super().__init__()

        # Networks
        self.G_A2B, self.G_B2A = G_A2B, G_B2A
        self.D_A,   self.D_B   = D_A,   D_B

        # Loss functions
        self.adv_loss   = nn.MSELoss()
        self.cycle_loss = nn.L1Loss()
        self.idt_loss   = nn.L1Loss()

        # Optimizers
        self.G_opt = optim.Adam(
            chain(G_A2B.parameters(), G_B2A.parameters()),
            lr=lr, betas=betas
        )
        self.D_A_opt = optim.Adam(D_A.parameters(), lr=lr, betas=betas)
        self.D_B_opt = optim.Adam(D_B.parameters(), lr=lr, betas=betas)

    # ---------- helpers ----------------------------------------------------
    def _disc_loss(self, D, real, fake):
        """0.5·[MSE(D(real),1)+MSE(D(fake),0)]"""
        pred_real = D(real)
        pred_fake = D(fake.detach())
        return 0.5 * (
            self.adv_loss(pred_real, torch.ones_like(pred_real)) +
            self.adv_loss(pred_fake, torch.zeros_like(pred_fake))
        )

    # ---------- main training step ----------------------------------------
    def update_parameters(self, real_A, real_B):
        """Single step: update D_A → D_B → freeze discriminators → update generators"""
        # 1) Generate fake images
        fake_B = self.G_A2B(real_A)  # A→B
        fake_A = self.G_B2A(real_B)  # B→A

        # 2) -------- Discriminator ----------
        D_A_loss = self._disc_loss(self.D_A, real_A, fake_A)
        D_B_loss = self._disc_loss(self.D_B, real_B, fake_B)

        self.D_A_opt.zero_grad()
        D_A_loss.backward()
        self.D_A_opt.step()

        self.D_B_opt.zero_grad()
        D_B_loss.backward()
        self.D_B_opt.step()

        # 3) -------- Generator ----------
        # (a) Temporarily freeze discriminators to avoid backprop through them
        for p in chain(self.D_A.parameters(), self.D_B.parameters()):
            p.requires_grad_(False)

        # (b) Forward pass again using updated discriminator weights
        fake_B = self.G_A2B(real_A)
        fake_A = self.G_B2A(real_B)

        #    • Adversarial loss (ensure label and pred shapes match to avoid errors)
        pred_fake_B = self.D_B(fake_B)
        pred_fake_A = self.D_A(fake_A)

        G_adv = 0.5 * (
            self.adv_loss(pred_fake_B, torch.ones_like(pred_fake_B)) +
            self.adv_loss(pred_fake_A, torch.ones_like(pred_fake_A))
        )

        #    • Cycle-consistency
        cycle_A = self.cycle_loss(self.G_B2A(fake_B), real_A)
        cycle_B = self.cycle_loss(self.G_A2B(fake_A), real_B)

        #    • Identity
        idt_A = self.idt_loss(self.G_B2A(real_B), real_B)
        idt_B = self.idt_loss(self.G_A2B(real_A), real_A)

        G_loss = (
            G_adv +
            10.0 * (cycle_A + cycle_B) +
            5.0  * (idt_A + idt_B)
        )

        self.G_opt.zero_grad()
        G_loss.backward()
        self.G_opt.step()

        # (c) Unfreeze discriminators
        for p in chain(self.D_A.parameters(), self.D_B.parameters()):
            p.requires_grad_(True)

        # 4) Logging
        return (
            D_A_loss.item(),
            D_B_loss.item(),
            G_loss.item()
        )
