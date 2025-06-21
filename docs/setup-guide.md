# GitHub仓库设置操作指南

## 📄 启用GitHub Pages

### 步骤1：访问仓库设置
1. 打开GitHub仓库页面：https://github.com/xPeiPeix/face_mosaic
2. 点击顶部的 **Settings** 标签
3. 在左侧菜单找到 **Pages** 选项

### 步骤2：配置页面源
1. 在 **Source** 下拉菜单中选择 **Deploy from a branch**
2. 在 **Branch** 下拉菜单中选择 **main**
3. 在 **Folder** 下拉菜单中选择 **/ (root)** 或 **/docs**
4. 点击 **Save** 保存设置

### 步骤3：等待部署
- GitHub会自动构建并部署您的文档站点
- 通常需要几分钟时间完成
- 部署完成后，您的文档站点将在以下地址可用：
  `https://xPeiPeix.github.io/face_mosaic/`

## 🚀 创建v2.1.1 Release版本

### 步骤1：访问Release页面
1. 在GitHub仓库主页，点击右侧的 **Releases** 
2. 点击 **Create a new release** 按钮

### 步骤2：设置标签和版本信息
1. **Tag version**: 输入 `v2.1.1`
2. **Target**: 保持 `main` 分支
3. **Release title**: 输入 `v2.1.1 - 线程安全优化版本`

### 步骤3：编写Release描述
```markdown
## 🔧 修复和优化

### v2.1.1 (2025-01-21)
- 🔧 **修复**: 批量并发处理中的马赛克闪烁问题
- 🔒 **增强**: 线程安全处理，每个线程独立MediaPipe检测器
- 💪 **优化**: 工厂模式设计，彻底隔离线程状态
- 📊 **改进**: 线程安全模式实时提示

## ✨ 主要特性

- 🎯 **高精度人脸检测**：基于 Google MediaPipe
- 🎬 **完美音频保留**：使用FFmpeg智能合并
- 🚀 **批量并发处理**：3-4倍效率提升
- 📁 **智能文件管理**：自动断点续传
- ⚙️ **灵活参数配置**：可调节检测阈值和马赛克大小

## 📦 安装和使用

```bash
# 克隆仓库
git clone https://github.com/xPeiPeix/face_mosaic.git
cd face_mosaic

# 安装依赖
pip install -r requirements.txt

# 基础使用
python face_mosaic.py --input video.mp4 --output processed.mp4

# 批量并发处理
python face_mosaic.py --batch-folder ./videos/ --max-workers 4
```

## 🔧 系统要求

- Python 3.11+
- MediaPipe 0.10+
- OpenCV 4.8+
- FFmpeg (用于音频处理)

## 📚 文档

- [完整文档](https://xPeiPeix.github.io/face_mosaic/)
- [使用教程](README.md)
- [常见问题](docs/faq.md)

**感谢所有用户的支持和反馈！**
```

### 步骤4：完成发布
1. 勾选 **Set as the latest release** (设为最新版本)
2. 如果这是预发布版本，可以勾选 **This is a pre-release**
3. 点击 **Publish release** 完成发布

## ✅ 完成检查清单

- [ ] GitHub Pages已启用并成功部署
- [ ] 文档站点可以正常访问
- [ ] v2.1.1 Release已创建
- [ ] Release包含详细的更新日志
- [ ] 徽章在README中正确显示
- [ ] LICENSE文件已添加

## 🎯 预期效果

完成上述设置后，您的GitHub仓库将具备：

1. **专业外观**：徽章展示技术栈和项目状态
2. **完整文档**：在线文档站点提供详细说明
3. **版本管理**：规范的Release版本发布
4. **法律合规**：明确的开源许可证

---

**注意**：某些设置可能需要几分钟时间生效，请耐心等待。 