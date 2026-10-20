# AiWritingLegado — Legado 书源开发技能包

一套给 **AI 智能体和人** 使用的 [Legado（阅读）](https://github.com/gedoor/legado) 书源开发工具包：规则手册 + 知识库 + 真实案例 + Python 调试器。

目标很简单：**换一个 AI、换一个人，读完入口文档也能写出能导入、能搜索、能读正文的书源。**

> **给 AI 智能体（从这里开始）**：按 [`skill/SKILL.md`](skill/SKILL.md) 的流程工作；按任务查 [`knowledge/README.md`](knowledge/README.md)；开工前扫 [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md)；交付前用 [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) 自检。本仓库不依赖任何专用 MCP 工具。
>
> **使用约束**：不要改动项目的目录结构（不要移动、重命名、删除或重组现有目录和文件）；不要修改 [`book_sources/`](book_sources/) 中与本次任务无关的书源文件。只有用户明确要求修改时才动。
>
> 三条最容易违反的规则：书源名只用纯中文；`bookSourceGroup` 用 `""`；`nextContentUrl` 只用于同章下一页。

> 本项目基于 [DandanLLab/legadoSkill](https://github.com/DandanLLab/legadoSkill) 修改和扩充。

---

## 这个项目解决什么问题

Legado 通过 JSON 格式的“书源”抓取网站内容。写书源需要同时处理：

- CSS / Default / XPath / JSONPath / 正则 / JS 规则
- GET/POST、编码、Header、Cookie、动态 Token
- 目录分页、正文分页、懒加载封面
- Cloudflare / WAF / WebView / 移动端 API / 加密响应

本项目把这些知识整理成 AI 可以直接读的文档，并提供一个**近似模拟** Legado 行为的 Python 调试器，方便在导入真机前先跑一遍。

---

## 快速开始

### 给 AI 智能体

把仓库交给它，然后说：

> 按 `skill/SKILL.md` 的流程，为 `<网址>` 写一个 Legado 书源。

推荐阅读顺序：

1. [`skill/SKILL.md`](skill/SKILL.md) — **工作流程 + 硬性规范（最重要）**
2. [`knowledge/README.md`](knowledge/README.md) — 按任务查语法和模板
3. [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) — 已知坑
4. [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) — 交付前自检

> 本仓库**不依赖任何专用 MCP 工具**。AI 只需要能读文件、发 HTTP 请求、执行 Python。

### 给人类

```bash
# 1. 安装调试器依赖
pip install -r debugger/requirements.txt

# 2. 测试一个已有书源
python debugger/debugger_cli.py test book_sources/起点中文.json --keyword "斗破苍穹"

# 3. 分阶段测试
python debugger/debugger_cli.py search  book_sources/起点中文.json --keyword "斗破苍穹"
python debugger/debugger_cli.py info    book_sources/起点中文.json --url "https://m.qidian.com/book/1209977/"
python debugger/debugger_cli.py toc     book_sources/起点中文.json --url "https://m.qidian.com/book/1209977/"
python debugger/debugger_cli.py content book_sources/起点中文.json --url "<章节URL>"

# 4. 机器可读输出
python debugger/debugger_cli.py search book_sources/起点中文.json --keyword "斗破苍穹" --output json
```

生成的书源放入 [`book_sources/`](book_sources/)；临时 HTML、调试脚本放入 `temp/`（不提交）。

---

## 书源硬性规范（摘要）

完整版见 [`skill/SKILL.md`](skill/SKILL.md)。

1. **命名**：`bookSourceName` 只用纯中文名称（如 `绅士漫画`、`起点中文`）。禁止域名、后缀、Emoji。
2. **分组**：`bookSourceGroup` 默认空字符串 `""`，由用户在 App 里自行分组。
3. **内置浏览**：需要打开网页时用 `java.startBrowser(url, title)` 或 `java.showBrowser(url)`。禁止跳系统外部浏览器。
4. **正文分页**：`nextContentUrl` 只用于**同一章的下一页**（`text.下一页@href`）。下一章由阅读 App 根据目录自动处理，**不要**填“下一章”链接。
5. **目录分页**：`ruleToc.nextTocUrl` 用于目录页的“下一页/下一分页”。
6. **JSON 输出**：必须是标准 JSON 数组 `[...]`，无注释、无尾随逗号、无 Markdown 包裹。
7. **不存在的字段**：正文规则没有 `prevContentUrl`。
8. **选择器**：优先使用 `text.文本`、`class.xxx`、数字索引 `.0` / `.-1`；不要依赖 `:contains()`。
9. **JS 兼容**：Legado 使用 Rhino 1.8.0。不要调用未注入的 Java 方法（如 `java.randomUUID()`）；从 `java.getString()` / `java.ajax()` 拿到的字符串先用 `String(...)` 包装。
10. **WAF**：常规站点 `loginCheckJs` 保持为空；不要用全局模糊关键字判断拦截，详见 [`docs/WAF拦截与弹窗死循环分析及规避指南.md`](docs/WAF拦截与弹窗死循环分析及规避指南.md)。
11. **发现页排版**：分组标题独占一行且**不写 `url`**；手机端分类按钮一行 2 个（`layout_flexBasisPercent: 0.46`），不要用 `0.23` 排四列，否则中文分类名会被截断。完整写法见 [`skill/SKILL.md`](skill/SKILL.md)。

---

## 当前成品书源

| 文件 | 名称 | 类型 | 说明 |
|---|---|---|---|
| [`起点中文.json`](book_sources/起点中文.json) | 起点中文 | 文字 | 移动端搜索 + 请求头/WAF 适配 + 懒加载封面兜底 |
| [`起点图网.json`](book_sources/起点图网.json) | 起点图网 | 文字 | 网文数据/榜单/书单，非正文站 |
| [`禁漫天堂.json`](book_sources/禁漫天堂.json) | 禁漫天堂 | 图片 | 高防漫画站、WebView、图片解密 |
| [`绅士漫画.json`](book_sources/绅士漫画.json) | 绅士漫画 | 图片 | PC 模板 + 动态域名/发布页 + 登录 + 图片线路自动切换 + 搜索筛选（`关键词|cate=9`）+ 合集目录 |

参考稿和变体（未按最终命名规范整理）在 [`knowledge/reference/书源变体/`](knowledge/reference/书源变体/)。

`bookSourceType` 取值：`0` 文字、`1` 音频、`2` 图片、`3` 文件、`4` 视频。

---

## 目录结构

```text
AiWritingLegado/
├── README.md                      # 本文件（AI 入口 + 项目总览）
├── skill/
│   ├── SKILL.md                   # AI 工作手册（主文档）
│   ├── examples/                  # 4 类典型书源示例（HTML/API/动态API/WAF）
│   └── skill-creator/             # 技能评测/迭代工具
├── knowledge/
│   ├── README.md                  # 知识库导航
│   ├── 书源规则教程.md             # 规则教程（先读）
│   ├── legado_knowledge_base.md   # 数据结构 + 全语法速查
│   ├── css选择器规则.txt           # 选择器补充笔记
│   ├── 书源输出模板_严格模式.md     # JSON 模板与字段清单
│   ├── 真实书源模板库.txt          # 可改写模板
│   ├── 真实书源高级功能分析.md      # jsLib/loginUi/解密等
│   ├── 方法-JS扩展类.md            # java.* 方法
│   ├── 方法-加密解密.md            # MD5/AES/DES/RSA
│   ├── 方法-登录检查JS.md          # loginUrl/loginCheckJs/loginUi
│   ├── 书源实战日记.md             # 真实开发笔记
│   ├── 订阅源规则帮助.txt           # 订阅源规则
│   ├── Legado知识库.txt            # 一页纸速查
│   └── reference/                  # 真实书源、提示词、编码指南等
├── docs/
│   ├── README.md                  # 排错文档导航
│   ├── BUG_FIXES.md               # 修复日志（开工先扫）
│   ├── FINAL_CHECKLIST.md         # 提交前检查清单
│   ├── TOC_PAGINATION_RULES.md    # 目录分页
│   ├── WAF拦截与弹窗死循环分析及规避指南.md
│   ├── 移动端API与加密书源避坑指南.md
│   ├── 禁漫天堂与高防漫画站书源实战避坑指南.md
│   └── 案例-歌书网与起点图网.md     # 单站完整案例合集
├── book_sources/                  # 成品书源 JSON
├── debugger/
│   ├── debugger_cli.py            # 调试器命令行入口
│   ├── engine/                    # 规则解析、请求、调试、自动修复
│   ├── js_engine/                 # JS 近似执行
│   ├── environment_simulator.py   # 运行环境模拟
│   ├── legado_checker.py          # 检查本地 Legado 源码
│   ├── json_output.py             # JSON 落盘工具
│   ├── test_cases.py              # 测试用例框架
│   └── requirements.txt
├── assets/
│   ├── knowledge_base/book_sources/       # 134 份真实书源分析
│   ├── book_source_database/book_sources/ # 5 份原始书源 JSON
│   ├── 真实书源分析结果.json
│   ├── 阅读源码.txt                        # Legado 源码文档（约 14 MB）
│   ├── 元素选择浏览器参考。.txt
│   ├── 核心视图工具.txt
│   ├── 神秘的参考.txt
│   ├── eruda.js / user.js / 仿M浏览器元素审查.user.js / 傲娇的验证大佬v0.2.js
│   └── 动态加载.txt
└── archive/                       # 旧智能体资料、历史版本、重复文件（不使用）
```

---

## 调试器说明

调试器用 Python 近似实现 Legado 的规则解析，支持：

- CSS / Default / XPath / JSONPath / 正则
- 搜索、详情、目录、正文四个阶段
- GET/POST、Header、Cookie、编码
- 简单 JS 规则（基于 Python 的近似执行）

**它不能 100% 还原 Android + Rhino 的行为。** 典型差异：

- `<js>` 规则、`java.webView`、复杂 Rhino 特性可能不准
- 部分懒加载/JS 渲染页面拿不到真实 DOM
- 个别选择器在 Python 解析器里成功、真机失败（或相反）

遇到模拟结果和预期不符时：

1. 不要反复改规则碰运气；
2. 读 [`assets/阅读源码.txt`](assets/阅读源码.txt) 或克隆官方源码到 `legado/`；
3. 仍不确定就明确告诉用户“需要在 Legado App 中真机验证”，并给出验证步骤。

```bash
git clone https://github.com/gedoor/legado.git legado/
```

---

## 文档地图

| 想做什么 | 去哪里 |
|---|---|
| 让 AI 开始写书源 | [`skill/SKILL.md`](skill/SKILL.md) |
| 查规则语法 | [`knowledge/书源规则教程.md`](knowledge/书源规则教程.md)、[`knowledge/legado_knowledge_base.md`](knowledge/legado_knowledge_base.md) |
| 看输出模板 | [`knowledge/书源输出模板_严格模式.md`](knowledge/书源输出模板_严格模式.md)、[`skill/examples/`](skill/examples/) |
| 查已知坑 | [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) |
| 提交前自检 | [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) |
| 处理 WAF/验证码 | [`docs/WAF拦截与弹窗死循环分析及规避指南.md`](docs/WAF拦截与弹窗死循环分析及规避指南.md) |
| 处理移动端 API/加密 | [`docs/移动端API与加密书源避坑指南.md`](docs/移动端API与加密书源避坑指南.md) |
| 处理漫画/高防站 | [`docs/禁漫天堂与高防漫画站书源实战避坑指南.md`](docs/禁漫天堂与高防漫画站书源实战避坑指南.md) |
| 看完整单站排查案例 | [`docs/案例-歌书网与起点图网.md`](docs/案例-歌书网与起点图网.md) |
| 找相似真实书源 | [`assets/knowledge_base/book_sources/`](assets/knowledge_base/book_sources/) |
| 看历史旧资料 | [`archive/`](archive/)（**不要当现行规范**） |

---

## 维护约定

1. **主文档只有两份**：`README.md`（项目总览）和 `skill/SKILL.md`（AI 工作手册）。新规则优先补进这两份，不要把同一份内容抄到多个文件。
2. **知识细节**放 `knowledge/`，按 [`knowledge/README.md`](knowledge/README.md) 的导航归档。
3. **排错案例**放 `docs/`，结构固定为：现象 → 根因 → 修复 → 可推广经验。
4. 每修复一个真实书源问题，在 [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) 补一条摘要。
5. **docs 去重**：同一主题只保留一个入口；单站案例优先合并进现有案例集，不要新建平行文档。
   已废弃的方案不要直接删光，在 `BUG_FIXES` 的“历史尝试（已废弃）”里留一段警示即可。
6. 旧智能体资料、历史技能版本、重复文件统一放 `archive/`，不参与日常检索。
7. 不要在仓库里提交 `__pycache__`、`temp/`、`legado/`、日志文件。

---

## 来源与致谢

- 原始技能包：[DandanLLab/legadoSkill](https://github.com/DandanLLab/legadoSkill)
- Legado 官方仓库：[gedoor/legado](https://github.com/gedoor/legado)
- 知识库中的真实书源分析来自公开书源整理，仅用于学习规则写法；请遵守目标网站的服务条款和当地法律。

---

*文档整理：2026-10-20。入口文档：[`skill/SKILL.md`](skill/SKILL.md)。*
