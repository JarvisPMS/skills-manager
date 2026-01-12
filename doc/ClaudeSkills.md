# Claude Code Agent Skills 规范

> 来源: https://code.claude.com/docs/en/skills
>
> 本文档介绍如何在 Claude Code 中创建、使用和管理 Agent Skills。

## 概述

**Skill** 是一个 Markdown 文件，用于教 Claude 如何执行特定任务：例如使用团队标准审查 PR、按首选格式生成提交消息、或查询公司数据库架构。当你的请求匹配 Skill 的功能时，Claude 会自动应用它。

### 技能工作原理

Skills 是**模型调用**的：Claude 根据你的请求决定使用哪些 Skill，你无需显式调用 Skill。当请求匹配 Skill 的描述时，Claude 会自动应用相关的 Skills。

发送请求时，Claude 按以下步骤查找和使用相关的 Skills：

1. 分析请求内容
2. 匹配相关 Skill 的描述
3. 自动加载并应用 Skill

## Skills 的存储位置

| 位置 | 路径 | 适用范围 |
| --- | --- | --- |
| 企业级 | 见托管设置 | 组织内所有用户 |
| 个人级 | `~/.claude/skills/` | 你个人，所有项目 |
| 项目级 | `.claude/skills/` | 此仓库的所有协作者 |
| 插件级 | 插件捆绑 | 安装了插件的所有人 |

**优先级规则**：如果两个 Skills 同名，优先级从高到低为：企业级 > 个人级 > 项目级 > 插件级。

##何时使用 Skills

Claude Code 提供多种自定义行为的方式。关键区别是：**Skills 由 Claude 根据请求自动触发**，而斜杠命令需要你显式输入 `/command`。

| 使用方式 | 何时使用 | 运行时机 |
| --- | --- | --- |
| **Skills** | 给 Claude 专业知识（如"按我们的标准审查 PR"） | Claude 选择相关时 |
| **Slash 命令** | 创建可重用的提示（如 `/deploy staging`） | 你输入 `/command` 运行 |
| **CLAUDE.md** | 设置项目级指令（如"使用 TypeScript 严格模式"） | 加载到每个对话 |
| **Subagents** | 将任务委托给有独立工具的独立上下文 | Claude 委托或你显式调用 |
| **Hooks** | 在事件上运行脚本（如文件保存时检查） | 在特定工具事件上触发 |
| **MCP 服务器** | 连接 Claude 到外部工具和数据源 | Claude 根据需要调用 MCP 工具 |

### Skills vs Subagents

- **Skills**: 向当前对话添加知识
- **Subagents**: 在有自己工具的独立上下文中运行

使用场景：用 Skills 提供指导和标准；当需要隔离或不同的工具访问时使用 Subagents。

### Skills vs MCP

- **Skills**: 告诉 Claude _如何使用_ 工具
- **MCP**: _提供_ 工具

例如：MCP 服务器连接 Claude 到数据库，而 Skill 教 Claude 数据模型和查询模式。

## 配置 Skills

### 编写 SKILL.md

`SKILL.md` 文件是 Skill 中唯一必需的文件。它包含两部分：

1. **YAML 元数据**（在 `---` 标记之间的部分）
2. **Markdown 指令**（告诉 Claude 如何使用该 Skill）

**基本结构**：
```markdown
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
```

#### 可用的元数据字段

| 字段 | 必需 | 描述 |
| --- | --- | --- |
| `name` | 是 | Skill 名称。必须仅使用小写字母、数字和连字符（最多 64 字符）。应与目录名匹配。 |
| `description` | 是 | Skill 的功能和使用时机（最多 1024 字符）。Claude 用此决定何时应用 Skill。 |
| `allowed-tools` | 否 | Skill 激活时 Claude 可无需权限使用的工具。支持逗号分隔值或 YAML 风格列表。 |
| `model` | 否 | Skill 激活时使用的模型（如 `claude-sonnet-4-20250514`）。默认为对话的模型。 |
| `context` | 否 | 设置为 `fork` 以在独立的子代理上下文中运行该 Skill，拥有自己的对话历史。 |
| `agent` | 否 | 当设置 `context: fork` 时指定使用的代理类型（如 `Explore`、`Plan`、`general-purpose` 或 `.claude/agents/` 中的自定义代理名称）。仅在结合 `context: fork` 时适用。 |
| `hooks` | 否 | 定义此 Skill 生命周期范围的钩子。支持 `PreToolUse`、`PostToolUse` 和 `Stop` 事件。 |
| `user-invocable` | 否 | 控制 Skill 是否出现在斜杠命令菜单中。不影响 `Skill` 工具或自动发现。默认为 `true`。 |

### 更新或删除 Skill

- **更新**：直接编辑 `SKILL.md` 文件
- **删除**：删除该目录

更改立即生效。

### 使用渐进式披露添加支持文件

Skills 与对话历史、其他 Skills 和你的请求共享 Claude 的上下文窗口。为保持上下文聚焦，使用**渐进式披露**：将基本信息放在 `SKILL.md` 中，详细参考资料放在单独文件中，Claude 仅在需要时读取。

#### 多文件 Skill 结构示例

```
my-skill/
├── SKILL.md (必需 - 概述和导航)
├── reference.md (详细 API 文档 - 按需加载)
├── examples.md (使用示例 - 按需加载)
└── scripts/
    └── helper.py (实用脚本 - 执行但不加载)
```

**SKILL.md 引用示例**：
```markdown
## Overview
[基本指令]

## Additional resources
- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)

## Utility scripts
To validate input files, run the helper script:
```bash
python scripts/helper.py input.txt
```
```

### 使用 allowed-tools 限制工具访问

使用 `allowed-tools` frontmatter 字段限制 Skill 激活时 Claude 可以使用的工具。

```yaml
---
name: reading-files-safely
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---
```

或使用 YAML 列表以提高可读性：

```yaml
---
name: reading-files-safely
description: Read files without making changes. Use when you need read-only file access.
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

使用场景：
- 只读 Skills 不应修改文件
- 有限范围的 Skills：例如，仅数据分析，不写文件
- 安全敏感工作流需要限制功能

### 在分叉上下文中运行 Skills

使用 `context: fork` 在隔离的子代理上下文中运行 Skill，拥有自己的对话历史。适用于执行复杂多步操作而不混乱主对话的 Skills：

```yaml
---
name: code-analysis
description: Analyze code quality and generate detailed reports
context: fork
---
```

### 为 Skills 定义 Hooks

Skills 可以定义在 Skill 生命周期期间运行的 Hooks。使用 `hooks` 字段指定 `PreToolUse`、`PostToolUse` 或 `Stop` 处理程序：

```yaml
---
name: secure-operations
description: Perform operations with additional security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh $TOOL_INPUT"
          once: true
---
```

`once: true` 选项使 Hook 每会话仅运行一次。首次成功执行后，Hook 被移除。

### 控制 Skill 可见性

Skills 可以通过三种方式调用：

1. **手动调用**：你在提示中输入 `/skill-name`
2. **程序调用**：Claude 通过 `Skill` 工具调用
3. **自动发现**：Claude 读取 Skill 的描述并在与对话相关时加载

`user-invocable` 字段仅控制手动调用。设置为 `false` 时，Skill 从斜杠命令菜单隐藏，但 Claude 仍可程序调用或自动发现。

#### 使用场景

| 设置 | 斜杠菜单 | `Skill` 工具 | 自动发现 | 使用场景 |
| --- | --- | --- | --- | --- |
| `user-invocable: true` (默认) | 可见 | 允许 | 是 | 你希望用户直接调用的 Skills |
| `user-invocable: false` | 隐藏 | 允许 | 是 | Claude 可用但用户不应手动调用的 Skills |

### Skills 和 Subagents

#### 给子代理访问 Skills

子代理不自动继承主对话的 Skills。要给自定义子代理访问特定 Skills，在子代理的 `skills` 字段中列出它们：

```markdown
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Review code for quality and best practices
skills: pr-review, security-check
---
```

每个列出 Skill 的完整内容在启动时注入到子代理的上下文中，而不仅仅是可供调用。

#### 在子代理上下文中运行 Skill

使用 `context: fork` 和 `agent` 在分叉子代理中运行 Skill，拥有独立的上下文。

### 分发 Skills

- **项目 Skills**：将 `.claude/skills/` 提交到版本控制。任何克隆仓库的人都获得这些 Skills。
- **插件**：跨多个仓库共享 Skills，在插件中创建 `skills/` 目录，包含 `SKILL.md` 文件的 Skill 文件夹。通过插件市场分发。
- **托管**：管理员可以通过托管设置在组织范围内部署 Skills。

## 示例

### 简单 Skill（单文件）

最小 Skill 仅需包含 frontmatter 和指令的 `SKILL.md` 文件。

**结构**：
```
commit-helper/
└── SKILL.md
```

**SKILL.md 内容**：
```markdown
---
name: generating-commit-messages
description: Generates clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.
---

# Generating Commit Messages

## Instructions

1. Run `git diff --staged` to see changes
2. I'll suggest a commit message with:
   - Summary under 50 characters
   - Detailed description
   - Affected components

## Best practices

- Use present tense
- Explain what and why, not how
```

### 使用多文件

对于复杂 Skills，使用渐进式披露保持主 `SKILL.md` 聚焦，同时在支持文件中提供详细文档。

**结构**：
```
pdf-processing/
├── SKILL.md              # 概述和快速入门
├── FORMS.md              # 表单字段映射和填充指令
├── REFERENCE.md          # pypdf 和 pdfplumber 的 API 详细信息
└── scripts/
    ├── fill_form.py      # 填充表单字段的实用工具
    └── validate.py       # 检查 PDF 的必填字段
```

**SKILL.md 内容**：
```markdown
---
name: pdf-processing
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber packages.
allowed-tools: Read, Bash(python:*)
---

# PDF Processing

## Quick start

Extract text:
```python
import pdfplumber
with pdfplumber.open("doc.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For form filling, see [FORMS.md](FORMS.md).
For detailed API reference, see [REFERENCE.md](REFERENCE.md).

## Requirements

Packages must be installed in your environment:
```bash
pip install pypdf pdfplumber
```
```

## 故障排除

### 查看和测试 Skills

要查看 Claude 有权访问的 Skills，问 Claude 如"What Skills are available?"的问题。Claude 在对话开始时将所有可用 Skill 名称和描述加载到上下文窗口中。

**测试特定 Skill**：要求 Claude 执行与 Skill 描述匹配的任务。例如，如果你的 Skill 描述为"Reviews pull requests for code quality"，要求 Claude"Review the changes in my current branch"。

### Skill 未触发

`description` 字段是 Claude 决定是否使用你的 Skill 的方式。模糊的描述如"Helps with documents"不会给 Claude 足够的信息将 Skill 匹配到相关请求。

**好的描述应回答两个问题**：

1. **此 Skill 有什么功能？** 列出具体能力。
2. **Claude 应何时使用它？** 包括用户会提到的触发术语。

```markdown
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

这个描述有效，因为它命名了具体操作（extract、fill、merge）并包含用户会说的关键字（PDF、forms、document extraction）。

### Skill 未加载

**检查文件路径**：Skills 必须在正确的目录中，文件名为 `SKILL.md`（区分大小写）：

| 类型 | 路径 |
| --- | --- |
| Personal | `~/.claude/skills/my-skill/SKILL.md` |
| Project | `.claude/skills/my-skill/SKILL.md` |
| Enterprise | 见平台特定路径 |
| Plugin | 插件目录内的 `skills/my-skill/SKILL.md` |

**检查 YAML 语法**：frontmatter 中的无效 YAML 会阻止 Skill 加载。frontmatter 必须在第 1 行以 `---` 开始（前面没有空行），在 Markdown 内容前以 `---` 结束，使用空格缩进（不是制表符）。

**运行调试模式**：使用 `claude --debug` 查看 Skill 加载错误。

### Skill 有错误

**检查依赖项是否已安装**：如果 Skill 使用外部包，它们必须在你的环境中安装。

**检查脚本权限**：脚本需要执行权限：`chmod +x scripts/*.py`

**检查文件路径**：在所有路径中使用正斜杠（Unix 风格）。使用 `scripts/helper.py`，而不是 `scripts\\helper.py`。

### 多个 Skills 冲突

如果 Claude 使用错误的 Skill 或在类似 Skills 之间混淆，描述可能太相似。通过使用特定触发术语使每个描述不同。

例如，不要两个 Skills 描述中都有"data analysis"，而是区分它们：一个用于"sales data in Excel files and CRM exports"，另一个用于"log files and system metrics"。

### 插件 Skills 未出现

**症状**：从市场安装了插件，但问 Claude"What Skills are available?"时其 Skills 不出现。

**解决方案**：清除插件缓存并重新安装：

```bash
rm -rf ~/.claude/plugins/cache
```

然后重启 Claude Code 并重新安装插件：

```bash
/plugin install plugin-name@marketplace-name
```

**如果 Skills 仍未出现**，验证插件的目录结构正确。Skills 必须在插件根目录的 `skills/` 目录中：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── my-skill/
        └── SKILL.md
```

## 命名规范

Skill 目录名称必须与 SKILL.md 中的 `name` 字段一致：

- 必须仅使用小写字母、数字和连字符
- 最多 64 个字符
- 不能以连字符开头或结尾
- 不能包含连续连字符（`--`）

**正则表达式验证**：`^[a-z0-9-]+$`

## 最佳实践

1. **描述要具体**：在 `description` 中明确说明 Skill 的功能和使用场景，包含触发关键词
2. **使用渐进式披露**：基本信息放在 SKILL.md，详细内容放在支持文件
3. **限制工具访问**：使用 `allowed-tools` 限制 Skill 的权限范围
4. **脚本零上下文执行**：实用脚本可以被执行而不加载到上下文
5. **多文件结构**：对于复杂 Skills，使用参考文档和示例文件提高可维护性
