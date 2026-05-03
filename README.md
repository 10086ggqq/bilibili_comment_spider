# B站评论爬取工具 🔍

一个安全、高效的B站视频评论爬取工具，支持多种输入格式，内置多重反爬措施。

## ✨ 功能特性

- 🔗 **URL自动提取** - 支持直接粘贴B站链接，自动提取BV号
- 🛡️ **安全增强** - 随机延迟、User-Agent轮换、智能重试等多重反爬措施
- 📊 **数据导出** - 自动保存为CSV格式，包含完整的评论信息
- 🎯 **简单易用** - 命令行和交互式两种使用方式
- 🔒 **隐私保护** - Cookie等敏感信息独立配置，不上传到GitHub

## 📋 支持的输入格式

- BV号: `BV1ofR5B6E72`
- 完整链接: `https://www.bilibili.com/video/BV1ofR5B6E72/?spm_id_from=...`
- 短链接: `https://b23.tv/BV1ofR5B6E72`
- 带参数链接: `https://www.bilibili.com/video/BV1G1421k7WR/?p=1`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置Cookie

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑config.py，填入你的B站Cookie
```

**获取Cookie的方法**：
1. 打开浏览器，访问 https://www.bilibili.com 并登录
2. 按F12打开开发者工具
3. 切换到Network（网络）标签
4. 刷新页面（F5）
5. 点击任意请求，在右侧找到 Request Headers
6. 找到Cookie字段，复制整个值
7. 粘贴到 `config.py` 的 `COOKIE = ""` 引号中

### 3. 运行程序

**命令行方式**：
```bash
# 使用链接
python bilibili_crawler.py "https://www.bilibili.com/video/BV1ofR5B6E72/" 10

# 使用BV号
python bilibili_crawler.py BV1ofR5B6E72 10
```

**交互式方式**：
```bash
python bilibili_crawler.py
```

### 4. 代码调用

```python
from bilibili_crawler import crawl_comments

# 爬取评论
comments = crawl_comments(
    bvid="BV1ofR5B6E72",  # 或完整链接
    max_pages=10,
    safe_mode=True
)

print(f"获取了 {len(comments)} 条评论")
```

## 📊 输出格式

CSV文件包含以下字段：

| 字段 | 说明 |
|------|------|
| 视频标题 | 视频的标题 |
| BV号 | 视频的BV号 |
| 评论ID | 评论的唯一ID |
| 用户名 | 评论用户的昵称 |
| 用户等级 | 用户的等级 |
| 评论内容 | 评论的文本内容 |
| 点赞数 | 评论的点赞数 |
| 回复数 | 评论的回复数 |
| 评论时间 | 评论发布的时间 |
| IP属地 | 评论者的IP属地 |

## 🛡️ 安全特性

### 反爬措施

- ✅ **随机延迟** (2-8秒) - 模拟真实用户行为
- ✅ **User-Agent轮换** - 每10次请求自动切换
- ✅ **请求频率限制** - 避免触发反爬机制
- ✅ **智能重试** - 失败自动重试，最多3次
- ✅ **错误码处理** - 检测到-412自动等待

### 使用建议

- 每次爬取不超过50页
- 每天爬取不超过5个视频
- 两次爬取间隔至少30分钟
- 建议使用小号进行测试

## 📁 项目结构

```
pythoncode/
├── bilibili_comment_spider.py  # 核心爬虫类
├── bilibili_crawler.py         # 主程序入口
├── config.example.py           # 配置模板
├── config.py                   # 配置文件（不上传）
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目说明
├── 安全说明.txt                # 详细安全说明
└── 功能更新总结.txt            # 功能更新记录
```

## ⚙️ 配置说明

### config.py

```python
# B站Cookie配置
COOKIE = "你的Cookie"
```

### 安全配置

```python
# 调整请求间隔
spider.min_interval = 2.5  # 最小间隔（秒）
spider.max_interval = 8.0  # 最大间隔（秒）
```

## 📖 使用示例

### 单个视频爬取

```python
from bilibili_crawler import crawl_comments

comments = crawl_comments(
    bvid="https://www.bilibili.com/video/BV1ofR5B6E72/",
    max_pages=10,
    sort=0,  # 0=按热度, 2=按时间
    output_file="my_comments.csv"
)
```

### 批量爬取

```python
import time
from bilibili_crawler import crawl_comments

video_list = [
    "https://www.bilibili.com/video/BV1ofR5B6E72/",
    "https://www.bilibili.com/video/BV1WE411K7bD",
]

for url in video_list:
    comments = crawl_comments(url, max_pages=5)
    print(f"获取了 {len(comments)} 条评论")
    time.sleep(1800)  # 等待30分钟
```

## ⚠️ 注意事项

1. **Cookie有效期** - Cookie会过期，需要定期更新
2. **合理使用** - 遵守B站用户协议，仅用于学习研究
3. **账号安全** - 建议使用小号，避免使用主账号
4. **隐私保护** - 不要将config.py上传到GitHub

## 🔧 故障排除

### 问题1：未找到config.py

**解决方案**：
```bash
cp config.example.py config.py
# 然后编辑config.py填入Cookie
```

### 问题2：Cookie无效

**解决方案**：
- 重新获取Cookie
- 确保复制了完整的Cookie值
- 检查Cookie是否包含必要字段（SESSDATA, bili_jct等）

### 问题3：请求被拦截

**解决方案**：
- 增加请求间隔时间
- 减少爬取页数
- 等待一段时间后再试

## 📄 许可证

本项目仅供学习研究使用，请遵守相关法律法规和B站用户协议。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请提交Issue。

---

**免责声明**：本工具仅供学习研究使用，使用者需自行承担风险。作者不对任何因使用本工具导致的账号封禁、法律问题等负责。请合理、合法使用。
