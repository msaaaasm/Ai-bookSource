# AiWritingLegado — Legado 书源开发技能包

一套给 **AI 智能体和开发者** 使用的 [Legado（阅读）](https://github.com/gedoor/legado) 书源工业级开发工具包：规则手册 + 架构指南 + 实战避坑库 + Python 仿真调试器。

目标很简单：**换一个 AI、换一个开发者，读完入口文档也能写出能导入、能搜索、能读正文的高质量书源。**

> **给 AI 智能体（从这里开始）**：
> 1. 按 [`skill/SKILL.md`](skill/SKILL.md) 的标准流程开展工作；
> 2. 查阅语法与模板参考 [`knowledge/README.md`](knowledge/README.md)；
> 3. 开工前必须快速通读 [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) 了解已知陷阱；
> 4. 交付前必须对照 [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) 完成逐项自检。
> 5. 本项目不依赖任何专用外部 MCP 工具。
>
> **使用约束**：不要改动项目的核心目录结构；不要修改 [`book_sources/`](book_sources/) 中与本次任务无关的书源文件。
>
> **最容易忽略的三大黄金准则**：
> 1. **详情页路由收敛**：`bookUrlPattern` 必须且只能精准匹配单本详情页，严禁覆盖 `/search`、`/albums`、`/category` 等列表/搜索路由，否则阅读会在搜索阶段提前判定为详情页跳过搜索解析！
> 2. **目录纯净性**：目录专用于章节阅读导航，禁止追加任何讨论、评论、打赏等非正文伪章节，避免影响全书离线缓存与翻页。
> 3. **硬性规范三要素**：书源名称只用纯中文；`bookSourceGroup` 统一保持 `""`；`nextContentUrl` 仅用于**同章下一页**，下一章由阅读 App 自动驱动。

---

## 一、排错与避坑速查表（按异常现象）

遇到书源运行异常时，优先根据下表定位对应文档：

| 异常现象 | 核心根因与陷阱 | 优先阅读排查文档 | 深入原理与实战 |
|---|---|---|---|
| **搜索只出 1 条 / 搜索全空** | `bookUrlPattern` 误命中 `/search`，阅读提前进入单本详情页解析短路列表 | [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md)（绅士漫画） | [`docs/实战案例集-歌书网_起点图网_绅士漫画.md`](docs/实战案例集-歌书网_起点图网_绅士漫画.md) 案例三 |
| **目录含伪章节 / 简介评论获取不到** | 目录混入假章节 `#comments` 破坏纯净性；网页端评论依赖前端异步 AJAX 懒加载（`/ajax/album_pagination`） | [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md)（禁漫天堂） | [`docs/禁漫天堂与高防漫画站书源实战避坑指南.md`](docs/禁漫天堂与高防漫画站书源实战避坑指南.md) 第十二节 |
| **目录只有一部分 / 目录分页失效** | 混淆了 `nextTocUrl`（目录分页）与 `nextContentUrl`（正文分页） | [`docs/TOC_PAGINATION_RULES.md`](docs/TOC_PAGINATION_RULES.md) | [`skill/SKILL.md`](skill/SKILL.md) 1.6 / 4.5 节 |
| **验证弹窗死循环 / 403 / 202 / 503** | `loginCheckJs` 错误使用全局模糊匹配，或者拦截器循环触发 | [`docs/WAF拦截与弹窗死循环分析及规避指南.md`](docs/WAF拦截与弹窗死循环分析及规避指南.md) | 禁漫避坑指南第六节 |
| **移动端 API / 401 / 加密 / 签名失败** | 全局 Header 未同步动态鉴权、JSON 默认值时序逻辑错误、请求未带 Token | [`docs/移动端API与加密书源避坑指南.md`](docs/移动端API与加密书源避坑指南.md) | 禁漫避坑指南第十一节 |
| **高防漫画站 / WebView 超时 / 切片混淆** | `webJs` 空轮询导致 30 次超时白屏；图片使用垂直条带混淆切片 | [`docs/禁漫天堂与高防漫画站书源实战避坑指南.md`](docs/禁漫天堂与高防漫画站书源实战避坑指南.md) | [`book_sources/禁漫天堂.json`](book_sources/禁漫天堂.json) |
| **发现页分类空白 / 点开没内容** | 分类按钮 flexBasisPercent 宽度过窄导致中文截断或布局崩溃 | [`skill/SKILL.md`](skill/SKILL.md) 3.6 节 | [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) |
| **单站综合疑难杂症复盘** | 详情页目录正则贪婪清洗过度、JSoup空格选择器失效、Rhino 类型陷阱 | [`docs/实战案例集-歌书网_起点图网_绅士漫画.md`](docs/实战案例集-歌书网_起点图网_绅士漫画.md) | — |

---

## 二、文档体系导航 (`docs/`)

`docs/` 目录专注沉淀具有可复用价值的书源架构、底层源码机制与踩坑案例：

1. **[`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) — 快速修复日志**
   - 记录最新真实踩坑现象、根本原因、修复方案与关联文档快速索引。开工前必扫。
2. **[`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) — 交付前严选自检清单**
   - 涵盖 JSON 结构、命名规范、字段完整性、正则安全性、网络边界等全方位检查清单。
3. **[`docs/禁漫天堂与高防漫画站书源实战避坑指南.md`](docs/禁漫天堂与高防漫画站书源实战避坑指南.md) — 漫画与高防综合避坑体系**
   - 涵盖 `bookUrlPattern` 判定机制、`webJs` 轮询超时机理、规则优先级丢失、WAF 弹窗循环与 AVS 突破、图片 Lazyload 乱序、纯本地条带 Canvas 解密、纯净正文目录与评论 AJAX 异步双层拉取。
4. **[`docs/移动端API与加密书源避坑指南.md`](docs/移动端API与加密书源避坑指南.md) — 移动端 API 与加密专题**
   - 涵盖动态 Header 初始化时序、AES/DES 解密踩坑、搜索词编码、本地优先解密 + 降级重试架构。
5. **[`docs/WAF拦截与弹窗死循环分析及规避指南.md`](docs/WAF拦截与弹窗死循环分析及规避指南.md) — 防护盾与反爬专题**
   - 深入讲解 Cloudflare、人机验证弹窗防死循环准则、Cookie 持久化机制。
6. **[`docs/TOC_PAGINATION_RULES.md`](docs/TOC_PAGINATION_RULES.md) — 目录与正文分页深潜**
   - 深入剖析 `nextTocUrl` 与 `nextContentUrl` 的本质区别与标准配置格式。
7. **[`docs/实战案例集-歌书网_起点图网_绅士漫画.md`](docs/实战案例集-歌书网_起点图网_绅士漫画.md) — 完整单站案例集**
   - 聚合 **歌书网**（分页字段与正则清洗）、**起点图网**（WAF/越界/404/JSoup/Rhino）、**绅士漫画**（搜索误判与详情路由精准收敛）三大实战复盘。

---

## 三、快速开始

### 1. 给 AI 智能体
提供目标站点并下达指令：
> 请参考 `skill/SKILL.md` 的规范和工作流程，为 `<目标网址>` 编写或修复 Legado 书源。

推荐执行顺序：
1. 阅读 [`skill/SKILL.md`](skill/SKILL.md) 掌握硬性规范；
2. 扫描 [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) 与第一节的避坑速查表；
3. 参考 [`knowledge/README.md`](knowledge/README.md) 获取语法模板；
4. 完成编写后对照 [`docs/FINAL_CHECKLIST.md`](docs/FINAL_CHECKLIST.md) 逐项自查。

### 2. 给人类开发者（本地仿真调试）
```bash
# 1. 安装调试器依赖
pip install -r debugger/requirements.txt

# 2. 端到端测试已有书源
python debugger/debugger_cli.py test book_sources/起点中文.json --keyword "斗破苍穹"

# 3. 分阶段细粒度测试
python debugger/debugger_cli.py search  book_sources/起点中文.json --keyword "斗破苍穹"
python debugger/debugger_cli.py info    book_sources/起点中文.json --url "https://m.qidian.com/book/1209977/"
python debugger/debugger_cli.py toc     book_sources/起点中文.json --url "https://m.qidian.com/book/1209977/"
python debugger/debugger_cli.py content book_sources/起点中文.json --url "<章节URL>"
```

---

## 四、书源核心硬性规范（摘要）

详细要求见 [`skill/SKILL.md`](skill/SKILL.md)：

1. **书源命名**：`bookSourceName` 必须使用纯中文名称（如 `绅士漫画`、`禁漫天堂`）。严禁携带网址、域名后缀或 Emoji。
2. **默认分组**：`bookSourceGroup` 一律设为空字符串 `""`，交由读者在 App 自行分类。
3. **内置跳转**：需唤起网页交互时使用 `java.startBrowser(url, title)` 或 `java.showBrowser(url)`，禁止调用外部浏览器。
4. **正文分页**：`nextContentUrl` 仅用于**同一章内的下一页**（如 `text.下一页@href`）。下一章节由阅读底层根据目录自动衔接，严禁填写“下一章”链接。
5. **目录纯净**：目录只包含小说或漫画真实的话次列表，严禁在目录末尾拼接评论、打赏、推荐等非正文伪章节。
6. **选择器严谨**：优先使用 `text.文本`、`class.类名`、数字索引 `.0` / `.-1`；避免使用脆弱的 `:contains()`。
7. **Rhino 兼容**：阅读内置 Rhino 引擎。`java.ajax()` 返回结果为字符串，若需二次处理先用 `String(...)` 包裹；未暴露的 Java 类库严禁臆测调用。
8. **发现页排版**：标题独占整行且不留 `url`；移动端分类按钮一行排 2 个（`layout_flexBasisPercent: 0.46`），禁止排 4 列导致文字截断。

---

## 五、项目仓库目录结构

```text
AiWritingLegado/
├── README.md                                # 项目主入口（总览、避坑速查、体系导航）
├── skill/
│   ├── SKILL.md                             # AI 工作手册（核心工作流程与标准规则）
│   ├── examples/                            # 4 类典型书源示例（HTML/API/动态API/WAF）
│   └── skill-creator/                       # 技能迭代与评测工具
├── knowledge/
│   ├── README.md                            # 知识库主导航
│   ├── 书源规则教程.md                       # 规则教程与语法详解
│   ├── legado_knowledge_base.md             # 数据结构与全语法速查
│   ├── 书源输出模板_严格模式.md               # 标准 JSON 模板与字段清单
│   ├── 真实书源高级功能分析.md                # jsLib / loginUi / 解密实操
│   ├── 方法-JS扩展类.md                      # java.* 扩展函数说明
│   ├── 方法-加密解密.md                      # MD5 / AES / DES / RSA 加解密实战
│   └── reference/                           # 参考书源、官方样例与规范
├── docs/                                    # 排错、机制解析与实战案例库
│   ├── BUG_FIXES.md                         # 踩坑修复日志索引（开工先扫）
│   ├── FINAL_CHECKLIST.md                   # 书源交付前强制检查清单
│   ├── 禁漫天堂与高防漫画站书源实战避坑指南.md  # 漫画高防站实战指南（切片/WAF/目录纯净/AJAX评论）
│   ├── 移动端API与加密书源避坑指南.md         # 移动端 API / 签名 / 动态 Header 避坑指南
│   ├── WAF拦截与弹窗死循环分析及规避指南.md    # Cloudflare 与人机验证避坑指南
│   ├── TOC_PAGINATION_RULES.md              # 目录与正文分页深潜指南
│   └── 实战案例集-歌书网_起点图网_绅士漫画.md   # 单站综合实战修复深度复盘
├── book_sources/                            # 产出与维护的书源 JSON 文件
└── debugger/                                # Python 仿真实战调试器
```

---

## 六、维护与扩展准则

1. **入口统一**：项目主总览为根目录 `README.md`，AI 执行手册为 `skill/SKILL.md`，两份文件职责明确，避免重复冗余。
2. **案例合并**：同类单站案例优先归纳进专题指南或合并入 [`docs/实战案例集-歌书网_起点图网_绅士漫画.md`](docs/实战案例集-歌书网_起点图网_绅士漫画.md)，避免分散为大量零碎碎片文档。
3. **日志必记**：每解决一个新坑点，在 [`docs/BUG_FIXES.md`](docs/BUG_FIXES.md) 补充摘要索引，并在根目录 `README.md` 的避坑速查表中保持映射。

---

*文档整理更新：2026-10-22。主要入口：[`skill/SKILL.md`](skill/SKILL.md)*
