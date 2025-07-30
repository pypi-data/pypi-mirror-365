#discriminator.py
import torch
import torch.nn as nn

class Discriminator(nn.Module):
    def __init__(self, input_nc=3, ndf=64):
        """
        Args:
            input_nc: Number of input channels (3 for RGB images)
            ndf: Number of filters in the first conv layer

        The discriminator is relatively simple. It only needs to judge and output a probability,
        which is a classification task implemented with CNN.
        """
        super().__init__()
        
        model=[
            # First conv layer
            nn.Conv2d(input_nc,ndf,kernel_size=4,stride=2,padding=1),
            nn.LeakyReLU(0.2,inplace=False),

            # Second conv layer
            nn.Conv2d(ndf,ndf*2,kernel_size=4,stride=2,padding=1),
            nn.InstanceNorm2d(ndf*2, affine=True),
            nn.LeakyReLU(0.2,inplace=False),

            # Third conv layer
            nn.Conv2d(ndf*2,ndf*4,kernel_size=4,stride=2,padding=1),
            nn.InstanceNorm2d(ndf*4, affine=True),
            nn.LeakyReLU(0.2,inplace=False),

            # Fourth conv layer
            nn.Conv2d(ndf * 4, ndf * 8, kernel_size=4, stride=2, padding=1),
            nn.InstanceNorm2d(ndf * 8, affine=True),
            nn.LeakyReLU(0.2, inplace=False),

            # Output layer
            nn.Conv2d(ndf*8,1,kernel_size=4,stride=1,padding=1),
            nn.Sigmoid() # Output probability between [0,1]
        ]

        self.model = nn.Sequential(*model)
    
    
    def forward(self, x):
        for i, layer in enumerate(self.model):
            x = layer(x)
            x = x.clone()  # Avoid view/inplace issues
        return x
