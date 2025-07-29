import argparse
import os

import numpy as np
import scipy.io as sio
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau

from yms_zsl.models.HSAZLM import FCNN, LSELoss
from yms_zsl.tools.dataset import create_dataloaders
from yms_zsl.tools.plotting import plot_metrics
from yms_zsl.tools.tool import initialize_results_file, append_to_results_file
from yms_zsl.tools.train_eval_utils import train_fcnn_one_epoch


def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = args.output_dir
    vis_dir = os.path.join(output_dir, 'images')
    print("Using {} device training.".format(device.type))
    results_file = os.path.join(output_dir, 'fcnn_results.txt')
    column_order = ['epoch', 'train_losses', 'val_losses', 'lrs']
    custom_column_widths = {'epoch': 5, 'train_loss': 12, 'val_loss': 10, 'lr': 3}
    initialize_results_file(results_file, column_order)

    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size)

    mat_data = sio.loadmat(args.hsa_path)
    hsa_matrix = mat_data.get('HSA')
    hsa_matrix = torch.tensor(hsa_matrix)

    # feature_extractor = create_feature_extractor(args.feature_path).to(device)
    feature_extractor = torch.load(args.feature_path, map_location='cpu', weights_only=False).to(device)
    fcnn = FCNN(args.fcnn_channels).to(device)
    optimizer = torch.optim.Adam(fcnn.parameters(), lr=args.lr)
    scheduler = ReduceLROnPlateau(optimizer, factor=0.1, min_lr=1e-10, patience=10)
    criterion = LSELoss(hsa_matrix).to(device)
    train_losses = []
    val_losses = []
    best_loss = np.inf

    for epoch in range(args.epochs):
        result = train_fcnn_one_epoch(
            cnn=feature_extractor, fcnn=fcnn, optimizer=optimizer, train_loader=train_loader,
            val_loader=val_loader, device=device, criterion=criterion, epoch=epoch
        )
        lr = scheduler.get_last_lr()[0]
        result.update({'lr': lr})
        scheduler.step(result['val_loss'])
        train_losses.append(result['train_loss'])
        val_losses.append(result['val_loss'])
        append_to_results_file(results_file, result, column_order, custom_column_widths=custom_column_widths)

        torch.save(fcnn, os.path.join(output_dir, 'models', f'last_fcnn.pt'))
        if result['val_loss'] < best_loss:
            best_loss = result['val_loss']
            best = os.path.join(output_dir, 'models', f'best_fcnn.pt')
            torch.save(fcnn, best)

    plot_metrics(train_losses, val_losses, args.epochs, name='FCNN Loss',
                 save_path=os.path.join(vis_dir, 'fcnn_loss.png'))
    os.remove(os.path.join(output_dir, 'models', f'last_fcnn.pt'))


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--epochs', type=int, default=500)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--fcnn_channels', type=int, default=518)
    parser.add_argument('--data_dir', default=r'/data/coding/data/D0')
    parser.add_argument('--output_dir', default='/data/coding/results/train_D0')
    parser.add_argument('--feature_path', default=r'/data/coding/results/train_D0/models/feature_extractor.pt')
    parser.add_argument('--hsa_path', default=r'/data/coding/results/train_D0/HSA.mat')
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    main(opt)
