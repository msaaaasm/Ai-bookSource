# 知识库导航（knowledge）

> 先读 [`../skill/SKILL.md`](../skill/SKILL.md)，它是工作流程和硬性规范；这里放技术细节和真实案例。
> 文档之间如果有冲突，优先级为：**Legado 官方源码 / 真机行为 > `SKILL.md` > 本目录 > `reference/` 与历史资料**。

---

## 一、按任务查

| 你要做什么 | 先读 | 再查 |
|---|---|---|
| 第一次写书源，不懂规则语法 | [`书源规则教程.md`](书源规则教程.md) | [`legado_knowledge_base.md`](legado_knowledge_base.md) |
| 查 CSS / Default / XPath / JSONPath / 正则写法 | [`legado_knowledge_base.md`](legado_knowledge_base.md) | [`css选择器规则.txt`](css选择器规则.txt) |
| 输出完整书源 JSON | [`书源输出模板_严格模式.md`](书源输出模板_严格模式.md) | [`真实书源模板库.txt`](真实书源模板库.txt) |
| 用 JS 处理请求、加密、Cookie | [`方法-JS扩展类.md`](方法-JS扩展类.md) | [`方法-加密解密.md`](方法-加密解密.md) |
| 处理登录、Cloudflare、WAF | [`方法-登录检查JS.md`](方法-登录检查JS.md) | [`../docs/WAF拦截与弹窗死循环分析及规避指南.md`](../docs/WAF拦截与弹窗死循环分析及规避指南.md) |
| 做漫画 / 高防站 / WebView | [`../docs/禁漫天堂与高防漫画站书源实战避坑指南.md`](../docs/禁漫天堂与高防漫画站书源实战避坑指南.md) | [`../docs/移动端API与加密书源避坑指南.md`](../docs/移动端API与加密书源避坑指南.md) |
| 看真实站点怎么踩坑、怎么修 | [`书源实战日记.md`](书源实战日记.md) | [`../docs/BUG_FIXES.md`](../docs/BUG_FIXES.md) |
| 做订阅源（RSS/网页/视频） | [`订阅源规则帮助.txt`](订阅源规则帮助.txt) | [`reference/订阅源规则进阶.md`](reference/订阅源规则进阶.md) |
| 想快速查一条语法 | [`Legado知识库.txt`](Legado知识库.txt) | — |

---

## 二、核心文件说明

### 规则与语法

- **[`书源规则教程.md`](书源规则教程.md)** — 从入门到完整的规则教程，覆盖搜索、发现、详情、目录、正文、分页。**新任务优先读这一份。**
- **[`legado_knowledge_base.md`](legado_knowledge_base.md)** — 基于官方源码整理的数据结构 + CSS/Default/XPath/JSONPath/正则/JS 全量速查，适合当字典。
- **[`css选择器规则.txt`](css选择器规则.txt)** — 选择器问答式笔记，内容较杂，作为补充，不建议当唯一依据。
- **[`Legado知识库.txt`](Legado知识库.txt)** — 一页纸速查，适合快速回忆。

### 输出模板

- **[`书源输出模板_严格模式.md`](书源输出模板_严格模式.md)** — 必填字段、完整 JSON 模板、字段验证清单、常见错误。
- **[`真实书源模板库.txt`](真实书源模板库.txt)** — 可直接改写的小说站 / 笔趣阁类 / 聚合源模板。

### JS 能力

- **[`方法-JS扩展类.md`](方法-JS扩展类.md)** — `java.ajax`、`java.getString`、`java.webView`、Cookie、编码、缓存等内置方法。
- **[`方法-加密解密.md`](方法-加密解密.md)** — MD5、Base64、AES、DES、RSA、签名等。
- **[`方法-登录检查JS.md`](方法-登录检查JS.md)** — `AnalyzeUrl`、`loginUrl`、`loginCheckJs`、`loginUi` 的行为和示例。

### 进阶与实战

- **[`真实书源高级功能分析.md`](真实书源高级功能分析.md)** — `jsLib`、`loginCheckJs`、`loginUi`、多接口切换、图片解密、源变量等真实用法。
- **[`书源实战日记.md`](书源实战日记.md)** — 真实开发笔记：目录乱序、图片下一页、高防漫画站等。
- **[`订阅源规则帮助.txt`](订阅源规则帮助.txt)** — 订阅源（非书源）的规则说明。

---

## 三、`reference/` 参考区

`reference/` 不是主教程，按需查阅：

| 文件 | 用途 |
|---|---|
| [`真实书源知识库.md`](reference/真实书源知识库.md) | 134 个真实书源的统计结论（高频选择器、提取类型、常见模式） |
| [`书源精华速记.md`](reference/书源精华速记.md) | 精选实战技巧：选择器简写、超时、防盗链、UA、口诀 |
| [`HTML真实性检查清单.md`](reference/HTML真实性检查清单.md) | 如何确认拿到的是真实 HTML，而不是浏览器渲染后的 DOM |
| [`编码处理指南.md`](reference/编码处理指南.md) | 编码判断、GBK 配置、乱码排查 |
| [`阅读教程精华.txt`](reference/阅读教程精华.txt) | 阅读教程的精简版 |
| [`写源辅助AI提示词.txt`](reference/写源辅助AI提示词.txt) | 给其他 AI 的写源提示词 |
| [`ai提示词文档.txt`](reference/ai提示词文档.txt) | 另一份写源提示词参考 |
| [`书源日记231224.txt`](reference/书源日记231224.txt) | 早期经验日记 |
| [`订阅源规则进阶.md`](reference/订阅源规则进阶.md) | 订阅源进阶语法 |
| [`3a.json参考.txt`](reference/3a.json参考.txt)、[`TapManga.json参考.txt`](reference/TapManga.json参考.txt)、[`喜漫漫画.json参考.txt`](reference/喜漫漫画.json参考.txt)、[`霹雳书屋.json参考.txt`](reference/霹雳书屋.json参考.txt)、[`bqgui小说网参考.txt`](reference/bqgui小说网参考.txt) | 真实书源 JSON 参考 |
| [`cf登录检测.js参考.txt`](reference/cf登录检测.js参考.txt) | Cloudflare 检测的历史写法（**先看 WAF 指南，不要直接照搬**） |
| [`歌书网_书源_原始错误版.json`](reference/歌书网_书源_原始错误版.json)、[`歌书网_书源_修复版.json`](reference/歌书网_书源_修复版.json) | 修复前后对照案例（错误版含 `prevContentUrl` 等不存在的写法，**不要照抄**） |
| [`书源变体/`](reference/书源变体/) | 禁漫天堂的参考稿和 API 版，未按最终命名规范整理，**不要直接当成品发布** |

---

## 四、真实书源数据库

- [`../assets/knowledge_base/book_sources/`](../assets/knowledge_base/book_sources/) — 134 份真实书源分析（Markdown，命名形如 `序号_名称_书源_时间戳.md`），适合按网站类型找相似结构。
- [`../assets/book_source_database/book_sources/`](../assets/book_source_database/book_sources/) — 5 份原始书源 JSON，适合直接看结构。
- [`../assets/真实书源分析结果.json`](../assets/真实书源分析结果.json) — 统计结果。
- [`../assets/阅读源码.txt`](../assets/阅读源码.txt) — Legado 源码文档（约 14 MB），规则有疑问时的最终依据。

---

## 五、维护约定

1. **新知识优先补充到现有文件**，不要为每个小问题新建一篇文档。
2. 只有“可复用的完整案例/排错过程”才放进 `docs/`，命名用 `站点_问题_修复.md`。
3. 修复了一个真实书源的问题后，在 [`../docs/BUG_FIXES.md`](../docs/BUG_FIXES.md) 里加一条：现象 → 根因 → 修法 → 可推广的经验。
4. 不要往 `knowledge/` 放旧智能体的系统提示词、话术库、工具说明；这些属于 `archive/`。
