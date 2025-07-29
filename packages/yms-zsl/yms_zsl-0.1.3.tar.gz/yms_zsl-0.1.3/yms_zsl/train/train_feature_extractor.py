import argparse
import os

import torch
from torch.nn import CrossEntropyLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau

from yms_zsl.models.HSAZLM import CNN
from yms_zsl.tools.dataset import create_dataloaders
from yms_zsl.tools.plotting import plot_confusion_matrix, plot_all_metrics
from yms_zsl.tools.tool import initialize_results_file, calculate_metric, \
    append_to_results_file, make_save_dirs
from yms_zsl.tools.train_eval_utils import train_feature_extractor_one_epoch


def main(args, run=None):
    # 创建输出文件夹
    save_dir = args.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)

    # 创建结果文件
    results_file = os.path.join(save_dir, 'feature_extractor_results.txt')
    feature_extractor_column_order = ['epoch', 'train_losses', 'val_losses', 'accuracies', 'precisions', 'recalls',
                                      'f1-scores', 'lrs']
    initialize_results_file(results_file, feature_extractor_column_order)
    custom_column_widths = {'epoch': 5, 'train_loss': 12, 'val_loss': 10, 'accuracy': 10, 'precision': 9, 'recall': 7,
                            'f1-score': 8,
                            'lr': 3}

    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size)
    classes = train_loader.dataset.classes
    metrics = {'train_losses': [], 'val_losses': [], 'accuracies': [], 'precisions': [], 'recalls': [], 'f1-scores': [],
               'lrs': []}

    model = CNN(args.num_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=4, min_lr=1e-9)
    criterion = CrossEntropyLoss()
    best = -1
    for epoch in range(0, args.epochs):
        result = train_feature_extractor_one_epoch(model=model,
                                                   train_loader=train_loader,
                                                   val_loader=val_loader,
                                                   device=device,
                                                   optimizer=optimizer,
                                                   criterion=criterion,
                                                   epoch=epoch)
        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        print(metric)
        lr = lr_scheduler.get_last_lr()[0]
        lr_scheduler.step(result['val_loss'])

        metrics['train_losses'].append(result['train_loss'])
        metrics['val_losses'].append(result['val_loss'])
        metrics['accuracies'].append(metric['accuracy'])
        metrics['precisions'].append(metric['precision'])
        metrics['recalls'].append(metric['recall'])
        metrics['f1-scores'].append(metric['f1-score'])
        metrics['lrs'].append(lr)

        metric.update({'epoch': epoch, 'train_loss': result['train_loss'], 'val_loss': result['val_loss'], 'lr': lr})
        append_to_results_file(results_file, metric, feature_extractor_column_order,
                               custom_column_widths=custom_column_widths)
        if run is not None:
            run.log({'feature_extractor/': metric})

        save_file = {
            'epoch': epoch,
            'model_state_dict': model,
            'optimizer_state_dict': optimizer,
            'lr_scheduler_state_dict': lr_scheduler,
        }
        torch.save(save_file, os.path.join(model_dir, 'last_feature_extractor.pt'))
        if metric['f1-score'] > best:
            best = metric['f1-score']
            torch.save(model, os.path.join(model_dir, 'best_cnn.pt'))
            model.save(os.path.join(model_dir, 'feature_extractor.pt'))
            plot_confusion_matrix(all_labels=result['y_true'], all_predictions=result['y_pred'],
                                  classes=classes, path=img_dir, name='cnn_confusion_matrix.png')
            # plot_multi_class_curves(result['y_true'], result['y_pred'],
            #                         target_names=classes, save=img_dir)

    plot_all_metrics(metrics, args.epochs, 'cnn', img_dir)
    os.remove(os.path.join(model_dir, 'last_feature_extractor.pt'))
    return run


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default=r'/data/coding/data/D0')
    parser.add_argument('--save_dir', type=str, default=r'/data/coding/results/train_D0')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--num_classes', type=int, default=10)
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    main(opt)
