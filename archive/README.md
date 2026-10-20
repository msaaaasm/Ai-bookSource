# 归档目录（archive）

这里存放**历史资料**，日常开发书源不需要阅读。保留它们是为了可追溯，不要把它们当作现行规范。

| 子目录 | 内容 | 说明 |
|---|---|---|
| `old-agent/` | 旧版 Coze/LangChain 智能体的系统提示词、配置、自我认知、话术库、编码检测工具说明 | 其中提到的 `search_knowledge`、`smart_fetch_html`、`detect_charset`、`edit_book_source` 等工具在本仓库中**不存在**，不要照做 |
| `skill-history/` | `SKILL.md` 的 v0.1 ~ v0.7 历史版本 | 仅用于对比演进，规则可能已经过时或自相矛盾 |
| `duplicates/` | 与其他知识文件重复的内容 | 当前规范以 `knowledge/` 下的文件为准 |
| `legacy-index/` | 旧的 `knowledge_index.json`、`metadata.json`、`learned_sources.json` | 索引指向的文件已经调整，**不再维护**，不要依赖 |
| `legacy-tools/` | 一次性脚本（如 `generate_18comic.py`） | 可作为复杂书源的生成思路参考，不是通用工具 |

现行文档入口：

- 项目总览：[`../README.md`](../README.md)
- AI 工作手册：[`../skill/SKILL.md`](../skill/SKILL.md)
- 知识库导航：[`../knowledge/README.md`](../knowledge/README.md)
- 排错与检查：[`../docs/README.md`](../docs/README.md)
