import argparse
import os

import torch
from torch.nn import MSELoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import transforms

from yms_zsl.models.CAE import ConvResidualAE
from yms_zsl.models.HSAZLM import DRCAE
from yms_zsl.tools.dataset import create_dataloaders
from yms_zsl.tools.plotting import visualize_features
from yms_zsl.tools.tool import make_save_dirs, get_device, create_csv, \
    append_metrics_to_csv, generate_image_dataframe
from yms_zsl.tools.train_eval_utils import train_decae_one_epoch, extract_image_features


def main(args, run=None):
    save_dir = args.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)

    results_file = os.path.join(save_dir, 'results.csv')
    create_csv(['epoch', 'train_loss', 'val_loss', 'lr'], results_file)
    device = get_device()
    print("Using {} device training.".format(device.type))

    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor()])

    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size, transform=transform)
    # metrics = {'train_losses': [], 'val_losses': [], 'lrs': []}

    model = ConvResidualAE().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=4, min_lr=1e-9)
    criterion = MSELoss()
    best = 1e8
    last_model_path = os.path.join(model_dir, 'last_decae.pt')
    best_model_path = os.path.join(model_dir, 'best_decae.pt')
    for epoch in range(0, args.epochs):
        result = train_decae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch)
        lr = lr_scheduler.get_last_lr()[0]
        lr_scheduler.step(result['val_loss'])

        # metrics['val_losses'].append(result['val_loss'])
        # metrics['train_losses'].append(result['train_loss'])
        # metrics['lrs'].append(lr)
        result.update({'lr': lr})
        append_metrics_to_csv(result, results_file)
        if run is not None:
            run.log({'decae': result})

        save_file = {
            'epoch': epoch,
            'model': model,
            'optimizer': optimizer,
            'lr_scheduler': lr_scheduler,
        }
        torch.save(save_file, last_model_path)
        if result['val_loss'] < best:
            best = result['val_loss']
            model.save(best_model_path)

    os.remove(last_model_path)

    img_path = os.path.join(args.save_dir, 'img_path.csv')
    img_path_df = generate_image_dataframe(args.data_dir, 'val')
    img_path_df.to_csv(img_path, index=False)
    features_path = os.path.join(args.save_dir, 'features.npy')
    extract_image_features(best_model_path, device, img_path, features_path, transform)
    visualize_features(features_path, img_path, save_fig_path=os.path.join(img_dir, 'test.jpg'),
                       save_html_path=os.path.join(img_dir, 'test.html'))

    return run


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\0HP\data')
    parser.add_argument('--save_dir', type=str, default='output1')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--batch_size', type=int, default=64)
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = parse_args()
    print(opts)
    main(opts)
