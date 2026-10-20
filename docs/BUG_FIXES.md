# Bug 修复记录

记录各书源、工具的已知问题及修复方案，供后续 AI 或开发者参考，**避免重踩坑**。

---

## 起点中文 (qidian.com) — 搜索结果封面识别失败

**问题时间**：2026-10-20  
**文件**：`book_sources/起点中文.json` → `ruleSearch.coverUrl`  
**状态**：✅ 已修复

### 现象
搜索结果列表中，书籍封面图片无法显示（空白/统一占位图）。

### 根本原因
起点搜索页 (`m.qidian.com/so/`) 使用**懒加载**技术：

```html
<!-- 实际 HTML 结构 -->
<img src="https://imgservices-1252317822.image.myqcloud.com/coco/...占位图..."
     data-src="//bookcover.yuewen.com/qdbimg/349573/1036370336/180"
     class="_bookImg_e9qzy_15">
```

- `src` 属性 → 统一的**占位符**图片（`imgservices-*.myqcloud.com`），**不是**封面
- `data-src` 属性 → 真实封面 URL（`//bookcover.yuewen.com/qdbimg/...`），但以 `//` 开头（缺少协议头）

旧规则 `img@data-src@js:'https:' + result || img@src` 语法有歧义——`|| img@src` 在 Legado 规则语法中不是有效的回退写法，整条规则解析失败。

### 修复方案
改用 `<js>` 规则，明确处理懒加载：

```json
"coverUrl": "<js>\nvar ds = String(java.getString(\"img@data-src\") || \"\");\nif (ds && ds.trim() && ds.indexOf(\"imgservices\") === -1) {\n  result = ds.startsWith(\"//\") ? (\"https:\" + ds) : ds;\n} else {\n  var href = String(java.getString(\"a@href\") || \"\");\n  var m = href.match(/(\\d{8,})/);\n  result = m ? (\"https://bookcover.yuewen.com/qdbimg/349573/\" + m[1] + \"/180\") : \"\";\n}\n</js>"
```

**逻辑说明**：
1. 优先读取 `data-src`，过滤掉含 `imgservices` 的占位符图片
2. 若是 `//` 开头，补全为 `https://`
3. **兜底**：从书本链接 `href` 中用正则提取 bookId，直接构造标准封面 URL

> 注意：Python 模拟器对 `<js>` 形式的 `coverUrl` 支持有限，可能把整段列表项 HTML 当作结果返回；这不一定代表真机失败，最终以 Legado App 为准。

### 经验推广

> [!TIP]
> 遇到封面不显示时，先检查页面 HTML 的 `<img>` 标签是否使用了懒加载属性（`data-src`、`data-original`、`lazyload`、`data-lazy` 等），不要直接用 `img@src`。
>
> 兜底方案：从 `bookUrl` 中提取书源 ID，再拼接固定 CDN 格式构造封面 URL，完全绕开懒加载。

---

## 起点图趣/起点图网 (qidiantu.com) — 搜索接口 404 + 探索规则多处失效

**问题时间**：2026-02-18  
**文件**：`book_sources/起点图网.json`  
**状态**：✅ 已修复（详见 [`起点图网书源错误分析与修复指南.md`](起点图网书源错误分析与修复指南.md)）

### 现象摘要
1. 搜索无结果（接口返回 404）
2. 探索页封面全部缺失
3. 书名/作者出现乱码或多余字符（Rhino JS 引擎兼容问题）

### 关键原因
- `searchUrl` 用了已下线的旧接口 `/book/`，应改为 `/bookxyy/`
- `ruleExplore.coverUrl` 规则依赖 `td` 位置索引，页面改版后失效
- JS 规则中对 `java.getString()` 返回值直接调用 `.replace(/regex/g, '')` 触发 Rhino 引擎异常

---

## 通用：Rhino JS 引擎的 Java String 陷阱

**影响范围**：所有使用 `<js>` 规则的书源  
**状态**：✅ 有标准修复方案

### 问题描述
在 `<js>` 代码块中，`java.getString(...)` 返回的是 Java 原生的 `java.lang.String` 对象，**不是** JavaScript 的 `String` 原型实例。

在 Mozilla Rhino 引擎中，对 Java String 直接调用 JavaScript 的 `String.prototype.replace(RegExp, ...)` 时，Rhino 会尝试匹配 Java `java.lang.String.replace()` 的重载方法签名，导致：

```
EvaluatorException: Can't find method java.lang.String.replace(object,string)
```

### 修复方案

```javascript
// ❌ 危险写法 — 直接操作 Java String
java.getString('selector').replace(/pattern/g, '');

// ✅ 安全写法 — 先用 String() 转为 JS 原生字符串
String(java.getString('selector') || '').replace(/pattern/g, '');
```

**规则**：凡是从 `java.getString()`、`java.ajax()` 等 Java 接口拿到的字符串，在使用 JS 字符串方法前，**一律用 `String(... || '')` 包装**。

---

## 通用：懒加载图片封面识别

**影响范围**：使用懒加载的各类书源（如起点、晋江等）  
**状态**：✅ 有标准处理方案

### 常见懒加载属性

| 属性名 | 说明 |
|--------|------|
| `data-src` | 最常见，主流懒加载库 |
| `data-original` | jQuery Lazy Plugin |
| `data-lazy` | 部分框架 |
| `data-url` | 少数框架 |

### 通用识别规则（Legado 语法）

```
img@data-src||img@data-original||img@data-lazy||img@src
```

若值以 `//` 开头，需加协议头：

```json
"coverUrl": "img@data-src@js:result.startsWith('//') ? ('https:' + result) : result"
```

若需要过滤占位图，改用完整 `<js>` 规则（参见上方起点修复方案）。

---

## 绅士漫画 (wnacg.com) — 搜索只出 1 条 + 移动版布局与筛选

**问题时间**：2026-10-20  
**文件**：`book_sources/绅士漫画.json`  
**状态**：✅ 已修复

### 现象

1. 在阅读 App 里搜索只返回 1 条结果。
2. 网站搜索页（手机 Chrome）带“筛选”面板，但书源没有利用分类/标签/排序条件。
3. 合集（多话）在移动版布局下目录只识别出 1 章。

### 根因

- 站点按 UA 返回两套完全不同的 DOM：
  - **PC（桌面 UA）**：`ul.cc > li.gallary_item`、`.pic_box`、`.title`、`.info_col`
  - **移动（手机 UA）**：`ul#classify_container > li.cate-*`、`a.ImgA`、`a.txtA`、`span.info`
- 原规则只写了 PC 选择器；App/WebView 使用移动 UA 时匹配不到列表，只剩一个误匹配项。
- `bookUrlPattern` 只允许 `/photos/...`，而搜索结果实际是 `/photos-index-aid-...html`，详情页识别也会受影响。
- `ruleBookInfo.tocUrl` 写成了字符串 `baseUrl`，不是合法规则，真机会拼成 `https://站点/baseUrl`。
- 移动版合集章节在 `#dv-ch-list` 里，链接是 `photos-slide-aid-*`；原目录 JS 只认 PC 的 `a.tagshow`，因此只走单话兜底。

### 修复

1. `header` 改为手机 Chrome UA，和用户实际访问的移动版一致。
2. `ruleSearch` / `ruleExplore` 改为**双布局合并选择器**：
   - `bookList`: `ul#classify_container > li || ul.col_2 > li || div.itemBox || ul.cc > li.gallary_item`
   - `name`: `a.txtA@text || a.ImgA > span:not(.sr_tags)@text || .itemTxt a.title@text || .title a@text || ...`
   - `bookUrl`: `a.ImgA@href || .itemImg a@href || .pic_box a@href || .title a@href`
   - `kind`: 从 `cate-N` 映射为中文分类（同人誌·漢化、單行本·漢化、AI圖集等）。
   - `lastChapter` / `wordCount`: 用 JS 同时解析 `.info`、`.info_col`、`.itemTxt`。
3. `bookUrlPattern` 的路径段分隔符从 `[/?]` 改为 `[-/?]`，覆盖 `photos-index-*`。
4. `tocUrl` 改为 `""`，让 App 直接用详情页当目录页。
5. 目录 JS 同时支持：
   - 移动版 `#dv-ch-list li a`（章节名取 `<span>` 文本）
   - PC 版 `a.tagshow`
   - 单话兜底
6. `searchUrl` 改为 `<js>`，保留原站筛选参数，并支持在关键词后用 `|` 追加条件：
   - `关键词|cate=9`：只看分类 9（單行本·漢化）
   - `关键词|xcate=9`：排除分类 9
   - `关键词|tag=巨乳` / `关键词|xtag=蘿莉`：只看/屏蔽标签
   - `关键词|u=作者` / `关键词|xu=作者`：只看/屏蔽投稿者
   - `关键词|sort=day|week|month|year`：按今日/本周/本月/今年排序
   - 多个条件用 `|` 分隔，例如 `無修正|cate=9|tag=巨乳|sort=month`
   - 分类 ID 已写进 `bookSourceComment`

### 验证

- `python debugger/debugger_cli.py test book_sources/绅士漫画.json --keyword "無修正"`：搜索 24 条、详情、目录、正文全部通过。
- 合集 `photos-index-aid-396541.html`：目录识别 11 章。
- `無修正|cate=9`：返回 24 条，分类均为「單行本·漢化」。
- `無修正|sort=month`：正常返回。

### 经验推广

> 同一站点对手机/桌面 UA 返回不同 DOM 时，**不要只按一种布局写死选择器**。优先用 `||` 合并两套选择器，或把 UA 固定成你实际验证过的那一套。搜索列表、发现列表、详情、目录都可能各有一套布局。

---

*最后更新：2026-10-20*
