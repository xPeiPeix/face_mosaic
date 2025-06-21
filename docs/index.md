---
layout: default
title: 人脸自动打马赛克工具
---

# 人脸自动打马赛克工具

<p align="center">
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python"></a>
<a href="https://mediapipe.dev/"><img src="https://img.shields.io/badge/MediaPipe-0.10+-green.svg" alt="MediaPipe"></a>
<a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-4.8+-orange.svg" alt="OpenCV"></a>
<a href="https://github.com/xPeiPeix/face_mosaic/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License"></a>
<a href="https://github.com/xPeiPeix/face_mosaic/stargazers"><img src="https://img.shields.io/github/stars/xPeiPeix/face_mosaic?style=social" alt="GitHub Stars"></a>
</p>

基于 MediaPipe 实现的高精度人脸检测和自动马赛克处理工具，支持图片和视频处理，**完美保留原始音频**。

## 🚀 快速开始

### 安装
```bash
git clone https://github.com/xPeiPeix/face_mosaic.git
cd face_mosaic
pip install -r requirements.txt
```

### 基础使用
```bash
# 处理单张图片
python face_mosaic.py --input photo.jpg --output processed_photo.jpg

# 处理视频（保留音频）
python face_mosaic.py --input video.mp4 --output processed_video.mp4

# 批量并发处理
python face_mosaic.py --batch-folder ./videos/ --max-workers 4
```

## ✨ 核心特性

- 🎯 **高精度人脸检测**：基于 Google MediaPipe，识别准确率高
- 🎬 **视频音频保留**：处理视频时完美保留原始音频轨道
- 🖼️ **多格式支持**：支持图片(JPG/PNG/BMP等)和视频(MP4/AVI/MOV等)
- 📁 **批量处理**：支持目录批量处理，提高工作效率
- ⚙️ **灵活配置**：可调节检测置信度、马赛克大小等参数
- 🚀 **高性能**：并发处理，3-4倍效率提升

## 🎵 音频处理功能

### 工作原理
1. **音频检测**: 自动检测输入视频是否包含音频轨道
2. **分离处理**: 先处理视频帧，同时提取原始音频
3. **智能合并**: 使用 FFmpeg 将处理后视频与原始音频完美合并
4. **自动清理**: 处理完成后自动清理临时文件

## 🚀 批量并发处理

### 核心优势
- **🔄 多线程并发**：同时处理多个视频，3-4倍效率提升
- **🎯 智能文件管理**：自动生成`_processed`后缀文件
- **⚡ 断点续传**：自动跳过已处理文件，避免重复工作
- **📊 实时监控**：详细的进度条和统计报告
- **🔒 线程安全**：每个线程独立MediaPipe检测器，避免状态冲突

### 性能表现

| CPU核心数 | 推荐并发数 | 预期加速比 |
|:----------|:-----------|:-----------|
| 4核心     | 2-3        | 2-2.5倍    |
| 8核心     | 4-6        | 3-4倍      |
| 16核心+   | 6-8        | 4-5倍      |

## 📊 性能基准

### 测试环境
- **CPU**: Intel i7 / AMD Ryzen 7
- **内存**: 16GB RAM
- **视频**: 1280x720, 30FPS, 约1分钟

### 处理性能
- **处理速度**: 约 93 帧/秒
- **人脸检测**: 平均每帧检测 1-2 张人脸
- **内存占用**: 峰值约 2GB
- **音频延迟**: <1秒（合并阶段）

## 📚 项目文档

- [项目源码和详细说明](https://github.com/xPeiPeix/face_mosaic)

## 📄 许可证

本项目采用 [MIT 许可证](https://github.com/xPeiPeix/face_mosaic/blob/main/LICENSE)。

---

<div align="center">
Made with ❤️ by <a href="https://github.com/xPeiPeix">xPeiPeix</a>
</div> 