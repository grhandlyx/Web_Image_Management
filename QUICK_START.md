# 🎉 在线图像搜索已启用！

## ⚡ 快速开始（2分钟）

### 1️⃣ 安装依赖
```bash
pip install requests
```

### 2️⃣ 获取免费API密钥
访问 **https://unsplash.com/developers** → 注册 → 创建应用 → 复制Access Key

### 3️⃣ 配置密钥
```bash
export UNSPLASH_ACCESS_KEY="粘贴你的密钥"
```

### 4️⃣ 启动应用
```bash
python app.py
# 或使用快速启动脚本：
./start_with_online_search.sh
```

### 5️⃣ 使用在线搜索
1. 打开 http://localhost:5000
2. 在搜索框旁选择 **"Online"** 或 **"Both (Hybrid)"**
3. 输入 `sunset` 或 `dog` 然后搜索
4. 🎊 享受来自Unsplash的百万张高质量图片！

---

## 📖 详细配置

请查看：**[ONLINE_SEARCH_SETUP.md](ONLINE_SEARCH_SETUP.md)**

---

## 🔍 三种搜索模式

| 模式 | 说明 | 使用场景 |
|-----|------|---------|
| **Local Library** | 只搜索你上传的图片 | 管理个人图片库 |
| **Online** | 只搜索在线图库（Unsplash等） | 寻找新图片灵感 |
| **Both (Hybrid)** ⭐ | 同时搜索本地+在线 | 最全面的搜索 |

---

## ❓ 关于ImageNet的说明

**ImageNet不是在线搜索数据库！**

- ImageNet是一个用于训练AI模型的数据集
- 它不提供公开的搜索API
- 本系统使用的是Unsplash/Pexels等免费图库，拥有更多更好的图片

---

## 🆚 在线搜索 vs 本地搜索

### 本地搜索（Local）
- ✅ 完全离线，速度快
- ✅ 搜索你自己的图片
- ✅ 使用CLIP AI模型语义理解
- ❌ 图片数量取决于你的上传

### 在线搜索（Online）
- ✅ 1000万+高质量图片
- ✅ 专业摄影师作品
- ✅ 免费使用（遵守各平台许可）
- ❌ 需要网络连接
- ❌ 有API请求限制（免费版：50次/小时）

### 混合搜索（Hybrid）⭐ 推荐
- ✅ 结合两者优势
- ✅ 一次搜索，两种结果
- ✅ 先显示本地，再显示在线

---

## 💡 使用建议

### 场景1：上传狗的照片并找相似的
1. 上传你的 `dog.jpg`
2. 等待上传成功
3. 选择 **"Both (Hybrid)"**
4. 搜索 `dog`
5. 结果：
   - 📁 你上传的狗照片
   - 🌐 Unsplash的狗照片

### 场景2：寻找设计灵感
1. 选择 **"Online"**
2. 搜索 `minimalist interior design`
3. 浏览Unsplash的专业设计照片
4. 点击图片打开原图链接

### 场景3：管理家庭相册
1. 上传家庭照片
2. 选择 **"Local Library"**
3. 搜索 `birthday 2023`
4. 只显示你的家庭照片

---

## 🎯 功能总览

| 功能 | 本地 | 在线 | 状态 |
|-----|------|------|------|
| 语义搜索 | ✅ | ✅ | 已实现 |
| OCR文字搜索 | ✅ | ❌ | 已实现 |
| 相似图像搜索 | ✅ | ❌ | 已实现 |
| 图像分类 | ✅ | ❌ | 已实现 |
| 下载统计 | ✅ | ❌ | 已实现 |
| 用户认证 | ✅ | ✅ | 已实现 |

---

## 🛠️ 故障排查

### 上传失败
```bash
# 安装CLIP模型
./install_dependencies.sh
```
详见：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 在线搜索不可用
```bash
# 检查API密钥
echo $UNSPLASH_ACCESS_KEY

# 如果为空，配置它
export UNSPLASH_ACCESS_KEY="你的密钥"
```
详见：[ONLINE_SEARCH_SETUP.md](ONLINE_SEARCH_SETUP.md)

---

## 📚 文档索引

- **[ONLINE_SEARCH_SETUP.md](ONLINE_SEARCH_SETUP.md)** - 在线搜索完整配置指南
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排查和系统说明
- **[README.md](README.md)** - 原始项目说明

---

## 🚀 立即开始

```bash
# 方法1：快速启动（推荐）
./start_with_online_search.sh

# 方法2：手动启动
export UNSPLASH_ACCESS_KEY="你的密钥"
python app.py
```

打开 http://localhost:5000 开始探索！

---

**祝你使用愉快！** 🎨✨
