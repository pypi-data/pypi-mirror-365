import os
import re
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, \
    classification_report


def get_device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


# 读取txt内两个不同表格的数据，并将结果转换为字典列表输出
def read_multi_table_txt(file_path):
    # 读取原始内容
    with open(file_path, 'r') as f:
        content = f.read()

    # 按表格标题分割内容（假设每个新表格以"epoch"开头）
    table_blocks = re.split(r'\n(?=epoch\s)', content.strip())

    # 处理每个表格块
    table_dicts = []
    for block in table_blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        # 解析列名（处理制表符和混合空格）
        columns = re.split(r'\s{2,}|\t', lines[0])

        # 解析数据行（处理混合分隔符）
        data = []
        for line in lines[1:]:
            # 使用正则表达式分割多个连续空格/制表符
            row = re.split(r'\s{2,}|\t', line)
            data.append(row)

        # 创建DataFrame并自动转换数值类型
        df = pd.DataFrame(data, columns=columns)
        df = df.apply(pd.to_numeric, errors='coerce')  # 自动识别数值列，非数值转换为NaN

        # 将DataFrame转换为字典，每列以列表形式保存
        table_dict = df.to_dict(orient='list')
        table_dicts.append(table_dict)

    return table_dicts


def get_current_time(format_str="%Y-%m-%d %H:%M:%S"):
    """
    获取东八区（UTC+8）的当前时间，并返回指定格式的字符串
    :param format_str: 时间格式（默认为 "%Y-%m-%d %H:%M:%S"）
    :return: 格式化后的时间字符串
    """

    # 创建东八区的时区对象
    utc8_timezone = timezone(timedelta(hours=8))

    # 转换为东八区时间
    utc8_time = datetime.now(utc8_timezone)

    # 格式化为字符串
    formatted_time = utc8_time.strftime(format_str)
    return formatted_time


# val和test时的相关结果指标计算
def calculate_results(all_labels, all_predictions, classes, average='macro'):
    results = {
        'accuracy': accuracy_score(y_true=all_labels, y_pred=all_predictions),
        'precision': precision_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'recall': recall_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'f1_score': f1_score(y_true=all_labels, y_pred=all_predictions, average=average),
        'cm': confusion_matrix(y_true=all_labels, y_pred=all_predictions, labels=np.arange(len(classes)))
    }
    return results


def calculate_metric(all_labels, all_predictions, classes, class_metric=False, average='macro avg'):
    metric = classification_report(y_true=all_labels, y_pred=all_predictions,
                                   target_names=classes, digits=4, output_dict=True, zero_division=0)
    if not class_metric:
        metric = {
            'accuracy': metric.get('accuracy'),
            'precision': metric.get(average).get('precision'),
            'recall': metric.get(average).get('recall'),
            'f1-score': metric.get(average).get('f1-score'),
        }
        return metric
    else:
        return metric


def initialize_results_file(results_file, result_info):
    """
    初始化结果文件，确保文件存在且第一行包含指定的内容。

    参数:
        results_file (str): 结果文件的路径。
        result_info (list): 需要写入的第一行内容列表。
    """
    # 处理 result_info，在每个单词后添加两个空格
    result_info_str = '  '.join(result_info) + '\n'
    # 检查文件是否存在
    if os.path.exists(results_file):
        # 如果文件存在，读取第一行
        with open(results_file, "r") as f:
            first_line = f.readline().strip()
        # 检查第一行是否与 result_info 一致
        if first_line == result_info_str.strip():
            print(f"文件 {results_file} 已存在且第一行已包含 result_info，不进行写入。")
        else:
            # 如果不一致，写入 result_info
            with open(results_file, "w") as f:
                f.write(result_info_str)
            print(f"文件 {results_file} 已被重新初始化。")
    else:
        # 如果文件不存在，创建并写入 result_info
        with open(results_file, "w") as f:
            f.write(result_info_str)
        print(f"文件 {results_file} 已创建并写入 result_info。")


def is_similar_key(key1, key2):
    """
    检查两个键是否相似，考虑复数形式的转换。

    Args:
        key1 (str): 第一个键
        key2 (str): 第二个键

    Returns:
        bool: 如果两个键相似（包括复数形式的转换），返回 True，否则返回 False
    """
    if key1 == key2:
        return True

    # 检查 key2 是否是复数形式
    if key2.endswith("ies"):
        singular_candidate = key2.removesuffix("ies") + "y"
        if key1 == singular_candidate:
            return True

    if key2.endswith("es"):
        singular_candidate = key2.removesuffix("es")
        if key1 == singular_candidate:
            return True

    if key2.endswith("s"):
        singular_candidate = key2.removesuffix("s")
        if key1 == singular_candidate:
            return True

    return False


def append_to_results_file(file_path: str,
                           data_dict: dict,
                           column_order: list,
                           float_precision: int = 4,
                           more_float: int = 2,
                           custom_column_widths: dict = None) -> None:
    """
    通用格式化文本行写入函数

    参数：
    file_path: 目标文件路径
    data_dict: 包含数据的字典，键为列名
    column_order: 列顺序列表，元素为字典键
    float_precision: 浮点数精度位数 (默认5位)
    more_float: 额外的浮点数精度位数
    custom_column_widths: 自定义列宽的字典，键为列名，值为列宽
    """
    # 计算每列的最大宽度
    column_widths = []
    formatted_data = []
    for col in column_order:
        # 查找 data_dict 中相似的键
        dict_key = None
        for key in data_dict:
            if is_similar_key(key, col):
                dict_key = key
                break
        if dict_key is None:
            raise ValueError(f"Missing required column: {col}")

        value = data_dict[dict_key]

        # 根据数据类型进行格式化
        if isinstance(value, (int, np.integer)):
            fmt_value = f"{value:d}"
        elif isinstance(value, (float, np.floating)):
            if col in ['train_losses', 'val_losses']:  # 如果列名是'train_losses'或'val_losses'，保留浮点数精度位数+1位
                fmt_value = f"{value:.{float_precision + more_float}f}"
            elif col == 'lrs':
                fmt_value = f"{value:.8f}"
            else:
                fmt_value = f"{value:.{float_precision}f}"
        elif isinstance(value, str):
            fmt_value = value
        else:  # 处理其他类型转换为字符串
            fmt_value = str(value)

        # 确定列宽
        if custom_column_widths and col in custom_column_widths:
            column_width = custom_column_widths[col]
        else:
            # 取列名长度和数值长度的最大值作为列宽
            column_width = max(len(col), len(fmt_value))
        column_widths.append(column_width)

        # 应用列宽对齐
        if col == column_order[-1]:  # 最后一列左边对齐
            fmt_value = fmt_value.ljust(column_width)
        else:
            fmt_value = fmt_value.rjust(column_width)

        formatted_data.append(fmt_value)

    # 构建文本行并写入，列之间用两个空格分隔
    line = "  ".join(formatted_data) + '\n'
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(line)


def make_save_dirs(root_dir):
    img_dir = os.path.join(root_dir, 'images')
    model_dir = os.path.join(root_dir, 'models')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    print(f'The output folder:{img_dir},{model_dir} has been created.')
    return img_dir, model_dir


def list_folders(path):
    # 获取目录下的所有内容
    entries = os.listdir(path)
    # 筛选只保留文件夹
    folders = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return folders


def create_csv(data, file_path):
    """
    根据给定的字典或列表生成CSV文件

    参数:
        data: 可以是列表（作为表头）或字典（键为表头，值为数据）
        file_path: 字符串，CSV文件的保存路径（包括文件名）
    """
    if isinstance(data, list):
        # 处理列表：仅作为表头创建空文件
        df = pd.DataFrame(columns=data)
    elif isinstance(data, dict):
        # 处理字典：键作为表头，值作为数据
        # 检查是否所有值都是列表且长度一致
        values = list(data.values())
        if all(isinstance(v, list) for v in values):
            # 确保所有列表长度相同
            lengths = set(len(v) for v in values)
            if len(lengths) <= 1:  # 允许所有空列表或长度一致的非空列表
                df = pd.DataFrame(data)
            else:
                raise ValueError("字典中所有值的列表长度必须一致")
        else:
            raise ValueError("字典的值必须是列表类型")
    else:
        raise TypeError("data必须是列表或字典类型")

    # 保存为CSV文件
    df.to_csv(file_path, index=False)
    print(f"已生成CSV文件：{file_path}")


def append_metrics_to_csv(metrics, filename='training_metrics.csv'):
    """
    将一轮训练的指标数据按CSV表头顺序整理后追加到文件

    参数:
        metrics: 字典，包含当前轮次的指标数据
        filename: 保存指标的CSV文件名
    """
    # 检查文件是否存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"文件 {filename} 不存在，请先创建包含表头的CSV文件")

    # 读取CSV文件的表头（仅读取第一行）
    with open(filename, 'r') as f:
        header = f.readline().strip().split(',')

    # 检查metrics是否包含所有表头字段
    missing_keys = [key for key in header if key not in metrics]
    if missing_keys:
        raise ValueError(f"metrics缺少以下必要字段: {missing_keys}")

    # 按表头顺序重新整理字典
    ordered_metrics = {key: metrics[key] for key in header}

    # 转换为DataFrame并追加到CSV
    df = pd.DataFrame([ordered_metrics])
    df.to_csv(filename, mode='a', header=False, index=False)


def load_class_label_maps(txt_path):
    """
    直接从classes_to_label.txt加载class与label的映射关系

    参数:
        txt_path: 映射文件路径（格式：每行"class名称,label_id"）

    返回:
        class_to_label: dict - {class名称: label_id}
        label_to_class: dict - {label_id: class名称}
    """
    class_to_label = {}
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            # 分割class名称和label（处理可能的空格）
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 2:
                raise ValueError(f"映射文件格式错误，行内容应为'class,label'：{line}")
            cls, label = parts
            class_to_label[cls] = int(label)

    # 生成反向映射（label→class）
    label_to_class = {v: k for k, v in class_to_label.items()}
    return class_to_label, label_to_class


def generate_image_dataframe(root_dir, image_subdir):
    """
    直接读取classes_to_label.txt，生成包含图像路径、标注ID和类别名称的数据框

    参数:
        root_dir: 根目录（包含classes_to_label.txt）
        image_subdir: 存放图像的子文件夹（位于root_dir下）

    返回:
        pd.DataFrame - 包含'图像路径'、'标注类别ID'、'标注类别名称'的DataFrame
    """

    # 自然排序函数（确保文件名按数字顺序排列）
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

    # 1. 加载class与label的映射（直接读取txt文件）
    label_txt_path = os.path.join(root_dir, "classes_to_label.txt")
    if not os.path.exists(label_txt_path):
        raise FileNotFoundError(f"未找到映射文件：{label_txt_path}")
    class_to_label, label_to_class = load_class_label_maps(label_txt_path)

    # 2. 处理图像文件夹
    image_dir = os.path.join(root_dir, image_subdir)
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"图像文件夹不存在：{image_dir}")

    # 3. 获取所有图像文件并排序
    image_extensions = ('.bmp', '.jpg', '.jpeg', '.png')
    images_list = [
        f for f in os.listdir(image_dir)
        if f.lower().endswith(image_extensions)
    ]
    if not images_list:
        raise ValueError(f"图像文件夹中未找到任何图像文件：{image_dir}")
    images_list = sorted(images_list, key=natural_sort_key)

    # 4. 提取图像路径、标注ID和类别名称
    full_image_paths = []
    label_ids = []  # 标注类别ID（对应txt中的label）
    class_names = []  # 标注类别名称（对应txt中的class）

    for img in images_list:
        # 构建完整图像路径
        full_path = os.path.join(image_dir, img)
        full_image_paths.append(full_path)

        # 从文件名提取class名称（假设格式："class名称_其他信息.扩展名"）
        # 例如："0HP-No_123.jpg" → 提取"0HP-No"
        class_base = os.path.splitext(img)[0].split('_')[0]

        # 验证class是否在映射表中
        if class_base not in class_to_label:
            raise ValueError(
                f"文件名提取的class '{class_base}' 不在映射表中，请检查格式：\n"
                f"图像文件：{img}\n"
                f"映射表路径：{label_txt_path}"
            )

        # 转换为label_id和class名称
        label_id = class_to_label[class_base]
        class_name = label_to_class[label_id]

        label_ids.append(label_id)
        class_names.append(class_name)

    # 5. 构建并返回DataFrame
    return pd.DataFrame({
        '图像路径': full_image_paths,
        '标注类别ID': label_ids,
        '标注类别名称': class_names
    })