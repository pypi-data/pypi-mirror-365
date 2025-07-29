import os
import sys

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score
from tqdm import tqdm


def train_feature_extractor_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    mean_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='blue')
    for step, (images, labels) in enumerate(train_iterator):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 梯度清0
        optimizer.zero_grad()
        # 前向传播
        outputs = model(images)
        # 计算损失
        loss = criterion(outputs, labels)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()
        # 数值计算
        mean_loss = (mean_loss * step + loss.detach()) / (step + 1)
        _, predicted = torch.max(outputs, 1)
        # 设置进度条
        train_iterator.set_postfix(loss=loss.item(), mean_loss=mean_loss.item())
        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    train_accuracy = accuracy_score(y_true=all_labels, y_pred=all_predictions)
    print(f'the {epoch + 1} train accuracy is {train_accuracy}, and the train loss is {mean_loss.item():.6f}')

    val_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='GREEN')
    # 不计算梯度
    with torch.no_grad():
        for step, (images, labels) in enumerate(val_iterator):
            # 将数据转移到设备
            images, labels = images.to(device), labels.to(device)
            # 计算结果
            outputs = model(images)
            # 计算损失
            loss = criterion(outputs, labels)
            # 计算预测正确的样本
            _, predicted = torch.max(outputs, 1)
            val_iterator.set_postfix(loss=loss.item())
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        result = {'train_loss': mean_loss.item(), 'train_accuracy': train_accuracy, 'val_loss': val_loss.item(),
                  'y_pred': all_predictions, 'y_true': all_labels}
        # result = classification_report(y_true=all_labels, y_pred=all_predictions,
        #                                target_names=target_name, output_dict=True, digits=4)
        # result.update({'epoch': (epoch + 1), 'train_loss': mean_loss.item(),
        #                'val_loss': val_loss.item(), 'train_accuracy': train_accuracy})
    return result


def train_decae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    result = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images = images.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, images)

        loss.backward()
        optimizer.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    val_loss = torch.zeros(1).to(device)
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)

            outputs = model(images)
            loss = criterion(outputs, images)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    result['train_loss'] = train_loss.item()
    result['val_loss'] = val_loss.item()
    result['epoch'] = epoch + 1
    return result


def train_fcnn_one_epoch(cnn, fcnn, train_loader, val_loader, device, optimizer, criterion, epoch):
    result = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    cnn.eval()
    fcnn.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images, label = images.to(device), label.to(device)
        optimizer.zero_grad()
        feature = cnn(images)
        outputs = fcnn(feature)
        loss = criterion(outputs, label)
        loss.backward()
        optimizer.step()
        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())
    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    fcnn.eval()
    val_loss = torch.zeros(1).to(device)
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)
            feature = cnn(images)
            outputs = fcnn(feature)
            loss = criterion(outputs, label)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)
            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    result['train_loss'] = train_loss.item()
    result['val_loss'] = val_loss.item()
    result['epoch'] = epoch + 1
    return result


@torch.no_grad()
def cnn_predict(model, test_loader, device):
    model.eval()
    all_predictions = []
    all_labels = []
    test_iterator = tqdm(test_loader, file=sys.stdout, colour='yellow')
    for _, (images, labels) in enumerate(test_iterator):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)

        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    # return calculate_results(all_predictions, all_labels, test_loader.dataset.classes)
    return all_predictions, all_labels


@torch.no_grad()
def zlm_predict(feature_extractor, fcnn, test_loader, device, hsa_matrix):
    all_predictions = []
    all_labels = []
    predict_iterator = tqdm(test_loader, file=sys.stdout, colour='yellow')
    feature_extractor.eval()
    fcnn.eval()
    for images, label in predict_iterator:
        images, label = images.to(device), label.to(device)
        features = feature_extractor(images)
        embeddings = fcnn(features)
        # 批量计算所有样本与所有HSA的距离
        distances = torch.cdist(embeddings, hsa_matrix, p=2)  # [batch_size, num_classes]
        # 找到每个样本的最小距离索引
        _, predicted = torch.min(distances, dim=1)
        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(label.cpu().numpy())
    # return calculate_results(all_labels=all_labels, all_predictions=all_predictions,
    #                          classes=test_loader.dataset.classes)
    return all_predictions, all_labels


def extract_image_features(model_path, device, csv_path, save_path, transform):
    """
    从CSV文件中的图像路径提取特征并保存，支持自定义图像预处理

    参数:
        model_path: 模型文件路径
        device: 计算设备 (torch.device)
        csv_path: 包含图像路径的CSV文件路径
        save_path: 特征保存的npy文件路径
        transform: 图像预处理管道 (torchvision.transforms.Compose)
    """
    # 忽略警告信息
    import warnings
    warnings.filterwarnings("ignore")

    # 验证模型文件是否存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    # 加载模型
    model = torch.load(
        model_path,
        map_location='cpu',
        weights_only=False
    ).to(device)
    model.eval()  # 设置为评估模式

    # 验证CSV文件是否存在
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")

    # 读取CSV文件并检查必要列
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    if '图像路径' not in df.columns:
        raise ValueError("CSV文件中未找到'图像路径'列")

    # 特征提取
    encoding_array = []


    with torch.no_grad():  # 禁用梯度计算
        for img_path in tqdm(df['图像路径'], desc="提取特征"):
            # 检查图像文件是否存在
            if not os.path.exists(img_path):
                print(f"警告: 图像文件不存在 - {img_path}")
                continue

            try:
                # 打开图像并应用自定义预处理
                img_pil = Image.open(img_path).convert('RGB')  # 确保为RGB格式
                input_img = transform(img_pil).unsqueeze(0).to(device)

                # 提取特征（根据实际模型结构调整）
                feature = model(input_img).view(-1).squeeze().detach().cpu().numpy()

                encoding_array.append(feature)

            except Exception as e:
                print(f"处理图像 {img_path} 时出错: {str(e)}")

    # 保存提取的特征
    if encoding_array:
        encoding_array = np.array(encoding_array)

        # 确保保存目录存在
        np.save(save_path, encoding_array)
        print(f"特征提取完成，共 {len(encoding_array)} 个有效特征")
        print(f"特征已保存至: {save_path}")
    else:
        print("未提取到任何有效特征")



