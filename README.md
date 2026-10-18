# AiWritingLegado — Legado书源开发AI技能包

> 一个为AI智能体量身定制的Legado阅读APP书源开发技能包，内含知识库、调试引擎和全套规范。

---

## 这个项目是什么？

**AiWritingLegado** 是一套给AI（Trae、Claude、GPT等）使用的Legado书源开发工具包。

Legado（开源阅读APP）通过JSON格式的"书源"来抓取小说网站内容，书源开发需要深入理解CSS/XPath选择器、正则表达式、JavaScript、HTTP请求分析等知识。这个项目把这些知识系统化地组织起来，让AI可以高质量地完成书源开发工作。

项目包含：
- **AI技能文件**（`skill/SKILL.md`）：AI的完整工作指南，包含工作流程、规则、注意事项
- **知识库**（`knowledge/`）：书源开发所需的所有技术文档
- **调试引擎**（`debugger/`）：Python实现的Legado规则模拟调试工具
- **参考书源**（`book_sources/`）：已完成的书源JSON文件

---

## 快速开始

### 激活AI技能

将 `skill/SKILL.md` 的内容放入AI的**系统提示词**或**技能配置**中（支持 Antigravity, Claude Code, Cursor, Windsurf, ChatGPT, Trae 等任意环境）：

- **主技能文件**：`skill/SKILL.md` 直接启用
- **技能评测工具**：`tools/skill-creator/` 辅助生成与评估

### 使用调试引擎

```bash
# 测试书源
python debugger/test_universal.py book_sources/起点中文网.json -k 斗破苍穹

# 指定URL测试
python debugger/test_universal.py book_sources/起点中文网.json --url https://...
```

---

## 完整目录结构

```
AiWritingLegado/
├── .gitignore                      # Git忽略规则
├── assets/                         # 知识库核心资源（保持原路径供代码引用）
│   ├── knowledge_base/book_sources/# 1751个真实书源案例（参考数据库）
│   ├── knowledge_index.json        # 知识索引（代码引用）
│   ├── learned_sources.json        # 学习记录
│   ├── metadata.json               # 元数据
│   ├── eruda.js                    # 移动端调试工具
│   ├── user.js                     # 用户脚本基础库
│   ├── 仿M浏览器元素审查.user.js   # 元素审查工具
│   ├── 傲娇的验证大佬v0.2.js       # 验证码处理工具
│   ├── 阅读源码.txt               # Legado源码文档（14MB，代码引用）
│   ├── 元素选择浏览器参考。.txt    # 元素选择参考（2.8MB）
│   ├── 核心视图工具.txt            # 视图工具（1.7MB）
│   └── 神秘的参考.txt             # 参考资料（220KB）
├── book_sources/                   # 📦 所有完成的书源JSON输出
│   ├── 起点中文网.json
│   ├── 番茄小说.json
│   ├── 无限小说网.json
│   ├── 笔趣阁bqgui.json
│   └── 顶点小说.json
├── config/
│   ├── system_prompt.md            # 完整系统提示词（67KB）
│   ├── system/prompt.md            # 详细提示词规范
│   └── agent_llm_config.json       # LLM配置
├── debugger/                       # 🔧 Python模拟调试引擎
│   ├── test_universal.py           # 通用测试入口
│   ├── engine/
│   │   ├── debug_engine.py         # 调试引擎主类
│   │   ├── analyze_rule.py         # 规则分析器（CSS/XPath/JSON/Regex/JS）
│   │   ├── book_source.py          # 书源数据模型
│   │   ├── web_book.py             # 网页获取器
│   │   ├── auto_fixer.py           # 自动修复迭代
│   │   ├── analyze_url.py          # URL分析器
│   │   ├── file_organizer.py       # 文件整理器
│   │   └── kotlin_reference/       # Kotlin源码参考
│   └── legado_checker.py           # Legado仓库检查器
├── docs/                           # 📚 技术文档和开发报告
│   ├── AI_AGENT_WORKFLOW.md        # AI Agent工作流与开发规范
│   ├── ESSENTIAL_KNOWLEDGE_SUMMARY.md  # 精华知识汇总（必读）
│   ├── FINAL_CHECKLIST.md          # 书源最终检查清单
│   ├── LEGADO_DEBUGGER.md          # 调试器使用文档
│   ├── PROJECT_ARCHITECTURE.md     # 项目架构说明
│   └── ...（其他技术报告）
├── knowledge/                      # 📖 核心知识库
│   ├── css选择器规则.txt           # CSS选择器完整手册（80KB）
│   ├── 书源规则教程.md             # 从入门到入土详细教程（39KB）
│   ├── 真实书源模板库.txt           # 可直接用的书源模板
│   ├── 真实书源高级功能分析.md      # 134个真实书源分析
│   ├── 智能体自我认知.md            # AI能力和约束说明
│   ├── 方法-JS扩展类.md            # java对象JS方法
│   ├── 方法-加密解密.md            # 加密解密方法
│   ├── 方法-登录检查JS.md          # 登录验证JS
│   ├── Legado知识库.txt            # 知识速查
│   ├── 订阅源规则帮助.txt           # 订阅源开发
│   ├── 书源输出模板_严格模式.md     # 严格输出模板
│   ├── 书源实战日记.md             # 实战案例笔记
│   ├── legado_knowledge_base.md    # 综合知识库
│   └── reference/                  # 参考资料
│       ├── 3a.json参考.txt         # 实际书源参考
│       ├── TapManga.json参考.txt
│       ├── 霹雳书屋.json参考.txt
│       ├── 写源辅助AI提示词.txt    # 其他AI写源提示词
│       ├── 书源日记231224.txt      # 经验日记
│       └── ...（更多参考）
├── legado/                         # Legado官方Kotlin源码（需要时克隆）
│   └── （git clone https://github.com/gedoor/legado.git）
├── skill/                          # 🎯 AI技能包
│   ├── SKILL.md                    # 当前生效技能（v0.7，主文件）
│   ├── examples/                   # 经典书源实战案例库（起点WAF/段评范例等）
│   └── history/                    # 历史版本
│       ├── SKILLV0.1.md ~ SKILLV0.7.md
├── tools/                          # 🛠️ 辅助工具集
│   └── skill-creator/              # 技能自动创建、测试与评估工具包
├── temp/                           # 🗑 临时工作区（内容不纳入版本控制）
└── README.md                       # 本文件
```

---

## 核心组件说明

### 🎯 skill/SKILL.md — AI主技能文件

AI的完整工作指南，包含：
- 核心原则（官方Kotlin源码优先）
- 标准工作流程（5阶段：需求分析→网站分析→规则开发→调试验证→输出）
- 书源JSON字段规范（必填/选填/禁用字段）
- CSS/XPath/正则选择器规范
- 常见错误和自我检查清单

**如何更新**：直接在 `skill/SKILL.md` 中编辑优化，或借助 `tools/skill-creator` 工具链进行评估优化。

---

### 📖 knowledge/ — 核心知识库

| 文件 | 内容 |
|------|------|
| `css选择器规则.txt` | CSS选择器完整手册，Legado特有语法 |
| `书源规则教程.md` | 从入门到入土的详细教程（主力参考） |
| `真实书源模板库.txt` | 可直接使用的书源模板 |
| `真实书源高级功能分析.md` | 134个真实书源深度分析 |
| `智能体自我认知.md` | AI工具清单、能力边界、约束条件 |
| `方法-JS扩展类.md` | Legado内置Java对象JS调用方法 |
| `方法-加密解密.md` | MD5/Base64/AES等加密方法 |
| `方法-登录检查JS.md` | CF防护、登录验证的JS处理 |
| `书源输出模板_严格模式.md` | 规范的书源JSON输出格式 |
| `书源实战日记.md` | 真实开发经验记录 |
| `reference/` | 参考书源文件、提示词、其他资料 |

---

### 🔧 debugger/ — Python调试引擎

模拟Legado的规则解析行为，支持：
- CSS选择器、XPath、JSONPath、正则表达式
- JavaScript执行（近似模拟Rhino引擎）
- 自动修复迭代

```bash
# 基本用法
python debugger/test_universal.py <书源.json> -k <搜索关键词>

# 完整参数
python debugger/test_universal.py book_sources/起点中文网.json -k 斗破苍穹 --verbose
```

> ⚠️ **重要**：调试引擎是近似实现，不能100%还原Legado行为。
> 如有疑问，以 `legado/` 目录的Kotlin源码为准，或在真实APP中测试。

---

### 📦 book_sources/ — 书源输出目录

所有完成的书源JSON文件放在此目录。

**命名规范**：`<网站名称>.json`，例如：`起点中文网.json`

**提交前检查**：
1. 在Legado APP中实际导入测试
2. 搜索、目录、正文均正常
3. 确认JSON格式正确（无注释、无尾随逗号）

---

### 🗃️ assets/ — 大文件知识库

保持原路径，主要供调试引擎代码引用：
- `knowledge_base/book_sources/`：1751个真实书源参考数据库
- `阅读源码.txt`：Legado完整源码文档（14MB）
- 各种调试辅助脚本

---

## 书源输出规范

1. **最终书源JSON放入** `book_sources/` 目录
2. **临时工作文件放入** `temp/` 目录，完成后清理
3. **严格JSON格式**：无注释、无尾随逗号、所有字符串用双引号
4. **必填字段**：`bookSourceUrl`, `bookSourceName`, `bookSourceType`, `searchUrl`, `ruleSearch`, `ruleBookInfo`, `ruleToc`, `ruleContent`

---

## 给下一个AI的交接说明

### 📋 启动时必读顺序

```
1. skill/SKILL.md                          ← AI工作指南（最重要）
2. knowledge/智能体自我认知.md              ← 了解工具和约束
3. docs/ESSENTIAL_KNOWLEDGE_SUMMARY.md     ← 精华技巧汇总
4. knowledge/书源规则教程.md               ← 技术规则详解（按需）
```

### 🔧 调试引擎使用

```bash
python debugger/test_universal.py <书源文件> -k <关键词>
```

如果模拟失败，先查 `legado/` 的Kotlin源码，再告诉用户去APP测试。

### 📂 legado/ 源码目录

首次使用需要克隆：
```bash
git clone https://github.com/gedoor/legado.git legado/
```

已在 `.gitignore` 中忽略，不会被提交。

### 🗑️ temp/ 工作区

临时文件放 `temp/`，每次任务完成后清理：
- 调试中间输出
- 测试脚本
- 临时书源版本

### 📝 技能版本管理

- 当前版本：`skill/SKILL.md`（v0.7）
- 范例用例：`skill/examples/`
- 历史版本：`skill/history/`

---

*本项目由人工 + AI协作构建，持续迭代优化中。*
