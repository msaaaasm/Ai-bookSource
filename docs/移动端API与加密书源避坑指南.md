# 移动端 API 与加密书源实战避坑指南

> **文档定位**：API / 加密专题。最简红线见 [`../skill/SKILL.md`](../skill/SKILL.md) 的 1.10；
> 对接移动端 REST API、动态签名、AES/DES 时读本文。
>
> 本指南总结自禁漫天堂移动端 API（JMComic App 原生接口）等复杂加密书源的排查与重构实战，系统剖析移动端 RESTful API、动态签名鉴权、AES/DES 密文载荷在 Legado（开源阅读 3.0）环境下的典型陷阱与终极解决方案。

---

## 一、为什么会有 API 体系书源？

在开发漫画站或小说站书源时，通常存在两条技术路线：
1. **Web 网页爬虫路线**：通过阅读内置的 `webView: true` 渲染 PC 或移动网页，依赖 CSS/XPath 提取 DOM 元素。
   - *优势*：直观易懂，所见即所得。
   - *劣势*：受 Cloudflare 5 秒盾、网页广告弹窗、页面改版影响大；加载一次页面需解析大量 JS/CSS/图片，耗时通常在 2~5 秒以上。
2. **移动端原生 API 路线**：直接对接官方手机客户端（Android/iOS App）的 RESTful 接口（如 `/search`、`/album`、`/chapter`）。
   - *优势*：返回纯净 JSON 数据，无广告渲染损耗，接口稳定，速度极快（通常在 200~500ms 内响应）。
   - *劣势*：**通常具备严格的动态鉴权机制（时间戳、签名 Sign、版本号、Token）以及 AES/DES 请求与响应载荷加密**。一旦阅读规则与底层时序没有对齐，极易出现搜索全空、静默崩溃或 401/403 阻断。

---

## 二、API 书源 5 大高频致命陷阱与根本原因

### 陷阱 1：全局 `header` 缺少动态鉴权头（导致初次搜索直接 401 Unauthorized）

#### 【现象描述】
书源在 `searchUrl` 中拼装好了接口参数，并且在规则内也写了带签名的 `Getdata()` 方法，但在阅读中搜索书籍时，搜索结果却始终全空；如果查看日志，可能会看到类似响应：
```json
{"code": 401, "data": [], "errorMsg": "Not legal request."}
```

#### 【阅读底层机制揭秘】
在 Legado 的搜索流程（`SearchBook.kt` / `WebBook.kt`）中：
1. 阅读先执行 `searchUrl` 生成待请求的目标 URL。
2. **阅读底层 OkHttp 引擎会自动提取 `source.header` 中的请求头，并立即发起第一次 HTTP 请求**。
3. 请求完成后，阅读将响应内容赋值给全局变量 `result`，并将请求的目标地址赋值给 `baseUrl`，然后再进入 `ruleSearch.bookList` 进行解析。

#### 【致命错误】
很多作者认为只要在 `ruleSearch.bookList` 中调用自定义的 `Getdata(baseUrl)` 传签名即可，因此在全局 `header` 中只写了普通的静态 UA 和 Cookie。  
**结果**：阅读发起的**第一次网络请求**因为没有带上 API 必需的动态鉴权参数（如 `tokenparam: {timestamp},{version}`），直接被服务器返回了 `401 Unauthorized`！

#### 【终极防错解法】
全局 `header` 必须为 `<js>` 脚本，动态计算时间戳并注入鉴权头：
```javascript
<js>
eval(String(source.loginUrl));
var hostUrl = Get('url') || 'https://www.cdnhjk.net';
var time = String(Date.now()).slice(0, 10);
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36 EdgA/127.0.0.0",
    "Cookie": cache.get(java.md5Encode16(hostUrl + "cookie")) || cookie.getCookie(hostUrl),
    "tokenparam": time + "," + JMversion,
    "proxy": ""
};
cache.put(java.md5Encode16(hostUrl + "headers"), JSON.stringify(headers));
cache.put(java.md5Encode16(hostUrl + "last_time"), time); // 缓存时间戳供解密复用
JSON.stringify(headers);
</js>
```

---

### 陷阱 2：JavaScript 假值短路逻辑漏洞（导致请求裸奔丢失 UA，被 Cloudflare 拦截 403）

#### 【现象描述】
即使调用了专门发请求的函数，请求依然频繁失败或被拦截，手机抓包发现响应为 `403 Forbidden`。

#### 【代码逻辑漏洞】
许多书源中普遍存在类似这样一段“看似完美”的容错代码：
```javascript
// 错误示例：
headers = JSON.parse(cache.get(...) || '{}') || { 'User-Agent': 'Mozilla/5.0...' };
```

#### 【致命机制】
在 JavaScript 规范中：
* 空对象 `{}` 是 **Truthy（真值）**，即 `Boolean({}) === true`！
* 当 `cache.get(...)` 为空时，`JSON.parse('{}')` 返回空对象 `{}`。
* 由于左侧表达式是真值，`||` 逻辑运算符**直接短路返回 `{}`，后面的 `{ 'User-Agent': ... }` 根本不会执行**！
* 最终发送网络请求时，`headers` 沦为没有任何 `User-Agent` 的空头。Cloudflare、Akamai 等主流 WAF 只要识别到无 UA 的请求，会直接抛出 **HTTP 403 Forbidden**，请求在网关层被瞬间掐死！

#### 【终极防错解法】
不要使用对象级别的 `||` 短路兜底，必须显式判定属性：
```javascript
var headers = {};
try {
    headers = JSON.parse(cache.get(...) || '{}');
} catch(e) {}

// 显式校验关键属性
if (!headers || !headers['User-Agent']) {
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36 EdgA/127.0.0.0'
    };
}
```

---

### 陷阱 3：初始化时序错位与 `undefined` 拼接崩溃

#### 【现象描述】
书源刚导入阅读或清空缓存后第一次搜索，直接报错闪退或提示 `no protocol: undefined/xxx`。

#### 【执行时序剖析】
在阅读中，各规则脚本的执行顺序具有明确时序：
```
用户点击搜索 → 执行 source.header → 执行 searchUrl → OkHttp 发起搜索请求 → 执行 ruleSearch.bookList
```
* **问题爆发点**：在初次搜索时，`source.header` 会在 `searchUrl` 之前运行。
* 此时若尚未调用 `source.setVariable()`，`Get('url')` 就会返回 `undefined`！
* 如果代码中写了：
  ```javascript
  cache.put(java.md5Encode16(Get('url') + 'headers'), ...); // 存成了 "undefinedheaders"！
  java.ajax(Get('url') + '/setting');                      // 请求了 "undefined/setting" 抛异常！
  ```
  1. 缓存键变成了 `undefinedheaders`，导致后续按真实域名查缓存永远为 `null`；
  2. 请求 `"undefined/setting"` 触发 `java.net.MalformedURLException: no protocol: undefined/setting` 严重异常，导致整个脚本进程中断。

#### 【终极防错解法】
1. **统一兜底域名**：所有获取当前主域名的函数必须有静态兜底：
   ```javascript
   var hostUrl = Get('url') || 'https://www.cdnhjk.net';
   ```
2. **提前预热初始化**：在 `header` 的第一行就执行 `eval(String(source.loginUrl))`，确保 `$$$` 全局变量和持久化存储在第一次网络交互前就已完整装载。

---

### 陷阱 4：关键词粗暴正则过滤腰斩多词搜索

#### 【现象描述】
搜索单个词（如 `秘密`）能出结果，但搜索多词或复合词（如 `秘密 教学`、`斗罗 2`）却只能搜出单字或完全无内容。

#### 【代码根因】
在部分模板书源的 `searchUrl` 中，作者为了“去除特殊字符”，使用了极为粗暴的正则截断：
```javascript
// 错误示例：腰斩式过滤
return `${Get('url')}/search?search_query=${e.replace(/\s.*$|\/.*$/g, '')}`;
```
* `\s.*$` 的含义是：**匹配从第一个空白字符开始直到字符串结尾的所有内容并删除**！
* 当用户搜索 `秘密 教学` 时，` 教学` 被直接削掉，实际上只向服务端请求了 `秘密`。
* 且原代码未使用 `encodeURIComponent`，中文和特殊符号可能在传参给服务端时出现乱码。

#### 【终极防错解法】
使用标准的 `.trim()` 和 `encodeURIComponent()`：
```javascript
<js>
eval(String(source.loginUrl));
(function (e) {
    if (Get('search_TC') == true || e.indexOf('TC') > -1) {
        e = String(java.s2t(e)).replace(/TC/, '');
    }
    e = e.trim(); // 仅去除首尾多余空格，保留中间空格
    java.put(java.md5Encode16(Get('url') + "searchkey"), e);
    T = `{{get('t',Get('o'))}}`;
    Area = `{{get('area',Get('u'))}}`;
    Type = `{{get('type',Get('v'))}}`;
    if (/^jm\d+$/i.test(e)) return `{{Get('url')}}/album?id=${e.replace(/jm/i, '')}`;
    return `{{Get('url')}}/search?search_query=${encodeURIComponent(e)}${Area}${Type}${T}&page={{page}}`;
}(key));
</js>
```

---

### 陷阱 5：双重请求造成性能腰斩与 0ms 本地解密技巧

#### 【性能痛点剖析】
在传统的 API 书源中，作者往往直接在 `ruleSearch.bookList` 中写：
```javascript
// 低效做法：完全丢弃 result，发起二次网络请求
list = JSON.parse(Getdata(baseUrl)).content || [];
```
* **严重浪费**：阅读在执行 `ruleSearch` 之前，已经通过 `searchUrl` 拿着 `source.header` 发送过一次 HTTP 请求，并将服务端的原始密文存入了变量 `result`。
* 如果再次调用 `Getdata(baseUrl)`，相当于对同一个关键词**连续发起了两次一模一样的网络请求**！不仅搜索变慢一倍，还极易触发服务器的高频限流。

#### 【终极性能优化方案（本地优先解密 + 降级兜底）】
在 `source.header` 中生成时间戳时，顺手将其存入 `cache`：
```javascript
cache.put(java.md5Encode16(hostUrl + "last_time"), time);
```
在 `ruleSearch.bookList` 中，优先使用该时间戳直接对 `result` 执行本地 AES 解密（耗时 0ms 纯本地计算！），解密失败才平滑降级调用网络函数 `Getdata(baseUrl)`：
```javascript
<js>
eval(String(source.loginUrl));
var data = [];
var list = [];
var resStr = '';

// 1. 优先尝试本地解密阅读初次请求带回的 result（0ms 秒开）
try {
    var resObj = JSON.parse(result);
    if (resObj && resObj.code == 200 && typeof resObj.data === 'string') {
        var lastTime = cache.get(java.md5Encode16(Get('url') + "last_time"));
        if (lastTime) {
            var sign = java.md5Encode(lastTime + data_secret);
            resStr = java.aesBase64DecodeToString(resObj.data, sign, 'AES/ECB/PKCS7Padding', '');
        }
    }
} catch(e) {}

// 2. 若初次请求解密失败（如时间戳失效或初次请求失败），降级调用网络函数 Getdata 重新请求
if (!resStr) {
    try {
        resStr = Getdata(baseUrl);
    } catch(e) {}
}

// 3. 解析列表
try {
    list = JSON.parse(resStr).content || [];
} catch(e) {}

// 4. 组装返回书籍结构...
Put(JSON.stringify(data));
</js>
```

---

## 三、常用移动端加解密算法在阅读中的标准实现

阅读底层（Android Rhino 引擎）为 JS 上下文注入了丰富的 Java 原生密码学工具：

### 1. MD5 哈希计算
```javascript
// 计算普通 MD5 字符串（32位小写）
var md5Str = java.md5Encode("要计算的内容");

// 计算 16 位 MD5 字符串
var md5Short = java.md5Encode16("要计算的内容");
```

### 2. AES / DES 密文解密
```javascript
// 参数：密文(Base64), 密钥Key, 模式/填充, 偏移量IV(无IV传空字符串)
var decrypted = java.aesBase64DecodeToString(
    cipherTextBase64, 
    keyString, 
    'AES/ECB/PKCS7Padding', 
    ''
);
```

### 3. 繁简转换
```javascript
var s = java.t2s("繁體字"); // 繁转简
var t = java.s2t("简体字"); // 简转繁
```

---

## 四、自检清单（Checklist）

在编写或重构任何基于移动端 API、动态签名或加解密的书源时，请逐一检查以下项目：

- [ ] **1. Header 鉴权完整性**：全局 `header` 是否通过 `<js>` 动态计算并注入了当前时间戳及 Sign/Token？
- [ ] **2. Header UA 兜底性**：获取 `headers` 时是否显式判断了 `!headers['User-Agent']`，确保无论任何情况下都有有效 UA？
- [ ] **3. 变量初始化兜底**：`Get('url')` 是否有类似 `|| 'https://默认域名'` 的静态兜底？
- [ ] **4. 搜索参数编码**：`searchUrl` 是否使用 `encodeURIComponent()` 编码，且未误用正则表达式腰斩多词空格？
- [ ] **5. 响应复用解密**：搜索列表规则是否优先尝试对 `result` 执行本地解密，避免无效的双重网络请求？
- [ ] **6. 错误静默阻断**：所有 JSON 解析与网络降级是否包裹在 `try-catch` 中，避免脚本崩溃导致阅读界面假死？

