# 📚 书源示例库 (Book Source Examples)

本目录为 AI 提供了常见类型的 Legado 规范书源参考实现，覆盖各类典型网站架构与反爬对抗场景。另一个 AI 在接手开发任务时，可根据目标网站的技术栈直接对照以下示例结构进行编写。

---

## 示例清单与场景对照

| 文件名 | 对应类型 / 典型场景 | 核心技术点 | 参考来源 |
| :--- | :--- | :--- | :--- |
| `standard_html_example.json` | **标准 HTML 渲染站** | CSS 选择器、多级页面链接拼接、相对路径补全、目录与正文提取 | 顶点小说 / 笔趣阁类 |
| `api_json_example.json` | **API / JSON 数据站** | JSONPath 提取 (`$.data.list[*]`)、URL 参数模板构建、时间戳/签名处理 | 番茄小说 / 移动端接口 |
| `dynamic_api_example.json` | **正文动态鉴权 / 跨域 API 站** | `<js>` 脚本调用 `java.ajax`、备用域名动态轮询切换、`source.setVariable` 状态存储 | 笔趣阁 bqgui 类 |
| `waf_security_example.json` | **WAF 防火墙 / 验证码挑战站** | `loginCheckJs` 拦截检测 (202/403/probe.js)、静默 `java.webView` 自动绕过、`java.startBrowserAwait` 手动滑块降级、Flex 多维排行榜发现页 | 起点中文网官方站 |

---

## 典型编写范式速查

### 1. 标准 HTML 提取 (CSS 选择器)
- **书籍列表**：`"bookList": ".y-list__item"`
- **链接与属性**：`"bookUrl": "a@href"`、`"coverUrl": "img@data-src##^//##https://"`
- **正文多段合并**：`"content": ".content@p@html"`

### 2. 纯 JSON API 提取 (JSONPath)
- **列表**：`"bookList": "$.data.records[*]"`
- **字段**：`"name": "$.book_name"`、`"author": "$.author"`
- **URL 模板变量替换**：`"bookUrl": "https://api.example.com/book/{{$.book_id}}"`

### 3. 反爬与 WAF 穿透 (`loginCheckJs`)
- **状态码监听**：捕获 202（腾讯 WAF 等 Challenge 探测）、403、503、429
- **自动 WebView 穿透**：优先在后台静默执行 4 秒获取 Cookie
- **用户交互降级**：若静默失败，使用 `java.startBrowserAwait(url, title)` 唤起阅读内置浏览器完成滑块拖动
