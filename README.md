# kjrb - 科技新闻日报 🌍

> 自动聚合全球科技新闻，**自动翻译成中文**，每天 9 点发送到你的邮箱

## ✨ 核心特性

- ✅ **完全免费** - 使用开源 RSS 和公共 API，无任何费用
- ✅ **自动聚合** - 每天自动从 20+ 权威源收集新闻
- ✅ **智能翻译** - 英文新闻自动翻译成中文，中文新闻保持原样
- ✅ **中英文混合** - 支持国际权威源和中文科技媒体
- ✅ **无需付费 API** - 不依赖 NewsAPI，使用 RSS 源和公开接口
- ✅ **11 大分类** - AI、机器人、基础科学、物理、生物、化学、医疗、航空航天、心理学、社会学、信息工程
- ✅ **智能排序** - 根据权威性、关键词、时效性自动排序
- ✅ **邮件发送** - 每日 9:00 北京时间自动发送
- ✅ **美观格式** - HTML 邮件格式，包含分类、摘要、来源、原文链接
- ✅ **历史记录** - 所有日报自动保存在仓库

## 📚 信息源（20+ 源）

### 国际学术/科学源（6个）
- [Nature](https://nature.com) - 世界顶级学术期刊
- [Science Magazine](https://science.org) - 科学杂志
- [ArXiv AI/ML](https://arxiv.org/list/cs.AI) - 预印本库（AI/机器学习）
- [ArXiv Physics](https://arxiv.org/list/physics.gen-ph) - 预印本库（物理）
- [Phys.org](https://phys.org) - 物理学资讯
- [ScienceDaily](https://sciencedaily.com) - 科学日报

### 国际工程/技术源（3个）
- [IEEE Spectrum](https://spectrum.ieee.org) - IEEE 电气工程学会
- [MIT News](https://news.mit.edu) - MIT 官方新闻
- [Stanford News](https://news.stanford.edu) - 斯坦福大学新闻

### 国际科技媒体（3个）
- [TechCrunch](https://techcrunch.com) - 科技创新报道
- [The Verge](https://theverge.com) - 科技评论
- [Hacker News](https://news.ycombinator.com) - Y Combinator 社区

### 国际综合新闻（2个）
- [BBC Science](http://bbc.co.uk/news) - BBC 科学版块
- [Reddit r/science](https://reddit.com/r/science) - Reddit 科学社区

### 中文科技媒体（3个）🇨🇳
- [36氪](https://36kr.com) - 科技创业、新产品发布
- [机器之心](https://jiqizhixin.com) - AI、深度学习专业媒体
- [InfoQ](https://infoq.cn) - 技术资讯、开发者新闻

### 中文科学资讯（3个）🇨🇳
- [科学网新闻](http://sciencenet.cn) - 学术研究突破
- [���壳网](https://guokr.com) - 科学普及、生活科技
- [新浪科技](https://sina.com.cn) - 综合科技新闻

## 🌐 翻译功能

### 智能翻译方案（混合模式）：

✨ **自动语言检测**
- 中文新闻：保持原样，不重复翻译
- 英文新闻：自动翻译成中文

✨ **翻译显示**
- 主标题和摘要显示中文版本
- 英文原标题显示在下方（灰色小字）
- 点击"查看原文"可阅读完整英文内容

✨ **高效翻译**
- 使用免费翻译 API（MyMemory）
- 自动缓存避免重复翻译
- 翻译失败时优雅降级（显示原文）

### 邮件效果示例：

```
🌍 科技新闻日报
2026年6月11日 | 精选全球中英文科技资讯（自动翻译）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ [AI] DeepMind 发布最新 AI 模型，性能突破新高
   📌 原文标题: DeepMind Announces Breakthrough AI Model
   重要度：95/100
   摘要：Google DeepMind 宣布推出新一代AI模型，在多项基准测试中刷新纪录...
   来源：Nature
   查看原文 →

2️⃣ [机器人] 自动化技术在制造业中的新应用
   重要度：88/100
   摘要：最新研究表明机器人技术在制造业应用越来���广泛...
   来源：机器之心
   查看原文 →

... 共 20 条
```

## 🚀 30 秒快速开始

### 第 1 步：获取 Gmail 应用密码（如果需要邮件功能）

**✅ 启用两步验证：** https://myaccount.google.com/security

**✅ 生成应用密码：** https://myaccount.google.com/apppasswords
- 选择 App: **Mail**
- 选择 Device: **Windows Computer**（或你的设备）
- 获得 16 位密码（格式：`xxxx xxxx xxxx xxxx`）

### 第 2 步：配置 GitHub Secrets

**🔗 打开：** https://github.com/jiandanaiken/kjrb/settings/secrets/actions

**➕ 添加 3 个 Secret：**

| Secret 名称 | 值 |
|-----------|-----|
| `SENDER_EMAIL` | 你的 Gmail 地址 |
| `SMTP_PASSWORD` | 上面获得的 16 位密码 |
| `TARGET_EMAIL` | 接收邮件的邮箱（任意邮箱） |

### 第 3 步：测试运行

**🧪 手动触发：**
1. 进入仓库 → **Actions** 标签
2. 选择 **📰 每日科技新闻日报** 工作流
3. 点击 **Run workflow** → **Run workflow**

⏳ 等待 2-3 分钟，检查你的邮箱

## ⏰ 自动运行时间

默认配置：**每天北京时间 9:00** 自动运行

**修改运行时间：** 编辑 `.github/workflows/daily_news.yml` 中的 `cron` 字段

**Cron 时间对照表：**
```
北京时间    →    UTC    →    Cron 表达式
9:00        →    1:00   →    0 1 * * *
12:00       →    4:00   →    0 4 * * *
18:00       →   10:00   →    0 10 * * *
21:00       →   13:00   →    0 13 * * *
```

## 🔧 本地运行

想要在本地电脑测试？

```bash
# 1. 克隆仓库
git clone https://github.com/jiandanaiken/kjrb.git
cd kjrb

# 2. 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建 .env 文件（可选）
cp .env.example .env
# 编辑 .env，填入你的邮件配置（可以不填）

# 5. 运行
python news_aggregator.py
```

## 📊 工作原理

```
RSS 源 → 并行抓取 → 去重处理 → 自动分类 → 重要度评分 → 翻译处理 → 排序选取 → 生成报告 → 发送邮件
 20+     (10-30秒)  (全部)    (11类)     (0-100分)   (英文→中文)  (Top 20)  (HTML)    (SMTP)
```

## 🎯 新闻重要度计算

系统根据以下因素计算评分（0-100）：

| 因素 | 加分 |
|-----|-----|
| 来自 Nature/Science | +20 |
| 来自 IEEE/MIT | +15 |
| 来自 ArXiv | +12 |
| 来自中文权威源（机器之心/科学网） | +12 |
| 包含 "突破/Nobel" | +20 |
| 包含 "发现/首次" | +12 |
| 包含 "新纪录" | +10 |
| 最近发布 | +5 |

## 📁 仓库结构

```
kjrb/
├── .github/
│   └── workflows/
│       └── daily_news.yml          # GitHub Actions 工作流配置
├── news_aggregator.py              # 主聚合脚本（含翻译功能）
├── requirements.txt                # Python 依赖
├── .env.example                    # 环境变量示例
├── .gitignore                      # Git 忽略规则
├── README.md                       # 本文件
└── reports/                        # 生成的日报（自动创建）
    ├── report_20260611_090000.html
    ├── report_20260612_090000.html
    └── ...
```

## ❓ 常见问题

### Q: 邮件功能是必须的吗？
**A:** 不是必须的。即使不配置邮件，脚本仍会生成 HTML 报告并保存到仓库的 `reports/` 目录。你可以手动查看。

### Q: 可以改成其他邮箱发送吗？
**A:** 可以，但推荐用 Gmail（已测试）。其他邮箱需要 SMTP 服务器地址和应用专用密码。

### Q: 邮件未收到怎么办？
**A:** 
1. 检查 GitHub Secrets 是否正确配置
2. 查看 GitHub Actions 日志是否有错误
3. 检查垃圾邮件文件夹
4. 确保 Gmail 应用专用密码正确（应为 16 位）

### Q: 翻译效果不好怎么办？
**A:** 
1. 翻译使用免费 API（MyMemory），准确度可能不完美
2. 每条新闻都有"查看原文"链接，可以查看英文原文
3. 如果需要更好的翻译，可以使用付费翻译 API（修改代码）

### Q: 支持其他语言翻译吗？
**A:** 目前只支持中英文混合翻译。如需其他语言，可修改 `TranslationHelper` 类的参数。

### Q: 新闻源不够或效果不好？
**A:** 可以在 `news_aggregator.py` 中的 `RSS_FEEDS` 字典添加更多 RSS 源。

### Q: 运行时需要多久？
**A:** 通常 2-3 分钟（比之前多 30 秒是翻译时间），取决于网络速度和信息源响应时间。

### Q: 为什么没有获取到 20 条新闻？
**A:** 可能原因：
- 网络连接问题
- 某些信息源暂时不可用
- 获取到的新闻重复度高（系统自动去重）

## 📝 许可证

MIT License

## 🤝 反馈和改进

有建议或问题？欢迎提交 Issue 或 Pull Request！

---

**最后更新**：2026-06-11  
**版本**：v2.0（新增中文信息源和自动翻译）  
**状态**：✅ 完全可用

**快速链接**：
- [GitHub 仓库](https://github.com/jiandanaiken/kjrb)
- [Gmail 应用密码](https://myaccount.google.com/apppasswords)
- [GitHub Secrets 配置](https://github.com/jiandanaiken/kjrb/settings/secrets/actions)
