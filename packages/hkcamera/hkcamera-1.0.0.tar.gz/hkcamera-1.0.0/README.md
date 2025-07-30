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