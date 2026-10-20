# 书源提交前检查清单

> 每一项都通过再交付。模拟器通过不代表真机通过，标注“真机”的项必须在 Legado App 里确认。

---

## 一、JSON 与文件

- [ ] 文件是 UTF-8、标准 JSON，**最外层是数组** `[...]`
- [ ] 无注释、无尾随逗号、无 Markdown 代码围栏
- [ ] 用命令校验通过：

```bash
python -c "import json; d=json.load(open('book_sources/书名.json', encoding='utf-8')); print(type(d).__name__, len(d))"
```

- [ ] 文件位于 `book_sources/<纯中文名>.json`
- [ ] 没有覆盖用户已有的同名书源（如要覆盖，先确认）

---

## 二、命名与分组

- [ ] `bookSourceName` 是纯中文名称
- [ ] 不含域名、`.com`、`(xxx.com)`、`[xxx]`
- [ ] 不含 Emoji、图标、装饰符号
- [ ] `bookSourceGroup` 是 `""`（不预设分组）
- [ ] `bookSourceUrl` 是站点根地址，不是搜索页/详情页
- [ ] `bookSourceType` 正确：`0` 文字、`1` 音频、`2` 图片、`3` 文件、`4` 视频

快速检查：

```bash
python - <<'PY'
import json, re
d = json.load(open('book_sources/书名.json', encoding='utf-8'))
s = d[0] if isinstance(d, list) else d
print('name:', s.get('bookSourceName'))
print('group:', repr(s.get('bookSourceGroup')))
print('type:', s.get('bookSourceType'))
name = s.get('bookSourceName', '')
print('contains ascii/domain:', bool(re.search(r'[A-Za-z0-9.]', name)))
print('contains emoji:', bool(re.search(r'[\U0001F300-\U0001FAFF☀-➿]', name)))
PY
```

---

## 三、字段完整性

- [ ] `bookSourceUrl`、`bookSourceName` 非空
- [ ] 需要搜索的源：`searchUrl` 非空
- [ ] `ruleSearch.bookList`、`name`、`bookUrl` 非空
- [ ] `ruleToc.chapterList`、`chapterName`、`chapterUrl` 非空
- [ ] `ruleContent.content` 非空
- [ ] 有发现页时：`exploreUrl` 与 `ruleExplore` 配套
- [ ] 没有使用 `prevContentUrl`
- [ ] 没有编造的字段名

---

## 四、搜索

- [ ] 请求方法（GET/POST）与站点一致
- [ ] 搜索参数名正确（`q` / `keyword` / `searchkey` / ...）
- [ ] 编码正确（GBK 站点已加 `charset: "gbk"`）
- [ ] 需要 Header/Cookie/Token 的已补齐
- [ ] 搜索结果非空
- [ ] `name` 有值
- [ ] `bookUrl` 是完整可访问的详情页链接
- [ ] `author` / `kind` / `lastChapter` / `intro` 有值（页面有时）
- [ ] `coverUrl` 有值且不是占位图；懒加载已处理
- [ ] 相对链接/`//` 链接已正确处理

```bash
python debugger/debugger_cli.py search book_sources/书名.json --keyword "测试词" --output json
```

---

## 五、详情页

- [ ] `name` 正确
- [ ] `author` 正确（没有“作者：”前缀）
- [ ] `coverUrl` 可加载
- [ ] `intro` 正确，没有导航/广告混入
- [ ] `kind` / `lastChapter` / `wordCount` 有值（页面有时）
- [ ] 能拿到目录 URL（`tocUrl` 或 `bookUrl` 本身）

```bash
python debugger/debugger_cli.py info book_sources/书名.json --url "<详情URL>"
```

---

## 六、目录

- [ ] `chapterList` 数量与页面一致
- [ ] 第一章、最后一章都存在
- [ ] 章节名没有多余序号/广告
- [ ] 章节 URL 可访问
- [ ] 目录分页已处理（`nextTocUrl`）
- [ ] 倒序目录已反转
- [ ] 重复章节已去除
- [ ] 分卷站点已正确处理卷名/章节

```bash
python debugger/debugger_cli.py toc book_sources/书名.json --url "<目录URL>"
```

---

## 七、正文

- [ ] `content` 有正文，不是导航/广告/空壳
- [ ] 段落保留正确（需要时用 `@html`）
- [ ] 广告、域名、提示语已清理
- [ ] **同一章分页**已填 `nextContentUrl`
- [ ] **下一章**没有误填进 `nextContentUrl`
- [ ] 图片源：图片 URL 完整、可加载、数量正确
- [ ] 音频/视频源：媒体 URL 可播放

```bash
python debugger/debugger_cli.py content book_sources/书名.json --url "<正文URL>"
```

---

## 八、发现页（如果有）

- [ ] `exploreUrl` 的每个 URL 都能打开
- [ ] `{{page}}` 位置与站点分页格式一致
- [ ] 分类名与站点一致
- [ ] 列表规则能出书
- [ ] 封面/作者/简介正常
- [ ] 排行榜与分类冲突时已处理
- [ ] **排版**：分组标题独占一行（`layout_flexBasisPercent: 1` + `layout_wrapBefore: true`）
- [ ] **排版**：分组标题**不写 `url`**，尤其不能写 `"url": ""`（会打开首页/空列表）
- [ ] **排版**：手机端按钮一行 2 个（`layout_flexBasisPercent: 0.46`），没有四列挤压
- [ ] **排版**：每个按钮文字在手机上完整显示，没有被截断成“雜誌短…”

---

## 九、特殊场景

- [ ] **WAF/Cloudflare**：`loginCheckJs` 没有全局模糊匹配；没有 `java.connect` 二次请求；没有无限弹窗
- [ ] **移动端 API**：`header` 带全鉴权；没有 `{}` 真值短路；域名有兜底
- [ ] **加密响应**：解密逻辑可复现；失败有降级
- [ ] **WebView**：`webJs` 不是空轮询；有超时/失败处理
- [ ] **Rhino JS**：没有 `java.randomUUID()`；Java String 已 `String(...)` 包装
- [ ] **Cookie/Token**：已持久化，不是每次重新生成
- [ ] **编码**：中文无乱码

---

## 十、真机验证（必须）

- [ ] 导入书源成功
- [ ] 搜索出结果
- [ ] 打开详情页，信息正确
- [ ] 打开目录，能翻到最后一章
- [ ] 打开正文，内容完整
- [ ] 有发现页的，能正常浏览
- [ ] 连续阅读 3 章无异常
- [ ] 没有反复弹验证/白屏/闪退

---

## 十一、交付说明

- [ ] 在对话中给出完整 JSON（可复制导入）
- [ ] 说明测试结果：哪些通过、哪些未验证
- [ ] 说明已知限制（需要登录、需要代理、需要 WebView 等）
- [ ] 如有新踩坑，已更新 [`BUG_FIXES.md`](BUG_FIXES.md)

---

## 附：一键跑完四个阶段

```bash
python debugger/debugger_cli.py test book_sources/书名.json --keyword "测试词"
```

`test` 会依次跑搜索、详情、目录、正文。任何一步失败，先用对应的单阶段命令定位。
