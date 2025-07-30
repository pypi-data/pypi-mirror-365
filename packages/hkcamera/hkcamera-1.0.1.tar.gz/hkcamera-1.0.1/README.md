# HKCamera Package

这是一个独立的Python包，用于与海康威视摄像头SDK进行交互。

## 安装

```bash
pip install .
```

## 使用方法

```python
from camera import HKCam

# 创建摄像头对象
with HKCam('192.168.1.64', 'admin', 'password') as cam:
    if cam.isOpened():
        # 读取帧
        timestamp, frame = cam.read()
        # 处理帧
        # ...
    else:
        print("无法打开摄像头")
```

## 依赖

- numpy
- opencv-python

## 注意事项

1. 需要安装海康威视SDK库文件
2. 仅支持Windows和Linux系统
3. 需要正确的摄像头IP地址、用户名和密码

## 库文件

此包已包含所有必需的海康威视库文件，支持以下平台：

- Windows 32位
- Windows 64位
- Linux 32位
- Linux 64位

无需用户手动下载和放置库文件。

## 运行示例

我们提供了一个示例脚本 `example.py` 来演示如何使用这个包：

```bash
python example.py
```

请注意，示例脚本不会实际连接到摄像头，因为这需要真实的设备。在实际使用中，您需要提供有效的摄像头IP地址、用户名和密码，并确保已将海康威视的库文件放入相应的目录。

## 构建和分发

我们提供了一个构建脚本 `build_dist.py` 来简化包的构建和分发过程：

```bash
# 清理构建目录
python build_dist.py clean

# 构建分发包
python build_dist.py build

# 检查构建的分发包
python build_dist.py check

# 执行完整流程（清理、构建、检查）
python build_dist.py
```

构建的包将位于 `dist` 目录中，包括 wheel (.whl) 和源码 (.tar.gz) 格式。