# Bug 修复记录

记录各书源、工具的已知问题及修复方案，供后续 AI 或开发者参考，**避免重踩坑**。

> 开工先扫本页；需要专题深潜时按 [`README.md`](README.md) 的“快速索引（按现象）”跳转。
> 每篇保持短小：只留现象、根因、修法和一句可推广经验；完整排查过程放专题文档或案例集。

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
**状态**：✅ 已修复（详见 [`案例-歌书网与起点图网.md`](案例-歌书网与起点图网.md) 的“案例二”）

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

## 绅士漫画 (wnacg 家族) — 移动版双布局失败 → PC 模板重建

**问题时间**：2026-10-20
**文件**：`book_sources/绅士漫画.json`
**状态**：✅ 已重建（PC 模板 + 登录 + 图片线路 + 多章目录）

### 现象（演进）

1. 搜索任意关键词只返回 1 条。
2. 发现页有 4 个分组标题点开为空。
3. 改成“手机 + 桌面双布局合并选择器”后，真机仍不稳定；最终按参考源改用桌面 PC 模板。

### 根因（三个关键坑）

#### 坑 1：`bookUrlPattern` 命中搜索页 → 搜索只剩 1 条

`BookList.analyzeBookList(isSearch = true)` 会先判断搜索地址本身是否像详情页：

```kotlin
if (isSearch) bookSource.bookUrlPattern?.let {
    if (baseUrl.matches(it.toRegex())) {
        getInfoItem(...)   // 把搜索页当成一本书解析
        return bookList    // 直接返回，只有 1 条
    }
}
```

旧正则包含 `(?:photos|albums|comment|search)[-/?]`，搜索地址
`https://站点/search/index.php?...` 完全命中。注意 Kotlin `String.matches` 是整串匹配，
正则必须覆盖整个 URL。

**修复**：只匹配单本详情页，例如
`https?://[^/]+/photos-index-aid-[0-9]+[.]html`，不要包含 `search` / `albums` / `category`。

#### 坑 2：`exploreUrl` 分组标题写成 `"url": ""` → 分类空白

空串会被 `NetworkUtils.getAbsoluteURL(bookSourceUrl, "")` 解析成站点首页；
首页 DOM（如 `ul.col_3_2 > li`）通常不在 `ruleExplore.bookList` 里 → 0 条 → 空白。

**正确写法**：分组标题只写 `title` + `style`，**省略 `url`**
（`ExploreKind.url = null`，点击无动作）。不要写 `"url": ""`。
文本格式的 `exploreUrl` 没有“无链接标题”能力；需要分组标题时改用 JSON 数组。

#### 坑 3：移动/桌面双布局混合规则

站点按 UA 返回两套 DOM。曾用：
`ul#classify_container > li || ul.col_2 > li || div.itemBox || ul.cc > li.gallary_item`
并固定手机 UA。该方案在模拟器可出结果，但真机仍不稳定，且搜索/发现/详情各自有多套布局，维护成本高。

**最终修复**：固定**桌面 Chrome UA**，只写 PC 一套 DOM（`div.gallary_wrap > ul > li` 等），
不再混合两套模板。

### 最终书源要点

- `bookSourceUrl`：`https://www.wn10.shop/`（参考源当前可用域名；换域名只改这里）。
- `header`：桌面 Chrome UA + Referer；站点无 UA 会 403。
- 搜索/发现列表：`div.gallary_wrap > ul > li`、`.info .title a`、`.pic_box img`、`.info_col`。
- 详情：`div#bodywrap h2`、`.asTB .uwthumb img`，分类/页数正则；简介保留参考源的 `<useweb>` 图床线路卡片。
- 正文：`page_url` 提取 + `img1~5.wnimg2.cfd` 线路探测/缓存/TTL。
- 登录：参考源的账号/发布页/检查登录/取最新地址，另加图片线路测速与清缓存。
- 目录：`photos-slide-aid-*` → `photos-item-aid-*`，跳过 `reader-btn`；单话兜底“全一話”；
  合集章节分页用 JS `nextTocUrl`，仅当本页有章节链接时才跟随“後頁”
  （单话详情页底部也有 paginator，不能盲跟）。
- 发现页：9 组 37 个入口；分组标题独占一行且不写 `url`；手机端按钮一行 2 个（`0.46`）。
- 搜索筛选：`关键词|cate=9`、`关键词|tag=巨乳`、`关键词|sort=month`。

### 历史尝试（已废弃，勿照抄）

- 手机 UA + `ul#classify_container > li || ul.col_2 > li || div.itemBox || ul.cc > li.gallary_item` 的合并列表规则。
- 通过 `getDomain()` 读取登录信息里的自定义域名（与参考源登录体系冲突）。
- `exploreUrl` 分组标题写 `"url": ""`。

> 这些方案都曾“看起来能跑”，但分别在真机、登录、发现页上出问题；保留在此仅作警示。

### 验证

- `python debugger/debugger_cli.py test ... --keyword "無修正"`：搜索 24 条、详情、目录、正文通过。
- 合集 `396541`：11 章；大合集 `389914`：分页 6 页合并 67 章。
- 37 个发现入口第 1/2 页实抓均有列表；740 个列表项核心字段非空。
- 真机需确认：登录、图片线路切换、`<useweb>` 简介卡片。

### 经验推广

1. `bookUrlPattern` 只匹配详情页，绝不能匹配搜索/列表页。
2. 发现页分组标题只写 `title/style`，不写 `url`；空串会落到首页。
3. 站点按 UA 分流时，固定一套 UA + 一套 DOM；不要在同一规则里混合两套布局。
4. 有登录/动态域名/图片线路需求的源，优先复用已验证参考源，再替换发现页布局。
5. JS 规则统一 `result=...; result;`；能用正则就不用 `Packages.org.jsoup`，便于本地调试。

---

*最后更新：2026-10-20*
