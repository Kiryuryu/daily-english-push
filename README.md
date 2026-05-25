# 每日英语新闻推送

基于 GitHub Actions 的每日英语学习推送系统，通过 Server酱 推送到微信。

## 功能特点

- **BBC Learning English 早间推送**：每天早上 7:00 推送适合英语学习的短文、词汇和练习
- **Reuters 晚间新闻推送**：每天晚上 21:30 推送国际新闻英文阅读材料
- **每周汇总**：每周日 22:00 自动生成本周学习汇总

## 推送时间

| 类型 | 北京时间 | 内容 |
|------|----------|------|
| BBC Learning English | 每天 07:00 | 英语学习短文、词汇、练习 |
| Reuters News | 每天 21:30 | 国际新闻阅读、重点表达 |
| Weekly Summary | 周日 22:00 | 本周词汇复盘、主题总结 |

## 快速开始

### 1. Fork 本仓库

点击右上角 Fork 按钮。

### 2. 配置 GitHub Secrets

进入你的仓库 → Settings → Secrets and variables → Actions → New repository secret

添加以下 Secrets：

| 名称 | 说明 | 获取方式 |
|------|------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | [DeepSeek 官网](https://platform.deepseek.com/) |
| `SERVERCHAN_SENDKEY` | Server酱 SendKey | [Server酱官网](https://sct.ftqq.com/) |

### 3. 启用 GitHub Actions

进入 Actions 标签页，启用 workflow。

### 4. 手动测试

在 Actions 页面选择 "Daily English Push" workflow，点击 "Run workflow"，选择任务类型运行。

## 项目结构

```
daily-english-push/
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions 配置
├── src/
│   ├── main.py                # 主程序入口
│   ├── fetchers/
│   │   ├── bbc.py             # BBC 抓取模块
│   │   └── reuters.py         # Reuters 抓取模块
│   ├── llm/
│   │   └── deepseek.py        # DeepSeek API 客户端
│   ├── push/
│   │   └── serverchan.py      # Server酱推送模块
│   ├── storage/
│   │   └── local_store.py     # 本地存储模块
│   └── weekly/
│       └── summary.py         # 周报生成模块
├── data/
│   ├── daily/                 # 每日数据存储
│   └── weekly/                # 周报数据存储
├── requirements.txt           # Python 依赖
└── README.md
```

## 推送内容示例

### BBC 早间推送

```markdown
# BBC Learning English 今日阅读

## 一句话概括
本文讨论了人工智能对未来工作的影响。

## English Summary
Artificial intelligence is transforming the workplace...

## 今日重点词汇
- **transform**: 转变
  - 语境含义：彻底改变
  - 例句：AI is transforming how we work.
  - 搭配：transform into

## 今日小练习
1. AI is _____ the way we work.
   A. changing
   B. transforming
   C. converting
   D. transferring
   
   答案：B
```

### Reuters 晚间推送

```markdown
# Reuters 晚间英文新闻

## 今日新闻
Global Tech Summit Discusses AI Regulation
原文链接：https://...

## 中文背景
全球科技峰会在日内瓦召开，讨论人工智能监管问题...

## English Summary
World leaders gathered at the Global Tech Summit...

## 高价值表达
- **geopolitical tension**: 地缘政治紧张局势
- **regulatory framework**: 监管框架

## 适合背的句子
1. The summit addressed the growing need for international cooperation on AI governance.
```

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DEEPSEEK_API_KEY="your-api-key"
export SERVERCHAN_SENDKEY="your-sendkey"

# 运行测试
python src/main.py --task bbc
python src/main.py --task reuters
python src/main.py --task weekly
```

## 注意事项

1. **推送去重**：系统会自动检测已推送的文章，避免重复推送
2. **错误处理**：推送失败时会记录日志，不会中断整个流程
3. **数据存储**：每日推送内容会保存到 `data/` 目录，用于生成周报

## License

MIT
