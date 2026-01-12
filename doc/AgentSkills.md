# Agent Skills 官方文档总结

> 本文档基于 https://agentskills.io/ 官方网站内容整理
> 包括：Overview、What are Skills、Specification、Integrate Skills

---

## 一、概述 (Overview)

### 什么是 Agent Skills？

**Agent Skills** 是一种包含指令、脚本和资源的文件夹格式，代理可以发现并使用它们来更准确、更高效地完成任务。它们代表了一种简单、开放的格式，为代理提供新的能力和专业知识。

### 解决的核心问题

AI 代理的能力日益强大，但往往缺乏可靠工作所需的上下文。Agent Skills 通过以下方式解决这个问题：

- 为代理提供**程序性知识**访问
- 共享代理可以按需加载的**公司、团队和用户特定的上下文**
- 使代理能够根据特定任务扩展能力

### 主要价值

#### 对技能作者
- 构建一次，跨多个代理产品部署
- 创建可复用、可移植的技能包

#### 对兼容代理
- 终端用户可以开箱即用地为代理提供新能力
- 支持行业标准格式

#### 对团队和企业
- 将组织知识捕获在可移植、版本控制的包中
- 实现可重复、可审计的工作流程

### Agent Skills 的应用场景

1. **领域专业知识**：将专业知识打包成可复用的指令
   - 法律审查流程
   - 数据分析管道

2. **新能力**：赋予代理新能力，如：
   - 创建演示文稿
   - 构建 MCP 服务器
   - 分析数据集

3. **可重复工作流**：将多步骤任务转化为一致且可审计的流程

4. **互操作性**：在不同的技能兼容代理产品之间复用相同的技能

### 采用状态

Agent Skills 已被主流 AI 开发工具支持，包括：
- Cursor
- Claude (Claude Code, Claude.ai)
- OpenAI Codex
- GitHub Copilot
- VS Code
- 以及更多

### 开放开发

- 最初由 **Anthropic** 开发
- 作为**开放标准**发布
- 被越来越多的代理产品采用
- 开放给更广泛的生态系统贡献
- 仓库：[github.com/agentskills/agentskills](https://github.com/agentskills/agentskills)

---

## 二、什么是技能 (What are Skills)

### 核心结构

技能的核心是包含 `SKILL.md` 文件的文件夹：

```
my-skill/
├── SKILL.md          # 必需：指令 + 元数据
├── scripts/          # 可选：可执行代码
├── references/       # 可选：文档
└── assets/           # 可选：模板、资源
```

### 工作原理：渐进式披露

技能使用**渐进式披露**（Progressive Disclosure）高效管理上下文，分为三个阶段：

1. **发现 (Discovery)**
   启动时，代理仅加载每个可用技能的名称和描述，刚好足以了解何时可能相关。

2. **激活 (Activation)**
   当任务与技能描述匹配时，代理将完整的 `SKILL.md` 指令读入上下文。

3. **执行 (Execution)**
   代理遵循指令，根据需要可选地加载引用文件或执行捆绑代码。

这种方法使代理保持快速，同时按需访问更多上下文。

### SKILL.md 文件结构

每个技能都以包含 YAML frontmatter 和 Markdown 指令的 `SKILL.md` 文件开始：

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
---

# PDF Processing

## 何时使用此技能
当用户需要处理 PDF 文件时使用此技能...

## 如何提取文本
1. 使用 pdfplumber 进行文本提取...

## 如何填充表单
...
```

#### 必需的 Frontmatter 字段

- **`name`**：技能的简短标识符
- **`description`**：何时使用此技能（帮助代理确定相关性）

#### Markdown 正文

Markdown 正文包含实际指令，对结构或内容没有特定限制。

### 主要优势

1. **自文档化**：技能作者或用户可以阅读 `SKILL.md` 并理解其作用，使技能易于审计和改进。

2. **可扩展**：技能的复杂性可以从纯文本指令到包含可执行代码、资源和模板。

3. **可移植**：技能只是文件，因此易于编辑、版本控制和共享。

---

## 三、规范 (Specification)

### 目录结构

最小技能必须包含一个 `SKILL.md` 文件：

```
skill-name/
└── SKILL.md          # 必需
```

可选目录：`scripts/`、`references/`、`assets/`

### SKILL.md 格式

#### 必需的 Frontmatter

```yaml
---
name: skill-name
description: 此技能的功能描述和使用时机。
---
```

#### 完整 Frontmatter 示例

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

### 字段规范详细表

| 字段 | 必需 | 限制条件 |
|------|------|---------|
| `name` | ✅ 是 | 最多 64 字符。仅小写字母、数字和连字符。不能以连字符开头或结尾。不能有连续连字符。必须匹配父目录名。 |
| `description` | ✅ 是 | 最多 1024 字符。非空。描述技能的功能和使用时机。 |
| `license` | 否 | 许可证名称或捆绑许可证文件的引用。 |
| `compatibility` | 否 | 最多 500 字符。指示环境要求（目标产品、系统包、网络访问等）。 |
| `metadata` | 否 | 任意键值映射（用于额外元数据）。 |
| `allowed-tools` | 否 | 预批准工具的空格分隔列表。（实验性） |

### name 字段规则

#### 必需条件

- 1-64 个字符
- 仅包含小写字母、数字和连字符 (`a-z0-9-`)
- 不能以 `-` 开头或结尾
- 不能包含连续连字符 (`--`)
- 必须匹配父目录名称

#### 有效示例

```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

#### 无效示例

```yaml
name: PDF-Processing  # ❌ 不允许大写
name: -pdf            # ❌ 不能以连字符开头
name: pdf--processing # ❌ 不允许连续连字符
name: pdf_processing  # ❌ 不允许下划线
```

### description 字段规则

#### 必需条件

- 1-1024 个字符
- 应描述技能的功能和使用时机
- 应包含帮助代理识别相关任务的具体关键词

#### 好示例

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

#### 差示例

```yaml
description: Helps with PDFs.  # ❌ 太简略，缺乏关键词
```

### 其他可选字段

#### license 字段

```yaml
license: MIT
license: Apache-2.0
license: Proprietary. LICENSE.txt has complete terms
```

#### compatibility 字段

```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
```

**注意**：大多数技能无需 `compatibility` 字段。

#### metadata 字段

```yaml
metadata:
  author: example-org
  version: "1.0"
  category: document-processing
```

#### allowed-tools 字段（实验性）

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### Markdown 正文内容

正文包含技能说明，无格式限制。

**推荐章节**：
- 分步说明
- 输入/输出示例
- 常见边界情况处理

### 可选目录

#### scripts/
包含代理可运行的可执行代码。应该：
- 自包含或清楚记录依赖
- 包含有用的错误消息
- 优雅处理边界情况

支持的语言：Python、Bash、JavaScript（取决于代理实现）

#### references/
包含代理按需读取的附加文档：
- `REFERENCE.md` - 详细技术参考
- `FORMS.md` - 表单模板或结构化数据格式
- 特定领域文件（`finance.md`、`legal.md` 等）

#### assets/
包含静态资源：
- 模板（文档、配置）
- 图像（图表、示例）
- 数据文件（查找表、模式）

### 渐进式披露最佳实践

技能应结构化以高效使用上下文：

1. **元数据**（~100 tokens）
   `name` 和 `description` 在启动时为所有技能加载

2. **说明**（< 5000 tokens 推荐）
   完整 `SKILL.md` 正文在技能激活时加载

3. **资源**（按需）
   `scripts/`、`references/`、`assets/` 中的文件仅在需要时加载

**建议**：主 `SKILL.md` 保持在 **500 行以下**。将详细参考材料移至单独文件。

### 文件引用

从技能根目录使用相对路径：

```markdown
详情请参阅 [参考指南](references/REFERENCE.md)。

运行提取脚本：
scripts/extract.py
```

**建议**：文件引用保持距离 `SKILL.md` 一级深度。避免深度嵌套引用链。

### 验证工具

使用 [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) 参考库验证技能：

```bash
skills-ref validate ./my-skill
```

检查 `SKILL.md` frontmatter 有效性并验证所有命名约定。

---

## 四、集成技能 (Integrate Skills)

### 概述

本指南说明如何向 AI 代理或开发工具添加技能支持。兼容技能的代理需要：

1. **发现** 配置目录中的技能
2. **加载元数据**（名称和描述）在启动时
3. **匹配** 用户任务与相关技能
4. **激活** 技能（加载完整指令）
5. **执行** 脚本并根据需要访问资源

### 集成方法

#### 基于文件系统的代理
- 在计算机环境（bash/unix）中操作
- 代表最强大的选项
- 技能在模型发出 shell 命令时激活，如：
  ```bash
  cat /path/to/my-skill/SKILL.md
  ```
- 通过 shell 命令访问捆绑资源

#### 基于工具的代理
- 在没有专用计算机环境的情况下运行
- 实现允许模型触发技能的工具
- 可以通过工具实现访问捆绑资源
- 具体工具实现由开发者决定

### 技能发现

技能是包含 `SKILL.md` 文件的文件夹。代理应扫描配置目录以查找有效技能。

### 加载元数据

在启动时，仅解析每个 `SKILL.md` 文件的 frontmatter。这保持初始上下文使用量低。

#### 解析 Frontmatter 伪代码

```python
function parseMetadata(skillPath):
    content = readFile(skillPath + "/SKILL.md")
    frontmatter = extractYAMLFrontmatter(content)

    return {
        name: frontmatter.name,
        description: frontmatter.description,
        path: skillPath
    }
```

### 注入上下文

将技能元数据包含在系统提示中，以便模型知道哪些技能可用。

#### 对于 Claude 模型，推荐使用 XML 格式

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files, fills forms, merges documents.</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyzes datasets, generates charts, and creates summary reports.</description>
    <location>/path/to/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>
```

**关键点**：
- 对于基于文件系统的代理，包含 `location` 字段（SKILL.md 的绝对路径）
- 对于基于工具的代理，可以省略 location
- 保持元数据简洁——每个技能应向上下文添加大约 **50-100 tokens**

### 安全考虑

脚本执行会带来安全风险。考虑：

- **沙箱化**：在隔离环境中运行脚本
- **白名单**：仅执行来自可信技能的脚本
- **确认**：在运行潜在危险操作之前询问用户
- **日志记录**：记录所有脚本执行以供审计

### 参考实现

[skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) 库提供 Python 工具和 CLI，用于处理技能。

#### 验证技能目录

```bash
skills-ref validate <path>
```

#### 生成代理提示的 `<available_skills>` XML

```bash
skills-ref to-prompt <path>...
```

使用库源代码作为参考实现。

---

## 五、快速参考

### 技能创建检查清单

- [ ] 创建技能目录，名称符合规范（小写、连字符、无连续 `--`）
- [ ] 创建 `SKILL.md` 文件
- [ ] 添加 YAML frontmatter（必需：`name`、`description`）
- [ ] 确保 `name` 与目录名一致
- [ ] `description` 包含清晰的功能和使用场景说明
- [ ] 编写 Markdown 指令（保持在 500 行以内）
- [ ] 如需脚本，添加 `scripts/` 目录
- [ ] 如需详细参考，添加 `references/` 目录
- [ ] 如需资源文件，添加 `assets/` 目录
- [ ] 使用 `skills-ref validate` 验证技能

### 关键约定

| 约定 | 说明 |
|------|------|
| **命名** | 小写字母、数字、连字符，1-64 字符 |
| **描述** | 1-1024 字符，包含关键词 |
| **目录名** | 必须与 `name` 字段一致 |
| **文件引用** | 使用相对路径，保持一级深度 |
| **上下文效率** | 主文件 < 500 行，详细内容放 references/ |

### 常用命令

```bash
# 验证技能
skills-ref validate ./my-skill

# 生成提示 XML
skills-ref to-prompt ./skills-dir

# 安装到用户级
cp -r ./my-skill ~/.agent-skills/

# 安装到项目级
cp -r ./my-skill ./.agent-skills/
```

---

## 六、资源链接

- **官方网站**：https://agentskills.io/
- **GitHub 仓库**：https://github.com/agentskills/agentskills
- **参考库**：https://github.com/agentskills/agentskills/tree/main/skills-ref
- **示例技能**：https://github.com/anthropics/skills
- **最佳实践**：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

---

**文档生成日期**：2026-01-12
**来源**：https://agentskills.io/ 官方网站
