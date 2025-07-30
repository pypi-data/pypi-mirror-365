# AI Tools

一个简单的Python工具包，提供基础的AI相关工具函数。

## 安装

```bash
pip install lchpersonal-ai-tools
```

## 使用方法

```python
from ai_tools import sayHello, sayTest001, sayTest002

# 基础问候
sayHello()  # 输出: hello world!

# 显示音频处理代码示例
sayTest001()  # 输出音频特征提取代码

# 显示语音增强和评分代码示例
sayTest002()  # 输出语音增强代码
```

## 功能

- `sayHello()`: 输出 "hello world!" 消息
- `sayTest001()`: 显示音频特征提取代码示例
- `sayTest002()`: 显示语音增强和评分代码示例

## 要求

- Python 3.7+
- 可选依赖：librosa, matplotlib, numpy（用于音频处理功能）

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