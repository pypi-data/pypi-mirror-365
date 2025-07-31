
# convolutional-autoencoder-pytorch

A minimal, customizable PyTorch package for building and training convolutional autoencoders based on a simplified U-Net architecture (without skip connections). Ideal for representation learning, image compression, and reconstruction tasks.

## 🔧 Features

- 📦 Modular architecture (`Encoder`, `Decoder`, `AutoEncoder`)
- 🔁 Symmetric U-Net-like design without skip connections
- ⚡ Tanh output activation for stable image reconstruction
- 🧠 Residual blocks with RMS normalization and SiLU activation
- 📱 Designed for image inputs (`3×H×W`) with configurable channels and latent dim
- 🧪 Works with batched input tensors (e.g., `torch.Tensor[B, C, H, W]`)

## 📦 Installation

```bash
pip install convolutional-autoencoder-pytorch

```

## 🧩 Package Structure

```bash
convolutional-autoencoder-pytorch/
├── convolutional_autoencoder_pytorch/
│   ├── __init__.py
│   └── module.py          # All architecture classes and logic
├── pyproject.toml
├── LICENSE
└── README.md

```

## 🚀 Quick Start

### 1. Import the package and create the model

```python
import torch
from convolutional_autoencoder_pytorch import AutoEncoder

model = AutoEncoder(
    dim=64,
    dim_mults=(1, 2, 4, 8),
    dim_latent=128,
    image_channels=3
)

```

### 2. Forward pass and reconstruction

```python
images = torch.randn(8, 3, 128, 128)  # batch of images
reconstructed, latent = model(images)

# Or just get the reconstruction
recon = model.reconstruct(images)

```

### 3. Training step (sample loop)

```python
import torch.nn.functional as F
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

def train_step(images):
    model.train()
    optimizer.zero_grad()
    recon, _ = model(images)
    loss = F.mse_loss(recon, images)
    loss.backward()
    optimizer.step()
    return loss.item()

```

## ⚙️ Configuration Options

| Parameter | Description | Default |
|--|--|--|
| `dim` | Base channel size | `64` |
| `dim_mults` | List of multipliers for down/up blocks | `(1, 2, 4, 8)` |
| `dim_latent` | Latent bottleneck dimension | `64` |
| `image_channels` | Input/output image channels (e.g., 3) | `3` |
| `dropout` | Dropout probability | `0.0` |

## 🙋‍♂️ Author

Developed by [Mehran Bazrafkan](mailto:mhrn.bzrafkn.dev@gmail.com)
This project is an original implementation of a simplified autoencoder architecture. Some ideas and design inspirations were drawn from the open-source [`denoising-diffusion-pytorch`](https://github.com/lucidrains/denoising-diffusion-pytorch) project by Phil Wang, but the code and architecture were written independently.

## 📢 Contributions & Feedback

Contributions, issues, and feedback are welcome via [GitHub Issues](https://github.com/MehranBazrafkan/convolutional-autoencoder-pytorch/issues).

## 📄 License

This project is licensed under the terms of the [MIT LICENSE](https://github.com/MehranBazrafkan/convolutional-autoencoder-pytorch/blob/main/LICENSE).
