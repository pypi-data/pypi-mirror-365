import torch
import torch.nn as nn
import torch.nn.functional as F


# 定义残差块
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.res = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
        )

    def forward(self, x):
        residual = x
        out = self.res(x)
        out += residual
        return F.relu(out)


# 编码器 - 添加高斯噪声
class Encoder(nn.Module):
    def __init__(self, noise_std=0.1):
        super().__init__()
        self.noise_std = noise_std

        # 下采样路径
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),  # 64x64 -> 32x32
            nn.BatchNorm2d(32),
            nn.ReLU(),
            ResidualBlock(32)
        )  # 添加右括号

        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, stride=2, padding=1),  # 32x32 -> 16x16
            nn.BatchNorm2d(64),
            nn.ReLU(),
            ResidualBlock(64)
        )  # 添加右括号

        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=2, padding=1),  # 16x16 -> 8x8
            nn.BatchNorm2d(128),
            nn.ReLU(),
            ResidualBlock(128)
        )  # 添加右括号

        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, 3, stride=1, padding=1),  # 保持8x8
            nn.BatchNorm2d(256),
            nn.ReLU(),
            ResidualBlock(256)
        )  # 添加右括号

    def add_gaussian_noise(self, x):
        """添加高斯噪声，仅在训练时添加"""
        if self.training and self.noise_std > 0:
            noise = torch.randn_like(x) * self.noise_std
            return x + noise
        return x

    def forward(self, x):
        # 在输入层添加高斯噪声
        x = self.add_gaussian_noise(x)

        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        return x


# 解码器
class Decoder(nn.Module):
    def __init__(self):
        super().__init__()

        # 上采样路径
        self.deconv1 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 3, stride=1, padding=1),  # 保持8x8
            nn.BatchNorm2d(128),
            nn.ReLU(),
            ResidualBlock(128)
        )  # 添加右括号

        self.deconv2 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1),  # 8x8 -> 16x16
            nn.BatchNorm2d(64),
            nn.ReLU(),
            ResidualBlock(64)
        )  # 添加右括号

        self.deconv3 = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),  # 16x16 -> 32x32
            nn.BatchNorm2d(32),
            nn.ReLU(),
            ResidualBlock(32)
        )  # 添加右括号

        self.deconv4 = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),  # 32x32 -> 64x64
            nn.BatchNorm2d(16),
            nn.ReLU(),
            ResidualBlock(16)
        )  # 添加右括号

        # 最终输出层
        self.final_conv = nn.Conv2d(16, 3, kernel_size=3, padding=1)

    def forward(self, x):
        x = self.deconv1(x)
        x = self.deconv2(x)
        x = self.deconv3(x)
        x = self.deconv4(x)
        x = self.final_conv(x)
        return torch.sigmoid(x)


# 完整的自编码器模型
class ConvResidualAE(nn.Module):
    def __init__(self, noise_std=0.1):
        super().__init__()
        self.encoder = Encoder(noise_std)
        self.decoder = Decoder()

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

    def encode(self, x):
        """仅使用编码器"""
        return self.encoder(x)

    def decode(self, z):
        """仅使用解码器"""
        return self.decoder(z)

    def save(self, path):
        """保存编码器"""
        torch.save(self.encoder, path)

    def save_decoder(self, path):
        """保存解码器"""
        torch.save(self.decoder.state_dict(), path)