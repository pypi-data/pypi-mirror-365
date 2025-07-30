#generator.py
import torch
import torch.nn as nn


# ======== ResNet Block =========
class ResnetBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1),
            nn.Conv2d(dim, dim, kernel_size=3, stride=1, padding=0),
            nn.InstanceNorm2d(dim, affine=True),
            nn.ReLU(inplace=False),

            nn.ReflectionPad2d(1),
            nn.Conv2d(dim, dim, kernel_size=3, stride=1, padding=0),
            nn.InstanceNorm2d(dim, affine=True),
        )
    
    
    def forward(self, x):
        residual = x
        out = x
        for i, layer in enumerate(self.block):
            try:
                out = layer(out)
            except Exception as e:
                print(f"\n❌ Error in ResnetBlock at layer {i}: {layer}\n")
                raise
        return residual + out  # Safe residual connection



# ======== ResNet Generator =========
class ResnetGenerator(nn.Module):
    def __init__(self, input_nc=3, output_nc=3, ngf=64, n_blocks=9):
        """
        Args:
            input_nc: Number of input channels (3 for RGB images)
            output_nc: Number of output channels
            ngf: Number of filters in the first conv layer
            n_blocks: Number of ResNet blocks (9 used in CycleGAN paper)
        
        Implements the transformation from modern to vintage image.
        Structure: encoder (compress to latent space) → resnet → decoder → output layer
        """
        super().__init__()

        # Initial convolution
        model = [
            nn.ReflectionPad2d(3),
            nn.Conv2d(input_nc, ngf, kernel_size=7, padding=0),
            nn.InstanceNorm2d(ngf, affine=True),
            nn.ReLU(inplace=False)
        ]

        # Downsampling ×2
        in_features = ngf
        out_features = ngf * 2
        for _ in range(2):
            model += [
                nn.Conv2d(in_features, out_features, kernel_size=3, stride=2, padding=1),
                nn.InstanceNorm2d(out_features, affine=True),
                nn.ReLU(inplace=False)
            ]
            in_features = out_features
            out_features = in_features * 2

        # Residual blocks to learn "delta_x"
        for _ in range(n_blocks):
            model += [ResnetBlock(in_features)]

        # Upsampling ×2
        out_features = in_features // 2
        for _ in range(2):
            model += [
                nn.ConvTranspose2d(in_features, out_features, kernel_size=3, stride=2, padding=1, output_padding=1),
                nn.InstanceNorm2d(out_features, affine=True),
                nn.ReLU(inplace=False)
            ]
            in_features = out_features
            out_features = in_features // 2

        # Output layer
        model += [
            nn.ReflectionPad2d(3),
            nn.Conv2d(ngf, output_nc, kernel_size=7, padding=0),
            nn.Tanh()
        ]

        self.model = nn.Sequential(*model)

    def forward(self, x):
        return self.model(x)
    
