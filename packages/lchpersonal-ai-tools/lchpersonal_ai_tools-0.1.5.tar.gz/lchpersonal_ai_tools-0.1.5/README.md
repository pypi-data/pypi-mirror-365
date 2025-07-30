# AI Tools

一个简单的Python工具包，提供基础的AI相关工具函数。

## 安装

```bash
pip install lchpersonal-ai-tools
```

## 使用方法

```python
from ai_tools import (
    sayHello, sayTest001, sayTest002, 
    sayTest003_1, sayTest003_2, sayTest004, sayTest005,
    sayTest003Plus_1, sayTest003Plus_2, sayTest003Plus_3, sayTest003Plus_4
)

# 基础问候
sayHello()  # 输出: hello world!

# 显示音频处理代码示例
sayTest001()  # 输出音频特征提取代码

# 显示语音增强和评分代码示例
sayTest002()  # 输出语音增强代码

# 显示情感分析项目代码示例（基础版）
sayTest003_1()  # 输出requirements.txt
sayTest003_2()  # 输出数据集处理代码
sayTest003_3()  # 输出CNN模型代码
sayTest003_4()  # 输出模型训练代码
sayTest003_5()  # 输出模型预测代码

# 显示语音识别和合成代码示例
sayTest004()  # 输出语音识别(ASR)代码
sayTest005()  # 输出语音合成(TTS)代码

# 显示高级情感分析项目代码示例（完整版）
sayTest003Plus_1()  # 输出推理模块 inference.py
sayTest003Plus_2()  # 输出训练模块 train.py
sayTest003Plus_3()  # 输出CNN模型 model.py
sayTest003Plus_4()  # 输出数据集处理 dataset.py
```

## 功能

### 基础功能
- `sayHello()`: 输出 "hello world!" 消息

### 音频处理
- `sayTest001()`: 显示音频特征提取代码示例
- `sayTest002()`: 显示语音增强和评分代码示例

### 情感分析项目（基础版）
- `sayTest003_1()`: 显示情感分析项目的requirements.txt
- `sayTest003_2()`: 显示情感分析数据集处理代码
- `sayTest003_3()`: 显示情感分析CNN模型代码
- `sayTest003_4()`: 显示情感分析模型训练代码
- `sayTest003_5()`: 显示情感分析模型预测代码

### 语音技术
- `sayTest004()`: 显示语音识别(ASR)代码示例
- `sayTest005()`: 显示语音合成(TTS)代码示例

### 高级情感分析项目（完整版）
- `sayTest003Plus_1()`: 显示完整推理模块 (inference.py)
  - 支持批量音频文件处理
  - 包含API接口对接功能
  - 结果自动提交和备份
- `sayTest003Plus_2()`: 显示完整训练模块 (train.py)
  - 高级训练循环和验证
  - 可视化训练历史
  - 类别权重平衡处理
- `sayTest003Plus_3()`: 显示高级CNN模型 (model.py)
  - 4层卷积+池化结构
  - 批归一化和Dropout正则化
  - 全局平均池化优化
- `sayTest003Plus_4()`: 显示高级数据集处理 (dataset.py)
  - Mel频谱+F0基频特征提取
  - 数据缓存和分割机制
  - PyTorch Dataset标准接口

## 要求

- Python 3.7+
- 可选依赖：
  - 音频处理：librosa, matplotlib, numpy, soundfile
  - 机器学习：torch, scikit-learn, pandas, tqdm, seaborn
  - 语音技术：dotenv, asyncio, requests
  - 特征提取：pickle（内置）

## 许可证

MIT License

## 开发

### 本地安装开发版本

```bash
git clone https://github.com/lchpersonal/ai-tools.git
cd ai-tools
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

### 构建包

```bash
python -m build
```

## 更新日志

### 0.1.5
- 添加sayTest003Plus系列函数（高级情感分析完整实现）
- sayTest003Plus_1: 完整推理模块（inference.py）
- sayTest003Plus_2: 完整训练模块（train.py）
- sayTest003Plus_3: 高级CNN模型（model.py）
- sayTest003Plus_4: 高级数据集处理（dataset.py）
- 提供完整的音频情感分析解决方案

### 0.1.4
- 添加sayTest004函数（语音识别ASR代码示例）
- 添加sayTest005函数（语音合成TTS代码示例）
- 完善语音技术相关功能
- 优化文档结构

### 0.1.3
- 添加sayTest003系列函数（完整的情感分析项目代码示例）
- 包含数据集处理、CNN模型、训练和预测的完整代码
- 优化代码结构和文档

### 0.1.2
- 添加sayTest002函数（语音增强和评分代码示例）
- 增强音频处理功能
- 优化代码结构

### 0.1.1
- 恢复utils模块功能
- 完善所有工具函数
- 修复导入问题

### 0.1.0
- 初始版本
- 添加sayHello函数 