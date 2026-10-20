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

*最后更新：2026-10-20*
