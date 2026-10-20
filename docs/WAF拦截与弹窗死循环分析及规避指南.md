# Legado WAF拦截机制、弹窗死循环根因分析及规避开发指南

> **文档定位**：WAF / 验证弹窗的根因分析与案例。开工红线摘要见
> [`../skill/SKILL.md`](../skill/SKILL.md) 的 1.9；遇到“验证弹窗死循环、发现页全空、403/202/503”时再读本文。

## 1. 现象描述与背景

在调试大型站点（如“起点中文网”等配备企业级 WAF / 安全网关的站点）时，开发书源常遇到以下两个典型严重问题：

1. **验证弹窗死循环**：
   导入书源后，无论进行搜索还是浏览发现页，阅读 App 都会强制弹出内置浏览器要求“安全验证”。用户完成滑块验证或点击验证通过后，关闭或返回阅读，但立即又弹出新的验证窗口，陷入**无法跳出的验证死循环**。
2. **发现页/分类排行榜内容全空（“已经到底了~”）**：
   在阅读 App 发现页中，所有分类和排行榜（如月票榜、畅销榜、玄幻、都市等）均加载失败，直接显示“已经到底了~”，无法解析出任何书籍列表。

---

## 2. 深度根因分析 (Root Cause Analysis)

经过对 Legado 原生源码（Kotlin）、Android Rhino JS 引擎与站点真实 HTTP 交互链路的逆向分析，确定该现象由以下三个连锁技术陷阱共同导致：

### 陷阱一：WAF 打点脚本引发的误判与“无限验证”死循环

很多开发者习惯在书源的 `loginCheckJs` 中写入通用的 WAF 拦截检测逻辑，例如：
```javascript
// 错误示例：全局文本模糊匹配
if (src.indexOf("x-waf-captcha") !== -1 || src.indexOf("安全验证") !== -1) {
    java.startBrowserAwait(url);
    return java.connect(url);
}
```

#### 致命缺陷：
* **良性脚本内置打点变量**：现代互联网站点（如阅文集团 `m.qidian.com`）即使在**完全正常的 200 OK 页面**中，前端也常驻加载了风控 SDK 与埋点代码。例如 HTML 源码中包含：
  ```html
  <script>(function(){ try { var name = "x-waf-captcha-referer"; ... })();</script>
  ```
* **死循环连锁反应**：
  1. 阅读发起正常的 HTTP 请求，服务端返回 `200 OK` 正常页面。
  2. `loginCheckJs` 拦截检查，发现页面字符串包含 `"x-waf-captcha"`。
  3. 书源**误判为当前请求已被 WAF 拦截**，触发 `java.startBrowserAwait(url)` 强制弹窗。
  4. 用户在弹窗中验证通过并关闭弹窗，执行流程恢复。
  5. 书源重新获取页面（或继续解析），然而返回的正常页面中**依然含有该打点变量**！
  6. `loginCheckJs` 再次命中匹配，再次弹出验证框。
  7. **最终结果**：形成永久无法解除的“无限验证弹窗死循环”。

---

### 陷阱二：`loginCheckJs` 内调用 `java.connect(url)` 导致请求头丢失

在旧版书源的 `loginCheckJs` 中，常有如下代码：
```javascript
java.startBrowserAwait(url);
return java.connect(url); // 致命陷阱
```

#### 致命缺陷：
* **Legado 源码实现原理**：
  在 Legado 源码中，`AnalyzeUrl` 发起请求时会携带书源配置中的专属请求头（例如动态生成的 `_csrfToken` Cookie、特定的 `Referer`、`User-Agent` 等）。
* **请求头丢失**：
  `java.connect(url)` 只是一个基础的裸 GET 请求，**不会继承当前 `AnalyzeUrl` 中所构造的完整 `headerMap`**。
* **业务接口鉴权失败**：
  起点等站点的 AJAX 排行榜接口（如 `/majax/rank/yuepiaolist`）强依赖请求头中的 `Cookie: _csrfToken=...`。
  一旦被 `java.connect(url)` 重发，Cookie 和 Referer 瞬间丢失，服务端直接返回：
  ```json
  {"code": 1, "msg": "失败"}
  ```
  阅读 App 解析不出任何书籍项，从而在 UI 界面上直接显示“已经到底了~”。

---

### 陷阱三：Android Rhino 引擎与 Python 模拟器环境差异（`java.randomUUID()` 缺失）

在开发排查排行榜请求的 CSRF Token 生成时，脚本中曾使用 `java.randomUUID()`：
```javascript
let token = java.getCookie("https://m.qidian.com", "_csrfToken");
if (!token) {
    token = java.randomUUID().toString(); // 致命陷阱
}
```

#### 致命缺陷：
* **环境不一致**：
  部分本地测试工具（或 Python Mock 环境）挂载了 `java.randomUUID`，导致在本地测试时能够成功运行。
* **Android 真实运行崩溃**：
  在 Android Legado 的真实 Rhino 1.8.0 引擎中，注入给 JS 运行时的 `java` 上下文对象是 `io.legado.app.model.analyzeRule.AnalyzeUrl` 或 `AnalyzeRule` 的实例对象，**并未暴露 `randomUUID()` 方法**！
* 在阅读 App 中运行该脚本时会直接触发致命异常：
  `TypeError: java.randomUUID is not a function`
  导致整个发现页请求构造直接崩溃抛错，无法发出有效请求。

---

## 3. Legado 底层原生机制与设计定位

许多开发者误以为必须在书源中手动通过 `loginCheckJs` 处理 Cloudflare / WAF 验证，这是重大的设计误区：

1. **Legado 原生网络层自带验证拦截器**：
   Legado 的 OkHttp Client 内部默认集成了 `CloudflareInterceptor` 和通用 Challenge 处理逻辑。当服务器返回真正的 `403/503 Cloudflare/WAF Challenge` 时，Legado 网络层会自动唤醒内置 WebView 进行过盾处理并自动同步 Cookie。
2. **`loginCheckJs` 的正确职责**：
   `loginCheckJs` 的定位是**业务级别的登录失效或特定权限拦截**（例如特定 JSON 响应 `{"code": 401, "msg": "请先登录"}`），**严禁用于全局 HTML 的粗暴模糊文本匹配**。

---

## 4. 规避指南与书源开发黄金红线

为了彻底杜绝此类问题在其他书源中再次发生，必须严格遵守以下四大开发红线：

### 🛑 红线一：严禁在 `loginCheckJs` 中使用全局模糊关键字匹配

* **严禁**：
  ```javascript
  // 绝对禁止！良性页面的 JS/注释经常包含此类词汇
  src.indexOf("waf") !== -1 || src.indexOf("验证") !== -1 || src.indexOf("captcha") !== -1
  ```
* **正确做法**：
  - 一般网站**直接将 `loginCheckJs` 置空**，交由 Legado 底层 OkHttp 和 Cloudflare 拦截器自动处理。
  - 如确有业务层拦截，必须严格校验**专属 HTTP 状态码**或**专属结构化 JSON 标识**：
    ```javascript
    // 仅在明确命中特定特征且状态码异常时触发
    if (result.status === 401 || (result.status === 403 && src.includes("<title>Access Denied</title>"))) {
        // ...
    }
    ```

### 🛑 红线二：严禁使用 `return java.connect(url)` 进行二次请求

* **严禁**在任何校验脚本中使用 `return java.connect(url)` 作为绕过后的刷新手段，此举必丢 Header 与 Cookie。
* **正确做法**：
  如需重新请求并保持 Header/Cookie，应允许规则自然流转，或通过阅读原生 `CookieStore` 机制让下一个网络周期自动携带持久化的 Cookie。

### 🛑 红线三：严禁依赖未在 Legado 规范中定义的 Java 对象方法

* **严禁**随意调用猜测的 Java 方法（如 `java.randomUUID()`、`java.currentTimeMillis()` 等）。
* **正确做法**：一律使用纯 JavaScript 原生标准实现：
  ```javascript
  // 标准纯 JS UUIDv4 实现（完全兼容 Rhino 引擎）
  function generateUUID() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
      });
  }
  ```

### 🛑 红线四：必须合理持久化 Cookie，避免每次请求重置 Session

* 针对需要 CSRF Token 或 Session 的移动端 API（如起点 `_csrfToken`）：
  ```javascript
  let token = java.getCookie("https://m.qidian.com", "_csrfToken");
  if (!token || token.length < 10) {
      token = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
      });
      // 必须持久化保存到 CookieStore 中
      java.putCookie("https://m.qidian.com", "_csrfToken", token);
  }
  ```
  这样可以确保整套会话在整个 App 运行周期内稳定一致，不会因为不断生成新 Token 而被服务端反爬系统拉黑。

---

## 5. 总结

| 错误模式 | 导致现象 | 正确解决方案 |
| :--- | :--- | :--- |
| `src.indexOf("x-waf-captcha")` | 正常页面打点脚本被误判，弹窗无限循环 | 移除全局模糊检测，由阅读底座自动处理过盾 |
| `return java.connect(url)` | 丢失 `_csrfToken` 等 Header，请求直接报 1 失败 | 绝不在 JS 拦截器中随意重连，保留原生网络上下文 |
| `java.randomUUID()` | Rhino 报错 `is not a function`，发现页彻底瘫痪 | 采用纯 JS 正则替换生成 UUID |
| 每次请求生成新 Token | 会话不一致，容易触发风控拦截 | 使用 `java.getCookie` + `java.putCookie` 保持会话持久 |

