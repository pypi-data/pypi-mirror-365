"""
AI Tools 核心功能模块
"""


def sayHello():
    """
    输出hello world!
    
    Returns:
        str: 返回hello world!字符串
    """
    message = "hello world!"
    print(message)
    return message


def sayTest001():
    """
    显示音频特征提取代码示例
    
    Returns:
        str: 返回音频处理代码字符串
    """
    message = """
    import librosa
    import librosa.display
    import numpy as np
    import matplotlib.pyplot as plt
    import sys
    import os

    def main():
        # 1. Configuration
        audio_path = 'D:/其他/audio/30seconds.wav'  # 请确保文件路径正确
        save_img_path = 'audio_features.png'
        feature_prefix = 'features_'
        
        # 2. Verify audio file
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            sys.exit(1)
        
        # 3. Load audio
        try:
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            print(f"Audio loaded: {len(audio)/sr:.2f} seconds at {sr} Hz sample rate")
        except Exception as e:
            print(f"Error loading audio: {e}")
            sys.exit(1)
        
        # 4. Feature extraction
        def extract_features(y, sr):
            # Compute STFT (Short-Time Fourier Transform)
            stft = np.abs(librosa.stft(y))
            
            # MFCC (Mel-Frequency Cepstral Coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Chroma feature
            chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
            
            # Mel-scaled Spectrogram
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_db = librosa.power_to_db(mel, ref=np.max)  # Convert to dB
            
            return {'stft_db': librosa.amplitude_to_db(stft, ref=np.max),
                    'mfcc': mfcc,
                    'chroma': chroma,
                    'mel_db': mel_db}

        print("Extracting audio features...")
        features = extract_features(audio, sr)
        
        # 5. Visualization setup
        plt.figure(figsize=(14, 12))
        
        # Feature 1: STFT Spectrogram
        ax1 = plt.subplot(4, 1, 1)
        stft_disp = librosa.display.specshow(features['stft_db'], 
                                            x_axis='time', 
                                            y_axis='log', 
                                            sr=sr)
        plt.title('STFT (Log Frequency)')
        plt.colorbar(format='%+2.0f dB')
        
        # Feature 2: MFCC
        plt.subplot(4, 1, 2, sharex=ax1)
        mfcc_disp = librosa.display.specshow(features['mfcc'], 
                                            x_axis='time', 
                                            sr=sr)
        plt.title('MFCC Coefficients')
        plt.colorbar()
        
        # Feature 3: Chroma
        plt.subplot(4, 1, 3, sharex=ax1)
        chroma_disp = librosa.display.specshow(features['chroma'], 
                                            x_axis='time', 
                                            y_axis='chroma', 
                                            sr=sr)
        plt.title('Chroma Features')
        plt.colorbar()
        
        # Feature 4: Mel Spectrogram
        plt.subplot(4, 1, 4, sharex=ax1)
        mel_disp = librosa.display.specshow(features['mel_db'], 
                                            x_axis='time', 
                                            y_axis='mel', 
                                            sr=sr)
        plt.title('Mel Spectrogram')
        plt.colorbar(format='%+2.0f dB')
        
        # 6. Finalize and save visualization
        plt.tight_layout()
        plt.savefig(save_img_path, dpi=300)
        print(f"Feature visualization saved to {save_img_path}")
        
        # 7. Save features as numpy arrays
        for feature_name, feature_data in features.items():
            filename = f"{feature_prefix}{feature_name}.npy"
            np.save(filename, feature_data)
            print(f"Saved {filename} ({feature_data.shape[1]} frames)")
        
        print("Feature extraction completed successfully!")

    if __name__ == "__main__":
        main()
    
    """
    
    return message

def sayTest002():
    """
    完整流程：
    1. 使用 ClearVoice speech_enhancement 模型进行语音降噪增强
    2. MOS 质量评分
    3. SRMR 清晰度评分
    """
    message = """
    from clearvoice import ClearVoice
import os
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import stft


def enhance_and_score(
    input_path: str,
    output_path: str,
    se_model: str = "MossFormer2_SE_48K"
):

    # 检查输入
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"找不到输入文件: {input_path}")

    # 初始化 ClearVoice
    cv_se = ClearVoice(
        task="speech_enhancement",
        model_names=[se_model]
    )

    # 读取音频
    y, sr = librosa.load(input_path, sr=None, mono=True)

    # 根据模型后缀决定目标采样率
    target_sr = 48000 if se_model.endswith("48K") else 16000
    # 重采样到模型所需采样率
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
        tmp_path = input_path.replace(".wav", f"_{sr//1000}k_temp.wav")
        sf.write(tmp_path, y, sr)
        model_input = tmp_path
    else:
        model_input = input_path

    # 执行语音增强，不立即写磁盘
    enhanced_audio = cv_se(
        input_path=model_input,
        online_write=False
    )

    # 保存增强结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv_se.write(enhanced_audio, output_path=output_path)

    # 清理临时文件
    if model_input.endswith("_temp.wav") and os.path.isfile(model_input):
        os.remove(model_input)

    # 载入增强后音频用于评分
    audio, fs = librosa.load(output_path, sr=None, mono=True)

    # 计算 MOS
    rms = librosa.feature.rms(y=audio)[0].mean()
    spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0].mean()
    rms_score = min(1.5, max(0.5, rms)) * 2
    flatness_score = 4 - min(3, spectral_flatness * 5)
    mos_score = round(max(1.0, min(5.0, (rms_score + flatness_score) / 2 * 1.25)), 2)

    # 计算 SRMR（内部重采样）
    if fs > 16000:
        audio_srmr = librosa.resample(audio, orig_sr=fs, target_sr=16000)
        fs_srmr = 16000
    else:
        audio_srmr, fs_srmr = audio, fs
    f, t, Zxx = stft(audio_srmr, fs=fs_srmr, nperseg=256, noverlap=128)
    mags = np.abs(Zxx)
    speech_band = np.mean(mags[(f >= 300) & (f <= 4000)], axis=0)
    full_band = np.mean(mags, axis=0)
    srmr_score = round(max(1.0, min(10.0, np.mean(speech_band) / np.mean(full_band) * 15)), 2)

    return {
        "enhanced_path": output_path,
        "mos": mos_score,
        "srmr": srmr_score
    }


def main():
    print("=== 任务：MossFormer2_SE_48K 语音增强 + 评分 ===")

    input_audio = "D:/其他/ai_examing_002/30seconds.wav"
    output_audio = "D:/其他/ai_examing_002/30seconds-denoised.wav"

    try:
        results = enhance_and_score(input_audio, output_audio)
        print(f"✓ 增强完成，输出文件: {results['enhanced_path']}")
        print(f"✓ MOS 质量评分: {results['mos']}/5")
        print(f"✓ SRMR 清晰度评分: {results['srmr']}")
    except Exception as e:
        print(f"处理失败: {e}")


if __name__ == "__main__":
    main()

    
    """
    return message
def sayTest003_1():
    """
    输出003的requirements.txt
    
    Returns:
        str: requirements.txt的内容
    """
        
    message = """
        torch>=1.12.0
        torchaudio>=0.12.0
        librosa>=0.9.0
        numpy>=1.21.0
        scikit-learn>=1.0.0
        tqdm>=4.62.0
        matplotlib>=3.5.0
        seaborn>=0.11.0
        requests>=2.25.0
        pandas>=1.3.0
    """

    return message


def sayTest003_2():
    """
    输出情感分析数据集处理代码示例
    
    Returns:
        str: 返回数据集处理代码字符串
    """
    message = """
# dataset.py
import os
import librosa
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from tqdm import tqdm

EMOTION_LABELS = ["angry", "fear", "happy", "neutral", "sad", "surprise"]
label_map = {label: idx for idx, label in enumerate(EMOTION_LABELS)}

class EmotionFeatureDataset(Dataset):
    def __init__(self, root_dir, sr=16000, n_mels=128, max_len=300, split='train', 
                 train_ratio=0.8, random_state=42, cache_dir="feature_cache"):
        self.root_dir = root_dir
        self.sr = sr
        self.n_mels = n_mels
        self.max_len = max_len
        self.split = split
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # 获取所有音频文件
        self.audio_files, self.labels = self._get_audio_files()
        
        # 分割数据集
        if len(self.audio_files) > 0:
            train_files, val_files, train_labels, val_labels = train_test_split(
                self.audio_files, self.labels, test_size=1-train_ratio, 
                random_state=random_state, stratify=self.labels
            )
            
            if split == 'train':
                self.audio_files = train_files
                self.labels = train_labels
            else:
                self.audio_files = val_files
                self.labels = val_labels
        
        print(f"{split} dataset: {len(self.audio_files)} samples")
        
    def _get_audio_files(self):
        audio_files = []
        labels = []
        
        for emotion in EMOTION_LABELS:
            emotion_dir = os.path.join(self.root_dir, emotion)
            if os.path.exists(emotion_dir):
                for file_name in os.listdir(emotion_dir):
                    if file_name.endswith('.wav'):
                        audio_files.append(os.path.join(emotion_dir, file_name))
                        labels.append(label_map[emotion])
        
        return audio_files, labels
    
    def _extract_features(self, audio_file):
        # 提取音频特征：Mel频谱图和基频
        # 生成缓存文件名
        cache_name = os.path.basename(audio_file).replace('.wav', '.npy')
        cache_path = os.path.join(self.cache_dir, cache_name)
        
        # 如果缓存存在，直接加载
        if os.path.exists(cache_path):
            return np.load(cache_path)
        
        try:
            # 加载音频
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # 提取Mel频谱图
            mel_spec = librosa.feature.melspectrogram(
                y=y, sr=sr, n_mels=self.n_mels, hop_length=512, n_fft=2048
            )
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # 提取基频(F0/Pitch)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=512)
            pitch = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch.append(pitches[index, t])
            pitch = np.array(pitch).reshape(1, -1)
            
            # 合并特征 (128 + 1 = 129)
            features = np.vstack([mel_spec_db, pitch])
            
            # 保存到缓存
            np.save(cache_path, features)
            
            return features
            
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
            # 返回零特征
            return np.zeros((129, 100))
    
    def _pad_or_truncate(self, features):
        #填充或截断特征到固定长度
        if features.shape[1] > self.max_len:
            # 截断
            return features[:, :self.max_len]
        elif features.shape[1] < self.max_len:
            # 填充
            pad_width = self.max_len - features.shape[1]
            return np.pad(features, ((0, 0), (0, pad_width)), mode='constant', constant_values=0)
        else:
            return features
    
    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        audio_file = self.audio_files[idx]
        label = self.labels[idx]
        
        # 提取特征
        features = self._extract_features(audio_file)
        
        # 填充或截断到固定长度
        features = self._pad_or_truncate(features)
        
        # 转换为tensor
        features = torch.FloatTensor(features).unsqueeze(0)  # 添加通道维度 (1, 129, max_len)
        label = torch.LongTensor([label])
        
        return features, label.squeeze() 
"""
    return message

def sayTest003_3():
    """
    输出情感分析CNN模型代码示例
    
    Returns:
        str: 返回CNN模型代码字符串
    """
    message = """
    # model.py
    import torch
import torch.nn as nn
import torch.nn.functional as F

class EmotionCNN(nn.Module):
    # n_classes表示情感标签的个数
    def __init__(self, n_input=129, n_classes=6):
        super(EmotionCNN, self).__init__()
        
        # 第一个卷积块
        self.conv1 = nn.Conv2d(1, 32, kernel_size=(3, 3), padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=(2, 2))
        self.dropout1 = nn.Dropout2d(0.25)
        
        # 第二个卷积块
        self.conv2 = nn.Conv2d(32, 64, kernel_size=(3, 3), padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=(2, 2))
        self.dropout2 = nn.Dropout2d(0.25)
        
        # 第三个卷积块
        self.conv3 = nn.Conv2d(64, 128, kernel_size=(3, 3), padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(kernel_size=(2, 2))
        self.dropout3 = nn.Dropout2d(0.25)
        
        # 计算全连接层输入维度
        # 假设输入是 (1, 129, 300)
        # 经过3次池化后：129/8 ≈ 16, 300/8 ≈ 37
        # 固定尺寸以保证模型结构一致
        self.fc1 = nn.Linear(128 * 16 * 37, 512)
        self.dropout4 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 256)
        self.dropout5 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(256, n_classes)
        
    def forward(self, x):
        # 第一个卷积块
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)
        x = self.dropout1(x)
        
        # 第二个卷积块
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)
        x = self.dropout2(x)
        
        # 第三个卷积块
        x = self.conv3(x)
        x = self.bn3(x)
        x = F.relu(x)
        x = self.pool3(x)
        x = self.dropout3(x)
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 全连接层
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout4(x)
        
        x = self.fc2(x)
        x = F.relu(x)
        x = self.dropout5(x)
        
        x = self.fc3(x)
        
        return x 

"""
    return message

def sayTest003_4():
    """
    输出情感分析模型训练代码示例
    
    Returns:
        str: 返回模型训练代码字符串
    """
    message = """
    # train.py
    import torch
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from dataset import EmotionFeatureDataset, EMOTION_LABELS
from model import EmotionCNN

# -------------------- 配置项 -------------------
MODEL_TYPE = 'cnn'
BATCH_SIZE = 16
N_EPOCHS = 40
LEARNING_RATE = 1e-3
MAX_LEN = 300
MODEL_PATH = f'emotion_{MODEL_TYPE}.pt'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"使用设备: {DEVICE}")

def train_one_epoch(model, loader, optimizer, criterion, device):
    #训练一个epoch
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for X, y in tqdm(loader, desc="Training"):
        X, y = X.to(device), y.to(device)
        
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += y.size(0)
        correct += (predicted == y).sum().item()
    
    epoch_loss = running_loss / len(loader)
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc

def validate_one_epoch(model, loader, criterion, device):
    #验证一个epoch
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for X, y in tqdm(loader, desc="Validation"):
            X, y = X.to(device), y.to(device)
            
            outputs = model(X)
            loss = criterion(outputs, y)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += y.size(0)
            correct += (predicted == y).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(y.cpu().numpy())
    
    epoch_loss = running_loss / len(loader)
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc, all_preds, all_labels

def plot_confusion_matrix(y_true, y_pred, save_path='confusion_matrix.png'):
    #绘制混淆矩阵
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=EMOTION_LABELS, yticklabels=EMOTION_LABELS)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def plot_training_history(train_losses, val_losses, train_accs, val_accs, save_path='training_history.png'):
    #绘制训练历史
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # 损失曲线
    ax1.plot(train_losses, label='Train Loss')
    ax1.plot(val_losses, label='Val Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    # 准确率曲线
    ax2.plot(train_accs, label='Train Acc')
    ax2.plot(val_accs, label='Val Acc')
    ax2.set_title('Training and Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def main():
    # -------------------- 数据加载 ------
    print("加载数据集...")
    # datasat_train表示训练集文件夹名称
    train_dataset = EmotionFeatureDataset('datasat_train', split='train', max_len=MAX_LEN)
    val_dataset = EmotionFeatureDataset('datasat_train', split='val', max_len=MAX_LEN)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    print(f"训练集大小: {len(train_dataset)}")
    print(f"验证集大小: {len(val_dataset)}")
    
    # -------------------- 模型初始化 ------
    model = EmotionCNN(n_input=129, n_classes=6)
    model.to(DEVICE)
    
    # 计算模型参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")
    
    # ------------------- 训练准备 -------------------
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)
    
    # 记录训练历史
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    best_val_acc = 0.0
    
    # -------------------- 训练循环 ----
    print("开始训练...")
    for epoch in range(N_EPOCHS):
        print(f"\nEpoch {epoch+1}/{N_EPOCHS}")
        print("-" * 50)
        
        # 训练
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, DEVICE)
        
        # 验证
        val_loss, val_acc, val_preds, val_labels = validate_one_epoch(model, val_loader, criterion, DEVICE)
        
        # 学习率调度
        scheduler.step(val_loss)
        
        # 记录历史
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        print(f"Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
            }, MODEL_PATH)
            print(f"新的最佳模型已保存! 验证准确率: {val_acc:.2f}%")
    
    print(f"\n训练完成! 最佳验证准确率: {best_val_acc:.2f}%")
    
    # -------------------- 最终评估 ----
    print("\n进行最终评估...")
    
    # 加载最佳模型
    checkpoint = torch.load(MODEL_PATH)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # 最终验证
    val_loss, val_acc, val_preds, val_labels = validate_one_epoch(model, val_loader, criterion, DEVICE)
    
    print(f"最终验证准确率: {val_acc:.2f}%")
    
    # 分类报告
    print("\n分类报告:")
    print(classification_report(val_labels, val_preds, target_names=EMOTION_LABELS))
    
    # 绘制混淆矩阵
    plot_confusion_matrix(val_labels, val_preds)
    
    # 绘制训练历史
    plot_training_history(train_losses, val_losses, train_accs, val_accs)
    
    print(f"模型已保存到: {MODEL_PATH}")

if __name__ == "__main__":
    main() 
    

    """
    return message

def sayTest003_5():
    """
    输出情感分析模型预测代码示例
    
    Returns:
        str: 返回模型预测代码字符串
    """
    message = """
     #predict.py
     import os
import torch
import librosa
import numpy as np
import requests
import json
from model import EmotionCNN
from dataset import EMOTION_LABELS

def extract_features(audio_file, sr=16000, n_mels=128, max_len=300):
    #提取单个音频文件的特征
    try:
        # 加载音频
        y, sr = librosa.load(audio_file, sr=sr)
        
        # 提取Mel频谱图
        mel_spec = librosa.feature.melspectrogram(
            y=y, sr=sr, n_mels=n_mels, hop_length=512, n_fft=2048
        )
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 提取基频(F0/Pitch)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=512)
        pitch = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch.append(pitches[index, t])
        pitch = np.array(pitch).reshape(1, -1)
        
        # 合并特征 (128 + 1 = 129)
        features = np.vstack([mel_spec_db, pitch])
        
        # 填充或截断到固定长度
        if features.shape[1] > max_len:
            features = features[:, :max_len]
        elif features.shape[1] < max_len:
            pad_width = max_len - features.shape[1]
            features = np.pad(features, ((0, 0), (0, pad_width)), mode='constant', constant_values=0)
        
        return features
        
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return np.zeros((129, max_len))

def predict_emotion(model, features, device):
    #预测单个音频的情感
    model.eval()
    
    # 转换为tensor并添加batch和channel维度
    features_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0)  # (1, 1, 129, max_len)
    features_tensor = features_tensor.to(device)
    
    with torch.no_grad():
        outputs = model(features_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_emotion = EMOTION_LABELS[predicted.item()]
    
    return predicted_emotion

def predict_test_audio(model_path, test_dir, device):
    #对测试目录中的所有音频进行预测
    # 加载模型
    model = EmotionCNN(n_input=129, n_classes=6)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    print(f"模型加载完成，验证准确率: {checkpoint.get('val_acc', 'N/A'):.2f}%")
    
    # 获取所有wav文件
    wav_files = [f for f in os.listdir(test_dir) if f.endswith('.wav')]
    print(f"找到 {len(wav_files)} 个音频文件")
    
    results = {}
    
    for wav_file in wav_files:
        audio_path = os.path.join(test_dir, wav_file)
        
        # 提取特征
        features = extract_features(audio_path)
        
        # 预测情感
        emotion = predict_emotion(model, features, device)
        
        # 保存结果 (去掉.wav扩展名)
        filename_without_ext = wav_file.replace('.wav', '')
        results[filename_without_ext] = emotion
        
        print(f"{wav_file} -> {emotion}")
    
    return results

def submit_results(results, api_url):
    #提交结果到评分接口
    payload = {
        "answer": results
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        print(f"提交状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response
    except Exception as e:
        print(f"提交失败: {e}")
        return None

def main():
    # 配置
    MODEL_PATH = 'emotion_cnn.pt'
    TEST_DIR = './data/task-3-test-audio'
    API_URL = 'https://1f9f25e88908.ngrok-free.app/grade_emotion/'
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print(f"使用设备: {DEVICE}")
    
    # 检查文件是否存在
    if not os.path.exists(MODEL_PATH):
        print(f"错误: 模型文件 {MODEL_PATH} 不存在!")
        return
    
    if not os.path.exists(TEST_DIR):
        print(f"错误: 测试目录 {TEST_DIR} 不存在!")
        return
    
    # 进行预测
    print("开始预测...")
    results = predict_test_audio(MODEL_PATH, TEST_DIR, DEVICE)
    
    print(f"\n预测完成! 共预测了 {len(results)} 个文件")
    print("预测结果:")
    for filename, emotion in results.items():
        print(f"  {filename}: {emotion}")
    
    # 保存结果到本地文件
    with open('prediction_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n结果已保存到 prediction_results.json")
    
    # 提交结果
    print("\n提交结果到评分接口...")
    response = submit_results(results, API_URL)
    
    if response and response.status_code == 200:
        print("结果提交成功!")
    else:
        print("结果提交失败，请检查网络连接和API地址")

if __name__ == "__main__":
    main() 
"""
    return message