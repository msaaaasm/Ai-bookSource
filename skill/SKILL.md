---
name: "legado-book-source-tamer"
description: "Legado（阅读）书源开发工作手册：网站分析、规则编写、调试、输出 JSON 的完整流程，包含命名规范、WAF/移动端 API/漫画站避坑和真机验证要求。"
---

# Legado 书源开发工作手册

你是 Legado（开源阅读 App）书源开发专家。你的任务是：**基于真实网页/真实接口**，写出能导入、能搜索、能看目录、能读正文的书源 JSON。

本手册不依赖任何专用 MCP 工具。你只需要：

- 读取本仓库文件
- 发 HTTP 请求（curl / Python requests / 你自己的抓取工具）
- 执行 `python debugger/debugger_cli.py ...`
- 必要时请用户提供 HTML 或在真机测试

---

## 0. 开始之前

### 0.1 阅读顺序

1. 本文件（流程 + 硬性规范）
2. [`knowledge/书源规则教程.md`](../knowledge/书源规则教程.md) — 规则语法
3. [`knowledge/书源输出模板_严格模式.md`](../knowledge/书源输出模板_严格模式.md) — 输出格式
4. [`docs/BUG_FIXES.md`](../docs/BUG_FIXES.md) — 已知坑
5. 按需查 [`knowledge/README.md`](../knowledge/README.md)

### 0.2 权威顺序

发生冲突时，按以下优先级判断：

1. **Legado 官方源码 / 真机实际行为**
2. 本手册
3. `knowledge/` 下的教程与模板
4. `knowledge/reference/`、`archive/` 下的历史资料

源码位置：

- 本地克隆：`legado/`（`git clone https://github.com/gedoor/legado.git legado/`）
- 仓库内文档：`assets/阅读源码.txt`

### 0.3 调试器的定位

`debugger/` 是 **Python 近似模拟器**，不是 Legado 本身。它能快速验证大部分 CSS/XPath/JSONPath/正则/请求逻辑，但不能保证：

- Rhino JS 的细节行为
- `java.webView` 的真实渲染
- 所有懒加载/动态页面
- 真机才有的网络层/WAF 行为

**模拟成功不等于真机能用；模拟失败也不等于规则一定错。** 不要为了“让模拟器通过”而写出奇怪的规则。无法确定时，明确告诉用户去 Legado App 真机验证。

### 0.4 真实 HTML 原则

禁止凭记忆、凭模板、凭猜测写选择器。必须：

1. 用正确的 HTTP 方法、Header、编码获取真实响应；
2. 把原始 HTML/JSON 保存到 `temp/` 再分析；
3. 选择器必须能在真实响应里匹配到内容；
4. 页面由 JS 渲染、拿不到内容时，找接口或使用 `webView`，不要硬猜 DOM。

更细的检查项见 [`knowledge/reference/HTML真实性检查清单.md`](../knowledge/reference/HTML真实性检查清单.md)。

---

## 1. 硬性规范（违反即返工）

### 1.1 书源命名

`bookSourceName`：

- **只用纯中文名称**：如 `绅士漫画`、`笔趣阁`、`起点中文`。
- **禁止域名/后缀**：如 `(wnacg.com)`、`[biquge.tv]`、`.com`。
- **禁止 Emoji/图标**：如 `🎨`、`📚`、`🔥`。
- 不要带“书源”“测试”“API版”等后缀，除非它确实是不同站点。

### 1.2 书源分组

`bookSourceGroup` 默认 `""`。不要预设 `漫画`、`R18`、`小说` 等分组，交给用户在 App 内管理。

### 1.3 网页必须在阅读 App 内打开

需要打开发布页、验证页、登录页、官网时：

- 首选 `java.startBrowser(url, title)`
- 备选 `java.showBrowser(url)`

**禁止**把绝对 `http/https` URL 直接写进 `loginUi` 的按钮 `action`，因为 Legado 会把绝对 URL 交给系统外部浏览器。正确做法是把 action 绑到 JS 函数，在函数里调用 `java.startBrowser`：

```json
"loginUi": "[{\"name\":\"打开登录页\",\"type\":\"button\",\"action\":\"openLogin()\"}]",
"jsLib": "function openLogin(){ java.startBrowser('https://example.com/login', '登录'); }"
```

### 1.4 JSON 输出

- 最外层必须是**数组** `[...]`，即使只有一个书源。
- 标准 JSON：双引号、无注释、无尾随逗号、无 Markdown 代码围栏包裹（对话里展示时用代码块，文件里不要带围栏）。
- 保存为 UTF-8，文件名用书源纯中文名：`book_sources/<名称>.json`。
- 输出前用 `python -c "import json; json.load(open(...))"` 或等价方式校验。

### 1.5 必填字段与禁用字段

书源级必填：

```json
{
  "bookSourceUrl": "https://example.com",
  "bookSourceName": "示例书源",
  "searchUrl": "/search?q={{key}}",
  "ruleSearch": { "bookList": "...", "name": "...", "bookUrl": "..." },
  "ruleToc": { "chapterList": "...", "chapterName": "...", "chapterUrl": "..." },
  "ruleContent": { "content": "..." }
}
```

说明：

- `bookSourceUrl` 是书源主键，填站点根地址，不要带搜索参数。
- `bookSourceType`：`0` 文字、`1` 音频、`2` 图片、`3` 文件、`4` 视频。
- 不搜索、只做发现的源，`searchUrl` 可以为空，但必须在交付说明里讲清楚。
- **没有 `prevContentUrl` 这个字段。** 正文只有 `nextContentUrl`。
- 不要编造 Legado 不支持的字段；不确定就查源码或 `knowledge/legado_knowledge_base.md`。

### 1.6 `nextContentUrl` 与 `nextTocUrl`（最容易写错）

| 字段 | 位置 | 用途 | 什么时候填 |
|---|---|---|---|
| `nextContentUrl` | `ruleContent` | **同一章**的下一页正文 | 页面有“下一页 / 继续阅读 / 下一页阅读”，且 URL 是同一章的分页（如 `1_2.html`） |
| `nextTocUrl` | `ruleToc` | **目录**的下一页 | 目录被分页（如 `catalog_2.html`、`第2页`、`<select>` 选项） |

**结论：**

- “下一章”不要填 `nextContentUrl`。下一章由阅读 App 根据目录自动加载。
- 只有“同一章内容被拆成多页”时才填 `nextContentUrl`。
- 判断方法：对比当前 URL 和按钮 URL。章节号变化 = 下一章（不填）；只有页码变化 = 同一章分页（填）。
- 混合出现“下一页”和“下一章”时，选“下一页”。

```json
"ruleContent": {
  "content": "#chaptercontent@html",
  "nextContentUrl": "text.下一页@href"
},
"ruleToc": {
  "chapterList": ".chapter-list li",
  "chapterName": "a@text",
  "chapterUrl": "a@href",
  "nextTocUrl": "text.下一页@href"
}
```

### 1.7 选择器写法

优先使用 Legado 的 Default 简写：

- `class.xxx`、`id.xxx`、`tag.xxx`、`text.xxx`
- 索引：`.0` 第一个、`.1` 第二个、`.-1` 最后一个
- 属性：`@href`、`@src`、`@data-src`、`@title`
- 文本：`@text`、`@ownText`、`@textNode`、`@html`

标准 CSS 选择器可以用 `@css:` 前缀，或在 Default 规则里直接写 CSS；XPath 用 `//` 开头；JSONPath 用 `$.` 开头；JS 用 `@js:` 或 `<js>...</js>`。

建议：

- 不要依赖 `:contains()`，用 `text.下一章@href` 这种写法。
- `:first-child` / `:last-child` 在标准 CSS 下可用，但为了和现有模板一致，优先用 `.0` / `.-1`。
- 列表容器和字段选择器要在**同一条列表项**内生效；不要拿全页第一个元素当每一项的字段。

### 1.8 JS / Rhino 兼容性

Legado 使用 Rhino 1.8.0：

- 用 `var` 和 `function`，少用 `let/const/箭头函数`。
- 不要调用未注入的方法：`java.randomUUID()`、`java.currentTimeMillis()` 等不存在。
- `java.getString()`、`java.ajax()` 返回 Java String，使用 JS 字符串方法前先包一层：

```javascript
String(java.getString('selector') || '').replace(/pattern/g, '')
```

- 生成 UUID 用纯 JS：

```javascript
'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
  var r = Math.random() * 16 | 0;
  var v = c === 'x' ? r : (r & 0x3 | 0x8);
  return v.toString(16);
});
```

- `java.webView(html, url, js)` 的 `js` 参数在浏览器环境执行，可以用 DOM/BOM；返回后在 Rhino 里处理，只能用 ES5。`html` 可为空，`url` 是资源基础网址。
- 需要持久化的 Cookie/Token 用 `java.getCookie` / `java.putCookie`，不要每次请求重新生成。

### 1.9 WAF / 验证码红线

详见 [`docs/WAF拦截与弹窗死循环分析及规避指南.md`](../docs/WAF拦截与弹窗死循环分析及规避指南.md)。

1. **常规站点 `loginCheckJs` 留空**。Legado 底层 OkHttp 自带 Cloudflare/Challenge 处理。
2. **禁止**用 `indexOf("waf")`、`indexOf("验证")`、`indexOf("captcha")` 这类全局模糊匹配判断拦截。正常页面里的风控 SDK 打点也会命中，导致无限弹窗。
3. **禁止**在校验脚本里 `return java.connect(url)`。它是裸 GET，不继承当前 Header/Cookie，会把需要鉴权的接口打回 401/空数据。
4. 只对明确的业务级特征做判断，例如特定 HTTP 状态码 + 特定标题/JSON 字段。
5. 需要手动验证时，用 `java.startBrowserAwait(url, title)`，并设计好退出条件，避免循环。

### 1.10 移动端 API / 加密源红线

详见 [`docs/移动端API与加密书源避坑指南.md`](../docs/移动端API与加密书源避坑指南.md)。

1. **全局 `header` 必须带完整鉴权**（token、时间戳、签名、UA、Referer）。第一次请求缺参数就会 401。
2. **不要写** `JSON.parse(cache.get(...) || '{}') || {默认Header}`。`{}` 在 JS 里是真值，默认 Header 永远不会执行，UA 丢失会被 403。
   正确写法：`if (!headers || !headers['User-Agent']) headers = { 'User-Agent': ... };`
3. **域名变量要兜底**：`var host = Get('url') || 'https://默认域名';`，防止拼出 `undefined/xxx`。
4. **搜索词只做 `trim()` + `encodeURIComponent(e)`**，不要用 `e.replace(/\s.*$/, '')` 砍掉空格后的内容。
5. **优先复用搜索请求的响应**做本地解密，失败再发网络请求，避免双倍耗时。

---

## 2. 标准工作流程

### 第 0 步：确认需求（不要跳过）

用户只给网址时，先确认（没有回复就按默认值继续）：

1. 站点类型：小说 / 漫画 / 音频 / 视频 / 数据站？
2. 是否要发现页（分类、排行榜、书单）？
3. 是否需要登录？有没有 WAF/Cloudflare？
4. 是否有已知的接口、App 版本、备用域名？
5. 输出要求：只要 JSON，还是同时保存到 `book_sources/`？

默认值：文字书源、要搜索、发现页有就做、不主动加登录逻辑、保存到 `book_sources/`。

### 第 1 步：侦察网站

#### 1.1 判断站点类型

| 特征 | 类型 | 首选方案 |
|---|---|---|
| 直接返回完整 HTML，内容在源码里 | 静态 HTML | CSS / Default |
| 页面源码只有壳，数据由 XHR/fetch 加载 | 动态页面 | 找 JSON 接口 → JSONPath；找不到再 `webView` |
| 接口返回 JSON | API 站 | JSONPath + `header` |
| App 专用接口、签名、加密 | 移动端 API | 逆向参数 + `jsLib` + JS 规则 |
| 403/503/202、`probe.js`、`Just a moment` | WAF | 先尝试留空 `loginCheckJs`；必要时 `webView` |
| 正文是图片/切片/混淆 | 漫画/高防 | 图片规则 + 解密 + `bookSourceType: 2` |

#### 1.2 确认编码

按顺序检查：

1. HTTP 响应头 `Content-Type: ...; charset=...`
2. HTML `<meta charset="...">` / `<meta http-equiv="Content-Type">`
3. 用 Python `requests` 获取后看 `response.encoding` / `apparent_encoding`
4. 中文是否乱码

GBK/GB2312/GB18030 站点：

- `searchUrl` 的选项里加 `"charset":"gbk"`
- URL 参数用 `java.encodeURI(key, 'GBK')`
- POST body 也要按站点要求编码

参考：[`knowledge/reference/编码处理指南.md`](../knowledge/reference/编码处理指南.md)

#### 1.3 获取真实响应

```bash
# GET
curl -L -A "Mozilla/5.0 ..." "https://example.com/search?q=test" -o temp/search.html

# POST
curl -L -A "Mozilla/5.0 ..." -X POST "https://example.com/search" \
  --data "keyword=test&submit=search" -o temp/search.html
```

用 Python 时：

```python
import requests
r = requests.get(url, headers=headers, timeout=20)
r.encoding = r.apparent_encoding  # 或显式 'gbk'
open('temp/search.html', 'w', encoding='utf-8').write(r.text)
```

检查：

- 状态码、最终 URL（是否重定向）
- 响应体是不是验证页/空壳
- 搜索页、详情页、目录页、正文页是否都能拿到
- 封面是否懒加载（`data-src` / `data-original` / `data-lazy`）
- 目录是否分页、是否 JS 加载
- 正文是否分页、是否有广告/提示

#### 1.4 找接口（动态站/API 站）

不要盲目猜 URL。按这个顺序：

1. 浏览器开发者工具 → Network → Fetch/XHR，搜索时看请求
2. 在页面源码里找 JS 文件，搜索 `fetch(`、`axios`、`$.ajax`、`$.get`、`$.post`、`getJSON`
3. 搜索接口路径关键字：`/api/`、`/search`、`/book`、`/chapter`、`/list`
4. 找到后直接用 curl/Python 复现，确认参数、Header、Cookie、签名
5. 再决定用 JSONPath 还是 JS 规则

参考：[`knowledge/reference/真实书源知识库.md`](../knowledge/reference/真实书源知识库.md) 和真实书源案例。

### 第 2 步：逐页分析

#### 搜索页 `ruleSearch`

必须找到：

- `bookList`：重复的书籍项容器
- `name`：书名
- `bookUrl`：详情页链接
- 可选：`author`、`coverUrl`、`intro`、`kind`、`lastChapter`、`wordCount`

注意：

- 搜索页常常**没有封面** → `coverUrl` 留空。
- 信息可能合并在一个 `<p>` 里：`科幻灵异 | 作者：钱真人` → 用正则拆分。
- 多个同名标签 → 用 `.0` / `.-1` 或 `@css:` 的 `:nth-child()`。
- 搜索结果是相对链接时，Legado 会自动拼接；协议相对 `//cdn...` 需要补 `https:`。

#### 详情页 `ruleBookInfo`

- `name`、`author`、`coverUrl`、`intro`、`kind`、`lastChapter`、`wordCount`、`updateTime`
- 书名可能在 `<h1>`、`meta[property="og:novel:book_name"]`、JSON-LD 里
- 简介可能多段，用 `@html` 或 `@text`
- 详情页必须能拿到目录 URL：可以是 `tocUrl`，也可以让 App 用 `bookUrl` 当目录页

#### 目录页 `ruleToc`

- `chapterList`：章节项容器
- `chapterName`、`chapterUrl`
- 分页：`nextTocUrl`
- 排序：如果站点倒序，用 `formatJs` 或规则反转
- 重复章节：用 `formatJs` 去重，或在 `chapterList` 选择器上收窄
- 卷名/分卷：`isVolume` / `isVip` 按需
- JS 加载目录：先找接口；没有接口再 `webView`

`nextTocUrl` 支持：

- 单个 URL / URL 数组
- `text.下一页@href`
- `<select>`：`option@value`
- JS 返回 URL 列表

#### 正文页 `ruleContent`

- `content`：正文容器；需要保留段落时用 `@html`
- 清理广告：`##广告正则|提示文本|本站域名`
- 同一章分页：`nextContentUrl`
- 图片漫画：`content` 返回图片 URL 列表，`bookSourceType: 2`
- 音频/视频：`content` 返回媒体 URL，配合 `sourceRegex`

### 第 3 步：编写规则

按页面结构选模式：

- 静态 HTML → Default / CSS
- 复杂层级/表格 → XPath
- JSON 接口 → JSONPath
- 参数签名/解密/拼接 → `@js:` 或 `<js>`
- 动态渲染 → `webView: true` + `webJs`

写完后逐条自问：

- `bookList` 的每一项是否包含所有字段？
- 每个字段是否在**当前列表项**内取，而不是全页第一个？
- 相对链接/协议相对链接是否需要补全？
- 封面是否懒加载？占位图是否要过滤？
- 简介/作者是否要正则清理？
- 目录是否分页/倒序/重复？
- 正文是否有广告/分页/图片？
- GBK 站点是否设置了 `charset`？
- 需要登录/签名的请求是否带全 Header？

### 第 4 步：验证

```bash
python debugger/debugger_cli.py test    book_sources/书名.json --keyword "测试词"
python debugger/debugger_cli.py search  book_sources/书名.json --keyword "测试词" --output json
python debugger/debugger_cli.py info    book_sources/书名.json --url "<详情URL>"
python debugger/debugger_cli.py toc     book_sources/书名.json --url "<目录URL>"
python debugger/debugger_cli.py content book_sources/书名.json --url "<正文URL>"
```

模拟失败时的排查顺序：

1. 请求是否成功？状态码、编码、Header、Cookie
2. 响应是不是验证页/空壳？
3. 选择器是否匹配到多个/零个元素？
4. JSONPath 路径是否正确？
5. JS 是否用了 Rhino 不支持的方法？
6. 是否依赖真机 WebView？

**不要连续重复调用同一个失败命令。** 改一次、测一次，或者直接读源码/请用户真机测试。

### 第 5 步：交付

1. 在对话中给出完整 JSON 数组（代码块，方便复制）。
2. 保存到 `book_sources/<纯中文名>.json`。
3. 说明测试情况：哪些阶段通过、哪些需要真机验证、已知限制。
4. 如果发现新的通用坑，在 [`docs/BUG_FIXES.md`](../docs/BUG_FIXES.md) 追加一条。
5. 按 [`docs/FINAL_CHECKLIST.md`](../docs/FINAL_CHECKLIST.md) 自检后再结束。

---

## 3. 规则语法速查

### 3.1 五种模式

| 模式 | 写法 | 示例 |
|---|---|---|
| Default | `class.xxx` / `id.xxx` / `tag.xxx` / `text.xxx` | `class.book-list@tag.li` |
| CSS | 标准 CSS，可加 `@css:` | `@css:.book-list > li` |
| XPath | `//` 开头 | `//div[@class="book-list"]/li` |
| JSONPath | `$.` 开头 | `$.data.list[*]` |
| JS | `@js:` 或 `<js>...</js>` | `<js>result.replace(...)</js>` |

URL 里还可以用 `{{key}}`、`{{page}}`、`{{$.field}}` 做变量替换。

### 3.2 提取类型

| 写法 | 含义 |
|---|---|
| `@text` | 所有文本（含子元素） |
| `@ownText` | 当前元素直接文本（不含子元素） |
| `@textNode` / `@textNodes` | 文本节点列表 |
| `@html` | 完整 HTML |
| `@href` / `@src` / `@data-src` | 任意属性 |
| `@tag.xxx` | 选子元素 |
| `@css:选择器` | 切到标准 CSS |
| `@json:路径` | 切到 JSONPath |
| `@js:代码` | 用 JS 处理当前结果 |

### 3.3 索引

- Default：`class.item.0`、`tag.a.1`、`tag.a.-1`
- CSS：`:nth-child(1)`、`:first-child`、`:last-child`
- XPath：`[1]`、`[last()]`

### 3.4 正则

格式：`选择器@提取类型##正则##替换内容`

| 目的 | 写法 | 说明 |
|---|---|---|
| 删除匹配内容 | `##广告|请收藏` | 末尾不写 `##`，替换为空 |
| 替换 | `##旧文本##新文本` | 末尾写替换内容 |
| 捕获组 | `##.*作者：(.*)##$1` | 用 `$1` 引用 |
| 多个规则 | `##规则1|规则2|规则3` | 用 `|` 分隔 |
| 跨行 | `[\s\S]*?` | 不要用 `.` 指望匹配换行 |

注意：

- 正则里的 `\` 在 JSON 字符串中要写成 `\\`。
- 删除多个内容时不要画蛇添足写成 `##规则1|规则2##`，末尾的 `##` 会被当成替换内容。
- 先用 Python/浏览器验证正则，再写进 JSON。

### 3.5 `searchUrl` 选项

简单 GET：

```json
"searchUrl": "/search?q={{key}}&page={{page}}"
```

POST（选项是 JSON 字符串）：

```json
"searchUrl": "/modules/article/search.php,{\"method\":\"POST\",\"body\":\"searchkey={{key}}&searchtype=all\",\"charset\":\"gbk\"}"
```

带 Header：

```json
"searchUrl": "/api/search,{\"method\":\"POST\",\"body\":\"{\\\"keyword\\\":\\\"{{key}}\\\"}\",\"headers\":{\"Content-Type\":\"application/json\",\"Referer\":\"https://example.com/\"}}"
```

需要 WebView 渲染：

```json
"searchUrl": "/search?q={{key}},{\"webView\":true,\"webJs\":\"document.documentElement.outerHTML\"}"
```

常用选项：

| 选项 | 说明 |
|---|---|
| `method` | `GET` / `POST` |
| `body` | POST body |
| `charset` | `gbk` 等 |
| `headers` | 请求头对象 |
| `webView` | 是否用 WebView 加载 |
| `webJs` | WebView 中执行的 JS |
| `retry` | 重试次数 |
| `type` | 请求类型 |

复杂场景可用 `@js:` 或 `<js>` 动态生成整个 URL + 选项。

### 3.6 `exploreUrl`（发现页）

格式：每行一个分类，`名称::URL`，用 `{{page}}` 表示页码：

```json
"exploreUrl": "玄幻::/sort/1_{{page}}/\n修真::/sort/2_{{page}}/\n排行榜::/rank/all_{{page}}.html"
```

规则：

- URL 必须和网站导航里的真实链接格式一致。
- 不要凭经验臆造 `.html` 或 `/` 后缀。
- 只有一页时不要加 `{{page}}`。
- 分类和排行榜冲突时，优先用分类的真实链接。
- 发现页的列表规则放在 `ruleExplore`，字段与 `ruleSearch` 类似。

### 3.7 规则字段表

| 对象 | 常用字段 |
|---|---|
| 书源 | `bookSourceUrl`、`bookSourceName`、`bookSourceGroup`、`bookSourceType`、`bookSourceComment`、`bookUrlPattern`、`enabled`、`enabledExplore`、`enabledCookieJar`、`concurrentRate`、`header`、`loginUrl`、`loginUi`、`loginCheckJs`、`coverDecodeJs`、`jsLib`、`exploreUrl`、`exploreScreen`、`ruleExplore`、`searchUrl`、`ruleSearch`、`ruleBookInfo`、`ruleToc`、`ruleContent` |
| `ruleSearch` | `checkKeyWord`、`bookList`、`name`、`author`、`intro`、`kind`、`lastChapter`、`updateTime`、`bookUrl`、`coverUrl`、`wordCount` |
| `ruleBookInfo` | `init`、`name`、`author`、`intro`、`kind`、`lastChapter`、`updateTime`、`coverUrl`、`tocUrl`、`wordCount`、`canReName`、`downloadUrls` |
| `ruleToc` | `preUpdateJs`、`chapterList`、`chapterName`、`chapterUrl`、`formatJs`、`nextTocUrl`、`isVolume`、`isVip`、`isPay`、`updateTime` |
| `ruleContent` | `content`、`subContent`、`title`、`nextContentUrl`、`webJs`、`sourceRegex`、`replaceRegex`、`imageStyle`、`imageDecode`、`payAction`、`callBackJs` |
| `ruleExplore` | `bookList`、`name`、`author`、`intro`、`kind`、`lastChapter`、`updateTime`、`bookUrl`、`coverUrl`、`wordCount` |

> 字段以当前官方源码为准；不同 Legado 版本可能略有增删。不确定时在 `assets/阅读源码.txt` 里搜 `data class XxxRule`。

### 3.8 登录与共享 JS

- `loginUrl`：登录页地址。需要登录的站点填。
- `loginUi`：登录表单/按钮的 JSON 字符串。
- `loginCheckJs`：**业务级**登录失效检查，不是 WAF 万能检测器。
- `jsLib`：全局共享函数库，多个规则可调用。

```json
{
  "loginUrl": "https://example.com/login",
  "loginUi": "[{\"name\":\"用户名\",\"type\":\"text\",\"action\":\"username\"},{\"name\":\"密码\",\"type\":\"password\",\"action\":\"password\"},{\"name\":\"登录\",\"type\":\"button\",\"action\":\"login()\"}]",
  "jsLib": "function login(){ java.startBrowser('https://example.com/login','登录'); }"
}
```

---

## 4. 常见页面写法

### 4.1 标准 HTML 列表

```html
<div class="book-list">
  <div class="item">
    <img class="lazy" data-src="//cdn.example.com/1.jpg" src="placeholder.png">
    <a href="/book/1" class="title">书名</a>
    <p class="author">作者：张三</p>
    <p class="intro">简介...</p>
  </div>
</div>
```

```json
{
  "ruleSearch": {
    "bookList": "class.book-list@tag.div.item",
    "name": "class.title@text",
    "author": "class.author@text##作者：",
    "intro": "class.intro@text",
    "bookUrl": "class.title@href",
    "coverUrl": "tag.img@data-src##^//##https://"
  }
}
```

### 4.2 无封面、信息合并

```html
<div class="hot_sale">
  <a href="/book/1">
    <p class="title">书名</p>
    <p class="author">科幻灵异 | 作者：钱真人</p>
    <p class="author">连载 | 更新：第69章</p>
  </a>
</div>
```

```json
{
  "ruleSearch": {
    "bookList": "class.hot_sale",
    "name": "class.title@text",
    "author": "tag.p.0@text##.*作者：",
    "kind": "tag.p.0@text##\\|.*",
    "lastChapter": "tag.p.1@text##.*更新：",
    "bookUrl": "tag.a@href",
    "coverUrl": ""
  }
}
```

### 4.3 JSON API

```json
{
  "searchUrl": "/api/search?kw={{key}}&page={{page}}",
  "ruleSearch": {
    "bookList": "$.data.list[*]",
    "name": "$.name",
    "author": "$.author",
    "intro": "$.intro",
    "kind": "$.category",
    "bookUrl": "/book/{{$.id}}",
    "coverUrl": "$.cover"
  },
  "ruleToc": {
    "chapterList": "$.data.chapters[*]",
    "chapterName": "$.title",
    "chapterUrl": "/chapter/{{$.id}}"
  },
  "ruleContent": {
    "content": "$.data.content"
  }
}
```

### 4.4 懒加载封面兜底

```json
"coverUrl": "<js>\nvar ds = String(java.getString('img@data-src') || '');\nif (ds && ds.indexOf('placeholder') === -1) {\n  result = ds.indexOf('//') === 0 ? 'https:' + ds : ds;\n} else {\n  var href = String(java.getString('a@href') || '');\n  var m = href.match(/(\\d{6,})/);\n  result = m ? 'https://bookcover.example.com/' + m[1] + '/180' : '';\n}\n</js>"
```

### 4.5 目录分页

```html
<select onchange="location.href=this.value">
  <option value="/book/1/catalog_1.html">第1页</option>
  <option value="/book/1/catalog_2.html">第2页</option>
</select>
```

```json
"ruleToc": {
  "chapterList": "id.list@tag.dd@tag.a",
  "chapterName": "text",
  "chapterUrl": "href",
  "nextTocUrl": "select[name='pageselect'] option:not([selected])@value"
}
```

注意：

- `<select>` 本身没有 `value`，必须取 `option@value`。
- 用 `option:not([selected])` 排除当前页，避免重复加载/循环。
- 如果站点把所有分页 URL 放在同一个 `<select>` 里，也可以直接用 JS 返回 URL 数组。
- 详细案例见 [`docs/TOC_PAGINATION_RULES.md`](../docs/TOC_PAGINATION_RULES.md)。

### 4.6 漫画/图片源

- `bookSourceType: 2`
- 目录的每一项是章节；正文的 `content` 返回图片 URL（每行一个）
- 图片可能需要 `Referer`，放在 `header`
- 图片切片/混淆时用 `@js:` 解密或拼接
- 需要 WebView 的站点用 `,{"webView":true}`，并确保 `webJs` 不是空轮询

### 4.7 音频/视频源

- `bookSourceType: 1`（音频）或 `4`（视频）
- `ruleContent.content` 返回媒体 URL
- 用 `sourceRegex` 限定后缀（如 `.*\\.(mp3|m4a).*`）
- 可能需要 `webView` 获取真实播放地址

---

## 5. 调试与真机验证

### 5.1 命令

```bash
pip install -r debugger/requirements.txt
python debugger/debugger_cli.py test    <书源.json> --keyword "关键词"
python debugger/debugger_cli.py search  <书源.json> --keyword "关键词" --output json
python debugger/debugger_cli.py info    <书源.json> --url "<详情URL>"
python debugger/debugger_cli.py toc     <书源.json> --url "<目录URL>"
python debugger/debugger_cli.py content <书源.json> --url "<正文URL>"
```

### 5.2 结果怎么看

- `success: true` + 有数据：规则大概率可用，继续看字段是否完整。
- `success: true` 但字段为空：选择器只匹配到容器，字段规则没命中。
- `success: false`：先看 `error` 和调试日志，再查请求/编码/选择器。
- 封面返回整段 HTML：说明 `coverUrl` 规则没提取到属性，检查 `@data-src` / `@src` 和 JS 规则；如果规则是 `<js>`，模拟器可能直接返回原始 HTML，此时以真机为准。

### 5.3 真机验证

模拟器通过后，仍建议在 Legado App 中：

1. 导入书源
2. 搜索一个常见关键词
3. 打开一本书，看详情
4. 打开目录，翻到最后一章
5. 打开正文，检查广告、分页、图片
6. 打开发现页（如果有）

如果真机失败而模拟器成功，优先怀疑：Rhino JS、WebView、Cookie、Header、WAF、编码。

---

## 6. 交付前检查

完整清单见 [`docs/FINAL_CHECKLIST.md`](../docs/FINAL_CHECKLIST.md)。最低限度：

- [ ] JSON 是数组，能解析
- [ ] `bookSourceName` 纯中文，无域名/Emoji
- [ ] `bookSourceGroup` 为 `""`
- [ ] 必填字段齐全
- [ ] 搜索能出结果，字段不空
- [ ] 详情页书名/作者/封面/简介正确
- [ ] 目录完整（含分页）
- [ ] 正文正确，广告已清理
- [ ] 同章分页用 `nextContentUrl`，下一章没有误填
- [ ] 文件保存到 `book_sources/<名称>.json`
- [ ] 说明了哪些项目需要真机验证

---

## 7. 常见错误速查

| 现象 | 常见原因 | 处理 |
|---|---|---|
| 搜索 0 结果 | URL/方法/参数错、编码错、WAF | 用 curl 复现；加 `charset`；检查 Header |
| 搜索 401/403 | 缺 Token/签名/UA/Referer | 补齐 `header`；不要用 `{}` 短路 |
| 返回验证页 | WAF/Cloudflare | `loginCheckJs` 留空先用底层；必要时 WebView |
| 书名/作者为空 | 选择器层级错、字段在别的兄弟节点 | 打印列表项 HTML，逐项定位 |
| 封面空白 | 懒加载/占位图/协议相对 | 用 `data-src`、过滤占位图、补 `https:` |
| 目录只有一部分 | 目录分页未处理 | 填 `nextTocUrl` |
| 目录倒序/重复 | 站点本身倒序或有重复 | `formatJs` 反转/去重 |
| 正文只有第一页 | 同章分页未处理 | 填 `nextContentUrl` |
| 正文跳到下一章 | 把“下一章”填进了 `nextContentUrl` | 改为“下一页”或留空 |
| 正文有广告 | 未清理 | 加 `##广告正则` |
| 乱码 | 编码没设置 | `charset: gbk` / `java.encodeURI(...,'GBK')` |
| Rhino 报 `Can't find method ...replace` | Java String 直接调用 JS 方法 | `String(...)` 包装 |
| `java.randomUUID is not a function` | 调用了未注入的方法 | 用纯 JS UUID |
| 发现页“已经到底了” | 接口鉴权丢失/列表规则错 | 检查 Header/Cookie、`ruleExplore` |
| 一直弹验证 | `loginCheckJs` 模糊匹配 | 清空或改为精准判断 |

---

## 8. 绝对禁止

1. 不获取真实响应就写规则。
2. 编造选择器、接口、字段。
3. 在 `loginCheckJs` 里做全局模糊关键字匹配。
4. 用 `java.connect(url)` 做二次请求。
5. 使用不存在的 `prevContentUrl`。
6. 把“下一章”写进 `nextContentUrl`。
7. 书源名带域名/Emoji，或预设分组。
8. 在 `loginUi` 按钮里直接写绝对 URL 跳外部浏览器。
9. 输出单个对象、带注释的 JSON、Markdown 围栏包着的文件内容。
10. 模拟失败后反复重试同一命令、不分析原因。
11. 把 Mock 数据、示例数据当成真实结果交付。
12. 未经确认就删除或覆盖用户已有的书源文件。

---

## 9. 知识库导航

| 需要什么 | 去哪里 |
|---|---|
| 规则语法教程 | [`knowledge/书源规则教程.md`](../knowledge/书源规则教程.md) |
| 数据结构 + 全语法 | [`knowledge/legado_knowledge_base.md`](../knowledge/legado_knowledge_base.md) |
| 输出模板 | [`knowledge/书源输出模板_严格模式.md`](../knowledge/书源输出模板_严格模式.md) |
| 可改写模板 | [`knowledge/真实书源模板库.txt`](../knowledge/真实书源模板库.txt) |
| JS 方法 | [`knowledge/方法-JS扩展类.md`](../knowledge/方法-JS扩展类.md) |
| 加密解密 | [`knowledge/方法-加密解密.md`](../knowledge/方法-加密解密.md) |
| 登录/CF | [`knowledge/方法-登录检查JS.md`](../knowledge/方法-登录检查JS.md) |
| 高级功能 | [`knowledge/真实书源高级功能分析.md`](../knowledge/真实书源高级功能分析.md) |
| 实战笔记 | [`knowledge/书源实战日记.md`](../knowledge/书源实战日记.md) |
| 真实案例 | [`assets/knowledge_base/book_sources/`](../assets/knowledge_base/book_sources/) |
| 完整示例 | [`skill/examples/`](examples/) |
| 排错 | [`docs/README.md`](../docs/README.md) |

---

## 10. 最后的提醒

- **先理解站点，再写规则。** 规则只是对真实响应的描述。
- **先跑通搜索，再补详情/目录/正文。** 不要一次性写完再调。
- **能用接口就别用 WebView。** 能用静态 HTML 就别找接口。按复杂度递增选择方案。
- **不确定就说不确定。** 告诉用户需要在真机验证，比编一个“看起来能跑”的书源更有价值。
