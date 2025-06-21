# 人脸自动打马赛克工具

基于 MediaPipe 实现的高精度人脸检测和自动马赛克处理工具，支持图片和视频处理，**完美保留原始音频**。

## ✨ 核心特性

- 🎯 **高精度人脸检测**：基于 Google MediaPipe，识别准确率高
- 🎬 **视频音频保留**：处理视频时完美保留原始音频轨道
- 🖼️ **多格式支持**：支持图片(JPG/PNG/BMP等)和视频(MP4/AVI/MOV等)
- 📁 **批量处理**：支持目录批量处理，提高工作效率
- ⚙️ **灵活配置**：可调节检测置信度、马赛克大小等参数
- 🚀 **高性能**：优化的处理算法，快速完成大批量任务

## 🛠️ 环境要求

### 推荐环境配置
- **Python**: 3.11+ (推荐使用虚拟环境)
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 建议 4GB+ RAM
- **存储**: 根据处理文件大小预留足够空间

### 虚拟环境安装（推荐）

```bash
# 创建Python 3.11虚拟环境
conda create -n face_mosaic_py311 python=3.11 -y

# 激活环境
conda activate face_mosaic_py311

# 安装依赖
pip install -r requirements.txt
```

### 快速安装
```bash
# 克隆项目
git clone <repository-url>
cd face_mosaic

# 安装依赖
pip install -r requirements.txt
```

## 📦 依赖包说明

| 包名 | 版本要求 | 功能 |
|------|----------|------|
| mediapipe | >=0.10.0,<0.11.0 | 人脸检测核心引擎 |
| opencv-python | >=4.8.0,<5.0.0 | 图像视频处理 |
| numpy | >=1.24.0,<2.0.0 | 数值计算（兼容版本） |
| ffmpeg-python | >=0.2.0 | 音频处理和合并 |
| tqdm | >=4.65.0 | 进度条显示 |

**⚠️ 注意**: numpy 版本限制在 2.0 以下以确保与 mediapipe 兼容。

## 🚀 使用方法

### 基础命令

```bash
# 处理单张图片
python face_mosaic.py --input photo.jpg --output processed_photo.jpg

# 处理视频（保留音频）
python face_mosaic.py --input video.mp4 --output processed_video.mp4

# 处理视频（不保留音频）
python face_mosaic.py --input video.mp4 --output processed_video.mp4 --no-audio

# 批量处理图片目录
python face_mosaic.py --input ./images/ --output ./processed_images/

# 🚀 批量并发处理视频文件夹（推荐）
python face_mosaic.py --batch-folder ./videos/ --max-workers 4

# 自定义并发数的批量处理
python face_mosaic.py --batch-folder ./videos/ --max-workers 2 --confidence 0.3
```

### 高级参数

```bash
# 自定义参数处理
python face_mosaic.py \
    --input video.mp4 \
    --output output.mp4 \
    --confidence 0.3 \
    --mosaic-size 30
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | str | 必填 | 输入文件或目录路径 |
| `--output` | str | 必填 | 输出文件或目录路径 |
| `--confidence` | float | 0.5 | 人脸检测置信度 (0.0-1.0) |
| `--mosaic-size` | int | 20 | 马赛克块大小，越小越精细 |
| `--no-audio` | flag | False | 禁用音频保留（仅输出视频） |
| `--batch-folder` | str | - | 批量处理文件夹路径 |
| `--max-workers` | int | 4 | 最大并发处理数 (1-16) |

## 🎵 音频处理功能

### 工作原理
1. **音频检测**: 自动检测输入视频是否包含音频轨道
2. **分离处理**: 先处理视频帧，同时提取原始音频
3. **智能合并**: 使用 FFmpeg 将处理后视频与原始音频完美合并
4. **自动清理**: 处理完成后自动清理临时文件

### 音频支持特性
- ✅ 保留原始音频质量
- ✅ 支持多种音频编码格式
- ✅ 自动时间轴同步
- ✅ 智能错误恢复
- ✅ 临时文件自动管理

## 🚀 批量并发处理功能

### 核心特性
- **🔄 多线程并发**：同时处理多个视频，3-4倍效率提升
- **🎯 智能文件管理**：自动生成`_processed`后缀文件
- **⚡ 断点续传**：自动跳过已处理文件，避免重复工作
- **📊 实时监控**：详细的进度条和统计报告
- **🔒 线程安全**：每个线程独立MediaPipe检测器，避免状态冲突

### 使用方式
```bash
# 批量处理文件夹内所有视频
python face_mosaic.py --batch-folder /path/to/videos/

# 自定义并发数（根据CPU核心数调整）
python face_mosaic.py --batch-folder /path/to/videos/ --max-workers 8

# 结合其他参数使用
python face_mosaic.py --batch-folder /path/to/videos/ --max-workers 4 --confidence 0.3 --no-audio
```

### 智能文件命名
- **输入**：`video.mp4` → **输出**：`video_processed.mp4`
- **输入**：`movie.avi` → **输出**：`movie_processed.avi`
- **自动跳过**：已存在的`*_processed.*`文件

### 性能优化建议
| CPU核心数 | 推荐并发数 | 预期加速比 |
|-----------|------------|------------|
| 4核心 | 2-3 | 2-2.5倍 |
| 8核心 | 4-6 | 3-4倍 |
| 16核心+ | 6-8 | 4-5倍 |

**⚠️ 注意**：并发数不宜过高，避免内存不足或系统过载。

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

## 🔧 故障排除

### 常见问题

**Q: 提示 "ffmpeg-python 未安装"**
```bash
# 解决方案
pip install ffmpeg-python>=0.2.0
```

**Q: 音频合并失败**
```bash
# 检查 FFmpeg 是否正确安装
ffmpeg -version

# 使用 --no-audio 选项仅处理视频
python face_mosaic.py --input video.mp4 --output output.mp4 --no-audio
```

**Q: numpy 版本冲突**
```bash
# 安装兼容版本
pip install "numpy>=1.24.0,<2.0.0"
```

**Q: MediaPipe 初始化失败**
```bash
# 重新安装 MediaPipe
pip uninstall mediapipe
pip install mediapipe>=0.10.0,<0.11.0
```

**Q: 批量处理内存不足**
```bash
# 降低并发数
python face_mosaic.py --batch-folder ./videos/ --max-workers 2

# 或者单线程处理
python face_mosaic.py --batch-folder ./videos/ --max-workers 1
```

**Q: 批量处理速度慢**
```bash
# 根据CPU核心数调整并发数
python face_mosaic.py --batch-folder ./videos/ --max-workers 6

# 禁用音频处理提升速度
python face_mosaic.py --batch-folder ./videos/ --max-workers 4 --no-audio
```

**Q: 批量处理马赛克闪烁**
```bash
# v2.1.1已修复线程安全问题，确保使用最新版本
# 线程安全模式会自动启用，每个线程使用独立检测器
python face_mosaic.py --batch-folder ./videos/ --max-workers 2
```

### 环境问题

**虚拟环境激活失败**
```bash
# 确认 conda 可用
conda --version

# 重新创建环境
conda create -n face_mosaic_py311 python=3.11 -y
conda activate face_mosaic_py311
```

**依赖冲突解决**
```bash
# 清理并重新安装
pip uninstall -y mediapipe opencv-python numpy
pip install -r requirements.txt
```

## 📋 更新历史

### v2.1.1 (2025-06-21)
- 🔧 **修复**: 批量并发处理中的马赛克闪烁问题
- 🔒 **增强**: 线程安全处理，每个线程独立MediaPipe检测器
- 💪 **优化**: 工厂模式设计，彻底隔离线程状态
- 📊 **改进**: 线程安全模式实时提示

### v2.1.0 (2025-06-21)
- 🚀 **新增**: 批量并发处理功能
- ⚡ **新增**: 多线程并发支持，3-4倍效率提升
- 🎯 **新增**: 智能文件管理和断点续传
- 📊 **新增**: 实时进度监控和详细统计报告
- 🔒 **优化**: 线程安全和错误隔离机制
- 🎛️ **新增**: --batch-folder 和 --max-workers 参数

### v2.0.0 (2025-01-20)
- ✅ **新增**: 完整音频保留功能
- ✅ **新增**: FFmpeg 集成支持
- ✅ **优化**: 虚拟环境兼容性
- ✅ **修复**: numpy 2.0 兼容性问题
- ✅ **增强**: 错误处理和用户提示
- ✅ **添加**: 临时文件自动管理

### v1.0.0 (2025-01-19)
- ✅ 基础人脸检测和马赛克功能
- ✅ 图片和视频处理支持
- ✅ 批量处理功能
- ✅ 命令行参数配置

## 📞 技术支持

如遇到问题，请提供以下信息：
1. Python 版本 (`python --version`)
2. 系统环境 (Windows/macOS/Linux)
3. 错误日志完整内容
4. 使用的命令和参数

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**🎯 现在开始体验高质量的人脸马赛克处理，音频完美保留！** 