import os
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, rcParams
from sklearn.manifold import TSNE
from sklearn.metrics import ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve
from sklearn.preprocessing import label_binarize
import seaborn as sns
import plotly.express as px


# def plot_confusion_matrix(cm, classes,
#                           save_path='confusion_matrix_D1.png',
#                           normalize=False,
#                           title='Confusion matrix',
#                           cmap=plt.cm.Blues):
#     """
#         绘制混淆矩阵的函数
#         这个函数不修改原始数据，但会返回混淆矩阵。
#         """
#     plt.figure()
#     if normalize:
#         cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#         print("Normalized confusion matrix")
#     else:
#         print('Confusion matrix, without normalization')
#
#     plt.imshow(cm, interpolation='nearest', cmap=cmap)
#     plt.title(title)
#     plt.colorbar()
#     tick_marks = np.arange(len(classes))
#     plt.xticks(tick_marks, classes, rotation=45)
#     plt.yticks(tick_marks, classes)
#
#     fmt = '.2f' if normalize else 'd'
#     # 用于判断变量normalize的值。如果normalize为True，则将格式化字符串.2f赋值给变量fmt；否则，将格式化字符串'd'赋值给变量fmt。
#     # 其中，.2f表示保留两位小数，'d'表示以十进制形式显示。
#     thresh = cm.max() / 2.
#     for i, j in np.ndindex(cm.shape):
#         plt.text(j, i, format(cm[i, j], fmt),
#                  horizontalalignment="center",
#                  color="white" if cm[i, j] > thresh else "black")
#
#     plt.tight_layout()
#     plt.ylabel('True label')
#     plt.xlabel('Predicted label')
#     plt.savefig(save_path)
#     plt.close()

def plot_confusion_matrix(all_labels,
                          all_predictions,
                          classes,
                          path,
                          name='confusion_matrix.png',
                          normalize=None,
                          cmap=plt.cm.Blues,
                          ):
    ConfusionMatrixDisplay.from_predictions(all_labels,
                                            all_predictions,
                                            display_labels=classes,
                                            cmap=cmap,
                                            normalize=normalize,
                                            xticks_rotation=45
                                            )
    plt.savefig(os.path.join(path, name))
    plt.close()


def plot_multi_class_curves(y_true, y_pred, target_names, save):
    # 将多分类标签转换为二进制标签（One - vs - Rest）
    n_classes = len(set(target_names))
    y_true_bin = label_binarize(y_true, classes=range(n_classes))
    y_pred_bin = label_binarize(y_pred, classes=range(n_classes))

    # 计算每个类别的精确率 - 召回率曲线和 AUC
    precision = dict()
    recall = dict()
    auc_scores = dict()

    for i in range(n_classes):
        precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i], y_pred_bin[:, i])
        auc_scores[i] = auc(recall[i], precision[i])

    # 绘制精确率 - 召回率曲线
    plt.figure()
    # 使用更丰富的颜色映射来应对类别数不确定的情况
    cmap = plt.get_cmap('tab10')
    for i in range(n_classes):
        color = cmap(i % 10)  # 循环使用颜色映射中的颜色
        plt.plot(recall[i], precision[i], color=color, lw=2,
                 label=f'{target_names[i]}:{auc_scores[i]:0.4f}')

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc="best")
    # 确保保存路径存在
    if not os.path.exists(save):
        os.makedirs(save)
    plt.savefig(os.path.join(save, 'precision_recall_curve.png'))
    plt.close()

    # 计算每个类别的 ROC 曲线和 AUC
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_bin[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # 绘制 ROC 曲线
    plt.figure()
    for i in range(n_classes):
        color = cmap(i % 10)  # 循环使用颜色映射中的颜色
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
                 label=f'{target_names[i]}:{roc_auc[i]:0.4f}')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="best")
    plt.savefig(os.path.join(save, 'roc_curve.png'))
    plt.close()


def plot_all_metrics(metrics_dict, num_epochs, img_name, save_path, plot_metric=False):
    """
    绘制训练指标曲线

    参数：
        metrics_dict: 包含指标数据的字典，键为指标名称，值为一个列表
        num_epochs: 训练的总轮数
        save_path: 保存图像的路径，默认为 'metrics.png'
    """
    # 检查是否存在 train_losses 和 val_losses
    has_train_loss = 'train_losses' in metrics_dict
    has_val_loss = 'val_losses' in metrics_dict

    # 获取指标名称列表，排除 'epoch'
    metric_names = [key for key in metrics_dict.keys() if key != 'epoch']

    # 如果有 train_losses 和 val_losses，添加一个特殊的键
    if has_train_loss and has_val_loss:
        metric_names.append('train_val_loss')

    # 计算子图的行数和列数，使得 m*n 最接近 metric_names 的数量
    num_metrics = len(metric_names)
    m = int(np.ceil(np.sqrt(num_metrics)))
    n = int(np.ceil(num_metrics / m))

    # 创建子图
    fig, axes = plt.subplots(m, n, figsize=(12 * n, 6 * m))
    axes = axes.flatten()  # 将二维数组的 axes 展平为一维

    # 绘制每个指标的曲线
    for i, name in enumerate(metric_names):
        ax = axes[i]

        if name == 'train_val_loss':
            # 绘制 train_losses 和 val_losses 在同一张图
            train_loss = metrics_dict['train_losses']
            val_loss = metrics_dict['val_losses']
            ax.plot(range(1, num_epochs + 1), train_loss, label='Training Loss')
            ax.plot(range(1, num_epochs + 1), val_loss, label='Validation Loss')
            ax.set_title('Loss over epochs')
        else:
            # 绘制其他指标
            metric = metrics_dict[name]
            ax.plot(range(1, num_epochs + 1), metric, label=f'{name}')
            ax.set_title(f'{name} over epochs')

        ax.set_xlabel('Epochs')
        ax.set_ylabel(f'{name}')
        ax.legend()
        ax.grid(True)

    # 删除多余的子图
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # 调整布局并保存图像
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'{img_name}_metrics.png'))
    plt.close()
    if plot_metric:
        # 为每个指标单独绘制一张图
        for name in metric_names:
            plt.figure(figsize=(12, 6))
            if name == 'train_val_loss':
                # 绘制 train_losses 和 val_losses 在同一张图
                train_loss = metrics_dict['train_losses']
                val_loss = metrics_dict['val_losses']
                plt.plot(range(1, num_epochs + 1), train_loss, label='Training Loss')
                plt.plot(range(1, num_epochs + 1), val_loss, label='Validation Loss')
                plt.title('Loss over epochs')
            else:
                # 绘制其他指标
                metric = metrics_dict[name]
                plt.plot(range(1, num_epochs + 1), metric, label=f'{name}')
                plt.title(f'{name} over epochs')

            plt.xlabel('Epochs')
            plt.ylabel(f'{name}')
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(save_path, f'{img_name}_{name}.png'))
            plt.close()


def plot_metrics(metric1, metric2, num_epochs, name, save_path='metrics.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, num_epochs + 1), metric1, label=f'Training {name}')
    plt.plot(range(1, num_epochs + 1), metric2, label=f'Validation {name}')
    plt.title(f'{name} over epochs')
    plt.xlabel('Epochs')
    plt.ylabel(f'{name}')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_single(met, num_epochs, name, save_path='metrics.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, num_epochs + 1), met)
    plt.title(f'{name} over epochs')
    plt.xlabel('Epochs')
    plt.ylabel(f'{name}')
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()


def plot_data_from_files(file_paths, exclude_headers=None, save_path='metrics.png'):
    """
    Plot data from multiple text files, excluding specified headers, with a fixed 2 rows layout.
    Use folder name as label if file names are consistent, otherwise use file name.

    Args:
    - file_paths (list): A list of file paths to read data from.
    - exclude_headers (list): A list of headers to exclude from plotting.
    """
    # 设置支持中文的字体
    rcParams['font.family'] = 'Microsoft YaHei'  # Windows系统
    # rcParams['font.family'] = 'PingFang SC'  # macOS系统
    rcParams['axes.unicode_minus'] = False  # 正确显示负号
    if exclude_headers is None:
        exclude_headers = ['epoch', 'lr']  # 默认排除的头部

    # 初始化一个列表来存储所有数据
    all_data = []

    # 处理每个文件
    for path in file_paths:
        data = {}
        with open(path, 'r') as file:
            headers = file.readline().strip().split('\t')
            for header in headers:
                data[header] = []
            for line in file:
                values = line.strip().split('\t')
                for header, value in zip(headers, values):
                    data[header].append(float(value))
        all_data.append(data)

    # 提取共同的epochs
    epochs = all_data[0]['epoch']  # 假设所有文件都有相同的epochs

    # 创建子图
    num_metrics = len([m for m in all_data[0].keys() if m not in exclude_headers])
    num_cols = (num_metrics + 1) // 2 + (1 if num_metrics % 2 else 0)  # 计算列数
    fig, axs = plt.subplots(2, num_cols, figsize=(15, 8), constrained_layout=True)
    axs = axs.flatten()  # 展平数组以便更容易迭代

    # 检查文件名是否一致，以确定使用文件名还是文件夹名作为标签
    file_names = [os.path.basename(path) for path in file_paths]
    unique_names = set(file_names)
    if len(unique_names) == 1:
        labels = [os.path.basename(os.path.dirname(path)) for path in file_paths]
    else:
        labels = file_names

    # 绘制每个指标的曲线图
    for i, key in enumerate([m for m in all_data[0].keys() if m not in exclude_headers]):
        for j, data in enumerate(all_data):
            axs[i].plot(epochs, data[key], label=f'{labels[j]} {key}', color=f'C{j}')
        axs[i].set_title(f'{key} over Epochs')
        axs[i].set_xlabel('Epoch')
        axs[i].set_ylabel(key)
        axs[i].legend()

    # 隐藏多余的子图
    for i in range(num_metrics, len(axs)):
        axs[i].axis('off')

    # 显示图表
    plt.savefig(save_path)
    plt.close()


def visualize_features(encoding_path, csv_path, save_html_path, show_feature='标注类别名称',
                       save_fig_path='test.jpg'):
    """
    使用TSNE可视化特征并生成静态和交互式图表

    参数:
        encoding_path: 特征数组的npy文件路径
        csv_path: 包含标签信息的CSV文件路径
        show_feature: 用于分类显示的特征列名
        save_fig_path: 静态图片保存路径
        save_html_path: 交互式HTML保存路径，为None则不保存
    """
    # 加载数据
    encoding_array = np.load(encoding_path, allow_pickle=True)
    df = pd.read_csv(csv_path)

    # 验证必要列是否存在
    if show_feature not in df.columns:
        raise ValueError(f"CSV文件中未找到'{show_feature}'列")
    if '图像路径' not in df.columns:
        raise ValueError("CSV文件中未找到'图像路径'列")

    # 获取类别列表
    class_list = df[show_feature].unique().tolist()
    n_class = len(class_list)
    print(f"共检测到 {n_class} 个类别")

    # 准备可视化样式
    marker_list = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8',
                   's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_',
                   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    # 随机打乱样式（固定随机种子确保结果可复现）
    random.seed(42)
    random.shuffle(marker_list)
    palette = sns.hls_palette(n_class)
    random.shuffle(palette)

    # TSNE降维
    print("开始TSNE降维...")
    tsne = TSNE(n_components=2, n_iter=20000, random_state=42)
    X_tsne_2d = tsne.fit_transform(encoding_array)
    print("TSNE降维完成")

    # 创建可视化数据框
    df_2d = pd.DataFrame({
        'X': X_tsne_2d[:, 0].squeeze(),
        'Y': X_tsne_2d[:, 1].squeeze(),
        show_feature: df[show_feature],
        '图像路径': df['图像路径']
    })

    # 绘制静态散点图
    plt.figure(figsize=(14, 14), facecolor='white')
    for idx, class_name in enumerate(class_list):
        # 获取当前类别的索引
        indices = np.where(df[show_feature] == class_name)
        # 绘制散点
        plt.scatter(
            X_tsne_2d[indices, 0],
            X_tsne_2d[indices, 1],
            color=palette[idx],
            marker=marker_list[idx % len(marker_list)],
            label=class_name,
            s=150
        )

    # 设置图例和坐标轴
    plt.legend(fontsize=16, markerscale=1, bbox_to_anchor=(1, 1))
    plt.xticks([])  # 隐藏x轴刻度
    plt.yticks([])  # 隐藏y轴刻度
    plt.tight_layout()

    # 保存静态图片
    plt.savefig(save_fig_path, dpi=500, bbox_inches='tight')
    print(f"静态图已保存至: {save_fig_path}")
    plt.close()  # 关闭图形避免显示

    # 创建交互式可视化
    print("生成交互式可视化...")
    fig = px.scatter(
        df_2d,
        x='X',
        y='Y',
        color=show_feature,
        symbol=show_feature,
        hover_name='图像路径',
        opacity=0.8,
        width=1000,
        height=600
    )

    # 优化布局
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))

    # 显示交互式图表
    # fig.show()

    # 保存HTML（如果指定了路径）
    fig.write_html(save_html_path)
    print(f"交互式HTML已保存至: {save_html_path}")

    return fig
