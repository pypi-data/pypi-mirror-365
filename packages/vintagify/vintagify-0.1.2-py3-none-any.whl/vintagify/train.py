#train.py
import torch
from torch.utils.data import DataLoader
from torch.nn import DataParallel
import os
from .bind_dataset import UnpairedPTDataset
from .optimize_loss import optimize_loss
from .generator import ResnetGenerator
from .discriminator import Discriminator

def train(
        domain_A_path,
        domain_B_path,
        epochs=100,
        batch_size=4,
        image_size=512,
        lr=0.0002,
        save_dir="checkpoints"
):
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device:{device}")

    torch.autograd.set_detect_anomaly(True)  # ← ✅ Enable anomaly detection here!

    
    # Each dataset sample consists of a pair of images as one tensor
    dataset = UnpairedPTDataset(domain_A_path, domain_B_path)
    # dataloader: batching, shuffling, multithreaded loading, tensor conversion
    # dataloader combines 4 samples into one batch
    dataloader=DataLoader(dataset,batch_size=batch_size,shuffle=True,drop_last=True)

    G_A2B=ResnetGenerator()
    G_B2A=ResnetGenerator()
    D_A=Discriminator()
    D_B=Discriminator()

    
    G_A2B.to(device)
    G_B2A.to(device)
    D_A.to(device)  
    D_B.to(device)

    loss_module=optimize_loss(G_A2B,G_B2A,D_A,D_B,lr=lr)

    os.makedirs(save_dir,exist_ok=True)

    # ==== Checkpoint recovery ====
    start_epoch = 1
    latest_epoch = 0
    for epoch_file in os.listdir(save_dir):
        if epoch_file.startswith("G_A2B_epoch") and epoch_file.endswith(".pth"):
            num = int(epoch_file.split("_epoch")[1].split(".")[0])
            latest_epoch = max(latest_epoch, num)
    
    if latest_epoch > 0:
        print(f"🔄 Resuming training from epoch {latest_epoch + 1}")
        G_A2B.load_state_dict(torch.load(f"{save_dir}/G_A2B_epoch{latest_epoch}.pth"))
        G_B2A.load_state_dict(torch.load(f"{save_dir}/G_B2A_epoch{latest_epoch}.pth"))
        D_A.load_state_dict(torch.load(f"{save_dir}/D_A_epoch{latest_epoch}.pth"))
        D_B.load_state_dict(torch.load(f"{save_dir}/D_B_epoch{latest_epoch}.pth"))
        start_epoch = latest_epoch + 1
    else:
        print("🚀 Starting training from scratch")

    for epoch in range(start_epoch, epochs + 1):
        for i,batch in enumerate(dataloader):
            real_A=batch["A"].to(device)
            real_B=batch["B"].to(device)

            fake_B=G_A2B(real_A)
            fake_A=G_B2A(real_B)


            result = loss_module.update_parameters(real_A, real_B)
            if result is None:
                print("⚠️ Skipping this batch due to backward error")
                continue
            
            D_A_loss, D_B_loss, G_loss = result
            if i % 10 == 0:
                print(f"[Epoch {epoch}/{epochs}] [Batch {i}/{len(dataloader)}] "
                      f"D_A: {D_A_loss:.4f}, D_B: {D_B_loss:.4f}, G: {G_loss:.4f}")
        torch.save(G_A2B.state_dict(),f"{save_dir}/G_A2B_epoch{epoch}.pth")
        torch.save(G_B2A.state_dict(),f"{save_dir}/G_B2A_epoch{epoch}.pth")
        torch.save(D_A.state_dict(),f"{save_dir}/D_A_epoch{epoch}.pth")
        torch.save(D_B.state_dict(),f"{save_dir}/D_B_epoch{epoch}.pth")
