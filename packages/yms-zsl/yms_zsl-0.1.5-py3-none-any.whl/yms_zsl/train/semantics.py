import argparse
import os
import sys
from collections import defaultdict

import numpy as np
import torch
from scipy.io import savemat
from tqdm import tqdm

from yms_zsl.models.HSAZLM import Encoder
from yms_zsl.tools.dataset import create_dataloaders
from yms_zsl.tools.tool import list_folders


def create_encoder(encoder_path):
    """创建并加载预训练编码器"""
    encoder = Encoder()
    encoder.load_state_dict(torch.load(encoder_path, map_location='cpu', weights_only=True))
    return encoder


def decea_extract_features(encoder, loader, device):
    """从数据集中提取特征"""
    features = defaultdict(list)
    encoder.eval()
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Extracting features", colour='blue', file=sys.stdout):
            outputs = encoder(images.to(device))
            for label, feat in zip(labels.cpu().numpy(), outputs.cpu().numpy()):
                features[int(label)].append(feat)
    return features


def cnn_extract_features(encoder, loader, device):
    """从数据集中提取特征"""
    all_features = []
    all_labels = []
    encoder.eval()
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Extracting features", colour='blue', file=sys.stdout):
            outputs = encoder(images.to(device))
            # 将特征和标签转换为 numpy 数组
            output_features = outputs.cpu().numpy()
            output_labels = labels.cpu().numpy()
            # 将特征和标签添加到对应的列表中
            all_features.extend(output_features)
            all_labels.extend(output_labels)

    return all_features, all_labels


def calculate_label_means(features_dict):
    """计算每个类别的特征均值并保持原始顺序"""
    sorted_labels = sorted(features_dict.keys())
    return np.array([np.mean(features_dict[label], axis=0) for label in sorted_labels])


def main(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 初始化数据集和数据加载器

    loader = create_dataloaders(args.data_dir, args.batch_size, subset=True)

    # 特征提取
    # encoder = create_encoder(args.encoder_path).to(device)
    encoder = torch.load(args.encoder_path, map_location='cpu', weights_only=False).to(device)
    features_dict = decea_extract_features(encoder, loader, device)
    nsa_array = calculate_label_means(features_dict)

    # 合并语义属性
    sa_matrix = np.loadtxt(args.sa_path, dtype=float)
    hsa = np.concatenate([sa_matrix, nsa_array], axis=1)

    # 保存结果
    data_name = os.path.basename(args.data_dir)
    parent_path = os.path.dirname(args.data_dir)
    dir_list = list_folders(parent_path)
    savemat(os.path.join(args.save_path, f'{data_name}-HSA.mat'), {'HSA': hsa})

    feature_extractor = torch.load(args.feature_extractor_path, map_location='cpu', weights_only=False).to(device)

    for dir_name in dir_list:
        data_path = os.path.join(parent_path, dir_name)
        train_loader, val_loader = create_dataloaders(data_path, args.batch_size)
        train_features, train_labels = cnn_extract_features(feature_extractor, train_loader, device)
        val_features, val_labels = cnn_extract_features(feature_extractor, val_loader, device)
        savemat(os.path.join(args.save_path, f'{data_name}-{dir_name}.mat'),
                {'train_features': train_features, 'train_labels': train_labels,
                 'val_features': val_features, 'val_labels': val_labels,
                 'class': train_loader.dataset.classes})


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Generate HSA matrix')
    parser.add_argument('--batch_size', type=int, default=100)
    parser.add_argument('--data_dir', default=r'/data/coding/CRWU/D0')
    parser.add_argument('--encoder_path', default='/data/coding/output/train_D0/models/decae.pt')
    parser.add_argument('--sa_path', default='/data/coding/CRWU/predicate-matrix-binary.txt')
    parser.add_argument('--save_path', default='/data/coding/output/train_D0')
    parser.add_argument('--feature_extractor_path',
                        default=r'/data/coding/output/train_D0/models/feature_extractor.pt')
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    main(opt)
