# Image Drive - 功能说明

## 📸 图像上传失败的解决方案

### 问题原因
上传失败通常是因为缺少必要的依赖：
1. **CLIP模型** - 用于图像特征提取和语义搜索
2. **Tesseract OCR** - 用于图像文字识别
3. **其他Python依赖** - torch, scikit-learn等

### 解决步骤

#### 方法1：使用自动安装脚本（推荐）
```bash
# 停止当前服务器 (Ctrl+C)

# 激活虚拟环境
source venv/bin/activate

# 运行安装脚本
./install_dependencies.sh

# 重新启动服务器
python app.py
```

#### 方法2：手动安装
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装Python依赖
pip install --upgrade pip
pip install Flask Flask-SQLAlchemy Werkzeug Pillow numpy scikit-learn pytesseract

# 安装PyTorch (CPU版本)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装CLIP模型
pip install ftfy regex tqdm
pip install git+https://github.com/openai/CLIP.git

# 安装Tesseract OCR (系统级别)
# macOS:
brew install tesseract

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# Windows:
# 从这里下载安装: https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 🔍 相似图像搜索 - 工作原理

### 重要说明：**不使用在线ImageNet数据库**

你的系统**完全离线运行**，相似图像搜索只在**你自己上传的图片库**中进行。

### 工作流程

#### 1. 图像上传时（utils.py:53-79）
```
上传图片 → CLIP模型提取特征向量(512维) → 存储到数据库
```

每张图片会被转换为一个512维的特征向量（embedding），这个向量包含了图片的语义信息。

#### 2. 相似图像搜索（gallery.html:17-20, 133-151）

**位置**：在Gallery页面的"Similar Image Search"按钮

**步骤**：
```
1. 用户上传查询图片
2. 系统计算查询图片的特征向量
3. 与数据库中所有图片的特征向量进行相似度比较（余弦相似度）
4. 返回相似度最高的图片
```

**代码位置**：
- 前端：`templates/gallery.html:133-151`
- 后端：`app.py:254-273`
- 相似度计算：`utils.py:125-181`

#### 3. 语义搜索（Semantic Search）

**位置**：Gallery页面的"Semantic Search"输入框

**工作原理**：
```
输入文本描述 → CLIP将文本转为特征向量 →
与图片特征向量比较 → 返回匹配的图片
```

例如：
- 输入 "a dog playing" → 找到狗的图片
- 输入 "sunset landscape" → 找到风景图片

---

## 🎯 三种搜索方式对比

| 搜索类型 | 输入 | 搜索范围 | 依赖 |
|---------|------|---------|------|
| **语义搜索** | 文字描述 | 你上传的所有图片 | CLIP模型 |
| **相似图像搜索** | 上传图片 | 你上传的所有图片 | CLIP模型 + sklearn |
| **OCR搜索** | 文字 | 图片中的文字内容 | Tesseract OCR |

---

## 💡 关于CLIP模型

**CLIP (Contrastive Language-Image Pre-training)** 是OpenAI开发的AI模型：

- **预训练**：模型已经在4亿张图片上训练完成
- **本地运行**：下载到你的电脑后，完全离线运行
- **不联网**：不需要连接ImageNet或任何在线数据库
- **模型大小**：ViT-B/32约350MB

### 首次使用时
第一次运行时，系统会自动下载CLIP模型：
```
~/.cache/clip/ViT-B-32.pt  (~350MB)
```

---

## 🖼️ 图像分类（Auto Categorization）

上传图片时，系统会自动分类到这些类别之一（utils.py:302-339）：

- flowers (花卉)
- food (食物)
- cars (汽车)
- dogs (狗)
- road signs (道路标志)
- buildings (建筑)
- landscapes (风景)
- birds (鸟类)
- electronics (电子产品)
- people (人物)

这个分类也是通过CLIP模型的语义理解能力实现的。

---

## 📊 数据存储

所有数据都存储在本地：

```
project/
├── instance/image_drive.db    # SQLite数据库（图片元数据和特征向量）
├── uploads/                   # 上传的原始图片
├── logs/                      # 系统日志
└── temp/                      # 临时文件
```

**不会上传到任何在线服务！**

---

## 🔧 故障排查

### 上传显示"Upload failed"

1. **检查日志**：
```bash
tail -50 logs/app.log
```

2. **查看终端输出**：运行服务器的终端窗口会显示详细错误

3. **常见错误**：
   - `CLIP model not available` → 运行 `./install_dependencies.sh`
   - `Tesseract not available` → 安装Tesseract OCR（OCR功能会禁用，但上传仍可工作）
   - `sklearn not available` → 运行 `pip install scikit-learn`

### 相似搜索不工作

确保：
1. ✓ CLIP模型已安装
2. ✓ scikit-learn已安装
3. ✓ 至少上传了2张图片（需要有对比的图片）

---

## 📝 总结

- ✅ 完全本地运行，不联网
- ✅ 使用你自己的图片库
- ✅ CLIP模型提供强大的语义理解能力
- ✅ 所有数据都在你的电脑上

如果还有问题，请查看 `logs/app.log` 中的详细错误信息！
