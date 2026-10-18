# 🎯 API密钥获取教程 - 超详细版

## 什么是API密钥？

**API密钥**就像一把钥匙，让你的应用可以访问Unsplash网站的图片数据库。

**不需要付费！完全免费！**

---

## 📝 第一步：注册Unsplash开发者账号（5分钟）

### 1. 打开网站

在浏览器中访问：**https://unsplash.com/developers**

### 2. 注册账号

- 如果你已有Unsplash账号 → 点击 **"Log in"**
- 如果没有账号 → 点击 **"Join free"** 注册一个

注册信息：
- 邮箱地址
- 密码
- 名字

### 3. 进入开发者页面

登录后，你会看到页面顶部有一个按钮：**"Register as a developer"**

点击它！

### 4. 同意开发者条款

会弹出一个页面，让你同意Unsplash的API使用条款。

勾选复选框 → 点击 **"Accept terms"**

---

## 🔑 第二步：创建应用并获取密钥（2分钟）

### 1. 点击"New Application"

在开发者页面，你会看到一个按钮：**"New Application"** 或 **"Create Application"**

点击它！

### 2. 填写应用信息

会出现一个表单，填写以下信息：

```
Application name（应用名称）:
  → 填写: Image Drive

Description（描述）:
  → 填写: Personal image search application for learning

Accept Terms（同意条款）:
  → 勾选所有复选框
```

然后点击 **"Create application"**

### 3. 获取Access Key

创建成功后，你会进入应用详情页面。

在页面中间，你会看到：

```
Keys
├── Access Key: [一串长长的字符，类似: abc123xyz456...]
└── Secret Key: [另一串字符]
```

**只需要复制 "Access Key" 这一串字符！**

例如：`xYz9pQmN3k7dFgH2jLsT8vBwC1eR4uI5oA6tP0q`

---

## ⚙️ 第三步：配置到你的应用（1分钟）

### 方法A：临时配置（本次运行有效）

打开终端（Terminal），输入：

```bash
export UNSPLASH_ACCESS_KEY="粘贴你刚才复制的Access Key"
```

**注意**：
- 把 `粘贴你刚才复制的Access Key` 替换成你实际复制的那串字符
- 要保留引号 `""`

例如：
```bash
export UNSPLASH_ACCESS_KEY="xYz9pQmN3k7dFgH2jLsT8vBwC1eR4uI5oA6tP0q"
```

按Enter键执行。

### 方法B：永久配置（推荐）

#### macOS/Linux用户：

1. 打开终端
2. 编辑配置文件：
```bash
nano ~/.zshrc
```

3. 在文件末尾添加：
```bash
export UNSPLASH_ACCESS_KEY="你的Access_Key"
```

4. 保存并退出：
   - 按 `Ctrl + O` → 保存
   - 按 `Enter` → 确认
   - 按 `Ctrl + X` → 退出

5. 让配置生效：
```bash
source ~/.zshrc
```

#### Windows用户：

1. 打开命令提示符（CMD）或PowerShell
2. 设置环境变量：
```cmd
setx UNSPLASH_ACCESS_KEY "你的Access_Key"
```

3. 关闭并重新打开命令提示符

### 方法C：直接写在代码里（不推荐，但最简单）

1. 打开项目文件夹中的 `config.py`
2. 找到这一行：
```python
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or ''
```

3. 改成：
```python
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or '你的Access_Key'
```

例如：
```python
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') or 'xYz9pQmN3k7dFgH2jLsT8vBwC1eR4uI5oA6tP0q'
```

4. 保存文件

**⚠️ 警告**：如果你要把代码上传到GitHub，**不要使用方法C**！否则别人会看到你的密钥。

---

## ✅ 第四步：验证配置是否成功

### 1. 检查密钥是否设置成功

在终端输入：
```bash
echo $UNSPLASH_ACCESS_KEY
```

如果显示你的密钥（那一串字符），说明配置成功！

如果什么都不显示，说明配置失败，重新执行第三步。

### 2. 启动应用

```bash
# 确保在项目目录
cd /Users/cicid/Desktop/project

# 启动应用
python app.py
```

### 3. 测试在线搜索

1. 打开浏览器，访问：http://localhost:5000
2. 登录你的账号
3. 在搜索框旁边的下拉菜单选择 **"Online"**
4. 输入：`sunset`
5. 点击 **"Search"**

如果看到很多漂亮的日落照片，说明**配置成功**！🎉

如果提示"Online search not configured"，说明配置失败，回到第三步重新配置。

---

## 🔍 完整示例流程

```bash
# 1. 设置API密钥（替换成你自己的）
export UNSPLASH_ACCESS_KEY="xYz9pQmN3k7dFgH2jLsT8vBwC1eR4uI5oA6tP0q"

# 2. 验证设置成功
echo $UNSPLASH_ACCESS_KEY
# 应该显示：xYz9pQmN3k7dFgH2jLsT8vBwC1eR4uI5oA6tP0q

# 3. 安装requests库（如果还没装）
pip install requests

# 4. 启动应用
python app.py

# 5. 打开浏览器访问 http://localhost:5000
```

---

## ❓ 常见问题

### Q1: 我找不到"Register as a developer"按钮

**A**: 确保你已经登录Unsplash账号。访问：https://unsplash.com/oauth/applications

### Q2: 创建应用后找不到Access Key

**A**: 在应用列表中，点击你刚创建的应用名称，进入详情页就能看到。

### Q3: 配置后还是显示"not configured"

**A**:
1. 检查密钥有没有复制完整（不要有空格）
2. 确保引号是英文的 `""` 不是中文的 `""`
3. 重启终端，重新设置环境变量
4. 重启应用 `python app.py`

### Q4: 可以不配置吗？

**A**: 可以！但是：
- 你只能使用"Local Library"模式（搜索你自己上传的图片）
- 无法使用"Online"和"Hybrid"模式

### Q5: 这个API要钱吗？

**A**: 完全免费！限制是每小时50次请求，对个人使用完全够用。

---

## 🎯 快速配置脚本

如果你觉得上面太复杂，用这个一键配置脚本：

```bash
# 运行快速配置脚本
./start_with_online_search.sh
```

脚本会：
1. 检查requests库是否安装
2. 引导你输入API密钥
3. 自动配置环境变量
4. 启动应用

---

## 📞 还有问题？

如果按照上面步骤还是不行，告诉我：

1. 你在哪一步卡住了？
2. 运行 `echo $UNSPLASH_ACCESS_KEY` 显示什么？
3. 运行 `python app.py` 后终端显示什么错误？

我会帮你解决！

---

## 🎉 配置成功的标志

当你看到：

1. 终端显示：`* Running on http://127.0.0.1:5000`
2. 浏览器能访问 http://localhost:5000
3. 选择"Online"搜索模式
4. 搜索"sunset"能看到漂亮的照片

**恭喜！你成功了！** 🚀
