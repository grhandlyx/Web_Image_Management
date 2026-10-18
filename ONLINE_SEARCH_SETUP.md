# 🌐 在线图像搜索 - 配置指南

## 重要说明

**ImageNet不是在线搜索数据库！** ImageNet是一个图像分类数据集，用于训练AI模型，不提供在线搜索服务。

本系统使用的是**免费的在线图片库API**，包括：
- **Unsplash** - 1000万+高质量图片
- **Pexels** - 数百万免费图片
- **Pixabay** - 数百万免费图片

---

## 🚀 快速开始（推荐：Unsplash）

### 步骤1：注册Unsplash开发者账号

1. 访问 https://unsplash.com/developers
2. 点击 "Register as a developer"
3. 登录或创建账号
4. 创建一个新应用（Application）
   - Application name: `Image Drive`
   - Description: `Personal image search application`
5. 获取 **Access Key**（类似：`abc123xyz...`）

### 步骤2：配置API密钥

有两种方式配置：

#### 方法A：环境变量（推荐）

在终端中运行：
```bash
# 在macOS/Linux
export UNSPLASH_ACCESS_KEY="你的Access_Key"

# 或者添加到 ~/.bashrc 或 ~/.zshrc 永久保存
echo 'export UNSPLASH_ACCESS_KEY="你的Access_Key"' >> ~/.zshrc
source ~/.zshrc
```

#### 方法B：直接修改config.py

编辑 `config.py` 文件：
```python
# 找到这一行
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or ''

# 改为
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or '你的Access_Key'
```

⚠️ **注意**：方法B不要提交到Git！将 `config.py` 添加到 `.gitignore`

### 步骤3：安装requests库

```bash
pip install requests
```

### 步骤4：重启服务器

```bash
# 停止当前服务器 (Ctrl+C)
python app.py
```

### 步骤5：测试在线搜索

1. 访问 http://localhost:5000
2. 在搜索框旁边的下拉菜单选择 **"Online"** 或 **"Both (Hybrid)"**
3. 输入搜索词，如 "sunset"
4. 点击 "Search"
5. 你会看到来自Unsplash的在线图片！

---

## 📊 API限制对比

| 平台 | 免费限额 | 注册难度 | 图片质量 | 推荐指数 |
|------|---------|---------|---------|---------|
| **Unsplash** | 50请求/小时 | ⭐⭐ 简单 | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐⭐⭐⭐ |
| **Pexels** | 200请求/小时 | ⭐⭐ 简单 | ⭐⭐⭐⭐ 很好 | ⭐⭐⭐⭐ |
| **Pixabay** | 100请求/分钟 | ⭐ 最简单 | ⭐⭐⭐ 良好 | ⭐⭐⭐ |

---

## 🔧 配置多个API（可选）

如果你想同时使用多个平台，获取更多结果：

### Pexels配置

1. 访问 https://www.pexels.com/api/
2. 点击 "Get Started" → 注册账号
3. 获取 **API Key**
4. 配置：
```bash
export PEXELS_API_KEY="你的API_Key"
```

### Pixabay配置

1. 访问 https://pixabay.com/api/docs/
2. 注册账号
3. 获取 **API Key**
4. 配置：
```bash
export PIXABAY_API_KEY="你的API_Key"
```

---

## 🎯 搜索模式说明

在Gallery页面的搜索框旁边，你会看到一个下拉菜单：

### 1. Local Library（本地库）
- 仅搜索你自己上传的图片
- 使用CLIP模型进行语义匹配
- 速度最快，完全离线

### 2. Online（在线）
- 仅搜索在线图片库（Unsplash/Pexels/Pixabay）
- 需要配置API密钥
- 可获取海量高质量图片
- **这就是你要的在线搜索！**

### 3. Both (Hybrid)（混合模式）✨ **推荐**
- 同时搜索本地和在线
- 结果分为两个部分显示：
  - 📁 Local Results（本地结果）
  - 🌐 Online Results（在线结果）
- 最全面的搜索体验

---

## 🔍 使用示例

### 搜索狗的图片
1. 选择搜索模式：**Online** 或 **Both (Hybrid)**
2. 输入：`dog playing in park`
3. 点击 **Search**
4. 结果会显示在线图片库中的狗图片

### 搜索风景照片
1. 选择：**Online**
2. 输入：`mountain landscape sunset`
3. 获取Unsplash的高质量风景照片

### 对比本地和在线结果
1. 选择：**Both (Hybrid)**
2. 输入：`cat`
3. 看到：
   - 你上传的猫图片（本地）
   - Unsplash的猫图片（在线）

---

## ❌ 故障排查

### 问题1：提示"Online search not configured"

**原因**：没有配置API密钥

**解决**：
```bash
# 检查环境变量
echo $UNSPLASH_ACCESS_KEY

# 如果为空，设置它
export UNSPLASH_ACCESS_KEY="你的密钥"

# 重启服务器
python app.py
```

### 问题2：搜索返回空结果

**可能原因**：
- API密钥错误
- 网络连接问题
- 达到API限制

**检查日志**：
```bash
tail -50 logs/app.log
```

### 问题3：`ModuleNotFoundError: No module named 'requests'`

**解决**：
```bash
pip install requests
```

---

## 📝 环境变量完整示例

创建一个 `.env.sh` 文件（不要提交到Git）：

```bash
#!/bin/bash
# Image Drive API Keys Configuration

# Unsplash API (推荐)
export UNSPLASH_ACCESS_KEY="your_unsplash_access_key_here"

# Pexels API (可选)
export PEXELS_API_KEY="your_pexels_api_key_here"

# Pixabay API (可选)
export PIXABAY_API_KEY="your_pixabay_api_key_here"
```

然后每次运行前加载：
```bash
source .env.sh
python app.py
```

---

## 🎨 图片来源和版权

所有在线搜索返回的图片都来自：
- **Unsplash** - 完全免费使用，无需署名（但推荐）
- **Pexels** - 完全免费使用，无需署名
- **Pixabay** - 完全免费使用，无需署名

这些平台的图片都可用于商业和个人用途！

---

## 💡 高级配置

### 修改搜索结果数量

编辑 `config.py`：
```python
# 默认20张
ONLINE_SEARCH_LIMIT = 20

# 改为50张
ONLINE_SEARCH_LIMIT = 50
```

### 禁用在线搜索

编辑 `config.py`：
```python
ENABLE_ONLINE_SEARCH = False
```

### 指定默认搜索提供商

编辑 `config.py`：
```python
# 可选: 'unsplash', 'pexels', 'pixabay', 'all'
DEFAULT_ONLINE_PROVIDER = 'unsplash'
```

---

## 🚀 开始使用

1. ✅ 安装依赖：`pip install requests`
2. ✅ 获取Unsplash API密钥（5分钟）
3. ✅ 配置环境变量
4. ✅ 重启服务器
5. ✅ 选择"Online"搜索模式
6. ✅ 享受海量在线图片！

**你现在可以搜索全球1000万+高质量图片了！** 🎉
