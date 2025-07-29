import argparse
import os
from pathlib import Path

import scipy.io as sio
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from yms_zsl.tools.dataset import CustomDataset
from yms_zsl.tools.plotting import plot_confusion_matrix
from yms_zsl.tools.tool import initialize_results_file, append_to_results_file, calculate_metric, list_folders
from yms_zsl.tools.train_eval_utils import cnn_predict, zlm_predict


def main(args):
    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device.".format(device.type))
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    path = Path(args.data_path)
    parent_dir = path.parent
    data_name = parent_dir.name

    results_file = os.path.join(output_dir, 'predict_results.txt')
    column_order = ['model', 'data', 'accuracy', 'precision', 'recall', 'f1-score']
    initialize_results_file(results_file, column_order)

    feature_extractor = torch.load(args.feature_path, map_location='cpu', weights_only=False).to(device)
    fcnn = torch.load(args.fcnn_path, map_location='cpu', weights_only=False).to(device)
    cnn = torch.load(args.cnn_path, map_location='cpu', weights_only=False).to(device)

    mat_data = sio.loadmat(args.hsa_path)
    hsa_matrix = mat_data.get('HSA')
    hsa_matrix = torch.tensor(hsa_matrix).float().to(device)

    data_dir = os.path.abspath(args.data_path)
    dir_list = list_folders(data_dir)
    for dir_name in dir_list:

        print(f'predict {dir_name}...')
        data_path = os.path.join(data_dir, dir_name, 'val')
        predict_data = CustomDataset(root_dir=data_path, transform=transforms.ToTensor())
        classes = predict_data.classes
        predict_loader = DataLoader(predict_data, batch_size=args.batch_size, shuffle=True)

        y_pred, y_true = cnn_predict(cnn, predict_loader, device)
        cnn_result = calculate_metric(y_true, y_pred, classes)
        cnn_result.update({'model': 'cnn', 'data': data_name})
        plot_confusion_matrix(y_true, y_pred, classes=classes, path=output_dir,
                              name=f'cnn_confusion_matrix_{data_name}.png')
        print(f'cnn Accuracy: {cnn_result["accuracy"]:.2%}, Precision: {cnn_result["precision"]:.2%}, '
              f'Recall: {cnn_result["recall"]:.2%}, F1: {cnn_result["f1-score"]:.2%}')

        y_pred, y_true = zlm_predict(feature_extractor, fcnn, predict_loader, device, hsa_matrix)
        zlm_result = calculate_metric(y_true, y_pred, classes)
        zlm_result.update({'model': 'zlm', 'data': data_name})
        print(f'ZLM Accuracy: {zlm_result["accuracy"]:.2%}, Precision: {zlm_result["precision"]:.2%}, '
              f'Recall: {zlm_result["recall"]:.2%}, F1: {zlm_result["f1-score"]:.2%}')
        plot_confusion_matrix(y_true, y_pred, classes=classes, path=output_dir,
                              name=f'zlm_confusion_matrix_{data_name}.png')

        append_to_results_file(results_file, zlm_result, column_order)
        append_to_results_file(results_file, cnn_result, column_order)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    # parser.add_argument('--fcnn-dim', type=int, default=517)
    # parser.add_argument('--cnn-dim', type=int, default=4)
    parser.add_argument('--data_path', default=r'/data/coding/data')
    parser.add_argument('--fcnn_path', default=r'/data/coding/results/train_D0/models/best_fcnn.pt')
    parser.add_argument('--hsa_path', default=r'/data/coding/results/train_D0/HSA.mat')
    parser.add_argument('--feature_path', default=r'/data/coding/results/train_D0/models/feature_extractor.pt')
    parser.add_argument('--cnn_path', default=r'/data/coding/results/train_D0/models/best_cnn.pt')
    parser.add_argument('--output_dir', default=r'/data/coding/results/train_D0/predict')
    parser.add_argument('--batch_size', type=int, default=32)
    return parser.parse_args(args if args else [])



if __name__ == '__main__':
    opt = parse_args()
    print(opt)
    # os.makedirs(opt.output_dir, exist_ok=True)
    main(opt)
