# Codex Agent Skills 规范

> 来源: https://developers.openai.com/codex/skills 和 https://developers.openai.com/codex/skills/create-skill
>
> 本文档介绍如何在 OpenAI Codex 中创建、使用和管理 Agent Skills。

## 概述

**Agent Skills** 让你能够为 Codex 添加特定任务的能力和专业知识。Skill 将指令、资源和可选脚本打包在一起,使 Codex 能够可靠地执行特定工作流。你可以在团队或社区之间共享 skills,它们基于开放的 Agent Skills 标准构建。

### Skills 的特点

- **跨平台支持**: 在 Codex CLI 和 IDE 扩展中均可使用
- **基于开放标准**: 构建在 Agent Skills 规范之上
- **可共享**: 可以在团队和社区中共享
- **渐进式披露**: 高效管理上下文

### 什么是 Skill

Skill 通过 `SKILL.md` 文件中的 Markdown 指令来表达能力,并配有可选的脚本、资源和资产,Codex 使用这些内容来执行特定任务。

**基本结构**:
```
my-skill/
├── SKILL.md      必需: 指令 + 元数据
├── scripts/      可选: 可执行代码
├── references/   可选: 文档
└── assets/       可选: 模板、资源
```

## Skills 工作原理

### 渐进式披露机制

Skills 使用**渐进式披露**来高效管理上下文:

1. **启动时**: Codex 加载每个可用 skill 的名称和描述
2. **激活时**: 才读取完整的指令和额外参考资源

### Skill 的调用方式

#### 1. 显式调用 (Explicit Invocation)

你可以直接在提示中包含 skills:
- 运行 `/skills` 斜杠命令选择
- 输入 `$` 来提及某个 skill

> 注意: Codex Web 和 iOS 暂不支持显式调用,但仍可以提示 Codex 使用仓库中的任何 skill

#### 2. 隐式调用 (Implicit Invocation)

当用户任务与 skill 的描述匹配时,Codex 自动决定使用可用的 skill

在任一方法中,Codex 都会读取被调用 skills 的完整指令以及额外参考资料。

## Skills 的存储位置和优先级

### 加载位置

Codex 从以下位置加载 skills。Skill 的位置定义了其作用域。当 Codex 从这些位置加载可用 skills 时,它会用优先级更高的 skill 覆盖同名 skill。

**优先级从高到低**:

| Skill Scope | 位置 | 建议用途 |
| --- | --- | --- |
| **REPO** | `$CWD/.codex/skills`<br>当前工作目录:启动 Codex 的位置 | 如果在仓库或代码环境中,团队可以在此签入与工作文件夹最相关的 skills。例如,仅与微服务或代码模块相关的 skills |
| **REPO** | `$CWD/../.codex/skills`<br>当在 git 仓库中启动 Codex 时,CWD 上方的文件夹 | 如果在具有嵌套文件夹的仓库中,组织可以在此签入与共享区域最相关的 skills |
| **REPO** | `$REPO_ROOT/.codex/skills`<br>当在 git 仓库中启动 Codex 时的最顶层根文件夹 | 如果在具有嵌套文件夹的仓库中,组织可以签入与使用仓库的每个人相关的 skills。这些作为根 skills,仓库中的任何子文件夹都可以覆盖它们 |
| **USER** | `$CODEX_HOME/skills`<br>(Mac/Linux 默认: `~/.codex/skills`)<br>用户个人文件夹中的任何 skills | 用于策划与用户相关的 skills,适用于用户可能工作的任何仓库 |
| **ADMIN** | `/etc/codex/skills`<br>在共享系统位置的机器或容器中签入的任何 skills | 用于 SDK 脚本、自动化,以及签入机器上每个用户可用的默认管理员 skills |
| **SYSTEM** | Codex 捆带的 skills | 与广泛受众相关的有用 skills,例如 skill-creator 和 plan skills。每个人启动 Codex 时都可用,可以被上面任何一层覆盖 |

### 选择位置的指导原则

- **仓库级** (`.codex/skills/`): 当 skills 应该随代码库移动时
- **用户级** (`~/.codex/skills/`): 当 skills 应该适用于机器上的所有仓库时
- **管理员/系统级**: 仅在托管环境中使用(例如,在共享机器上加载 skills)

## 创建 Skills

### 方法一: 使用内置 Skill Creator

Codex 附带一个内置的 skill 来创建新 skills。这是接收指导和迭代你的 skill 的推荐方法。

**调用 skill creator**:
```
$skill-creator
```

**可选地提供上下文**:
```
$skill-creator

Create a skill that drafts a conventional commit message based on a short summary of changes.
```

Creator 会询问:
- Skill 的功能
- Codex 应何时自动触发
- 运行类型(仅指令或脚本支持)

**输出**:
- 包含名称、描述和指令的 `SKILL.md`
- 如需要,还可以生成脚本存根(Python / 容器)

### 方法二: 手动创建

当你想要完全控制或直接在编辑器中工作时使用此方法。

#### 步骤 1: 选择 skill 位置

```bash
# 用户级 skill (Mac/Linux 默认)
mkdir -p ~/.codex/skills/<skill-name>

# 仓库级 skill (签入到你的仓库)
mkdir -p .codex/skills/<skill-name>
```

#### 步骤 2: 创建 SKILL.md

```markdown
---
name: <skill-name>
description: <它做什么以及何时使用它>
---

<指令、参考或示例>
```

#### 步骤 3: 重启 Codex 加载 skill

### SKILL.md 格式要求

Skills 使用 YAML front matter 加上可选的正文。

**必需字段**:

| 字段 | 要求 | 说明 |
| --- | --- | --- |
| `name` | 非空,最多 100 字符,单行 | Skill 名称 |
| `description` | 非空,最多 500 字符,单行 | 它做什么以及何时使用它 |

**可选字段**:

```yaml
metadata:
  short-description: Optional user-facing description
```

- Codex 忽略额外的键
- 正文可以包含任何 Markdown
- 正文保留在磁盘上,除非显式调用,否则不会注入到运行时上下文中

## Skill 目录结构

除了内联指令,skill 目录通常包括:

- **脚本**(例如 Python 文件): 执行确定性处理、验证或外部工具调用
- **模板和架构**: 例如报告模板、JSON/YAML 架构或配置默认值
- **参考数据**: 例如查找表、提示或预制示例
- **文档**: 解释假设、输入或预期输出

**完整结构示例**:
```
my-skill/
├── SKILL.md       必需: 指令 + 元数据
├── scripts/       可选: 可执行代码
├── references/    可选: 文档
└── assets/        可选: 模板、资源
```

Skill 的指令引用这些资源,但它们保留在磁盘上,保持运行时上下文小而可预测。

## 使用场景

### 何时使用 Skills

- 在团队间共享行为
- 强制一致的工作流
- 一次编码最佳实践并在各处重用

**典型用例**:
- 标准化代码审查清单和约定
- 强制执行安全或合规检查
- 自动化常见分析任务
- 提供 Codex 可以自动发现的团队特定工具

### 何时避免使用 Skills

- 一次性提示或探索性任务
- 保持技能聚焦,而不是试图建模大型多步系统

### Skill 类型

**仅指令型 (Instruction-only)**: 默认推荐,使用 Markdown 指令
**脚本支持型 (Script-backed)**: 当需要确定性或外部数据时使用脚本

## 示例

### 示例 1: 草拟提交消息

```markdown
---
name: draft-commit-message
description: Draft a conventional commit message when the user asks for help writing a commit message.
metadata:
  short-description: Draft an informative commit message.
---

Draft a conventional commit message that matches the change summary provided by the user.

Requirements:
- Use the Conventional Commits format: `type(scope): summary`
- Use the imperative mood in the summary (for example, "Add", "Fix", "Refactor")
- Keep the summary under 72 characters
- If there are breaking changes, include a `BREAKING CHANGE:` footer
```

**触发此技能的示例提示**:
```
Help me write a commit message for these changes:
I renamed `SkillCreator` to `SkillsCreator` and updated the sidebar.
```

## 内置 Skills

### Skill Creator

使用内置的 `$skill-creator` skill 在 Codex 中创建新技能。描述你想要 skill 做什么,Codex 将开始引导你的 skill。如果将其与 `$create-plan` skill 结合使用(实验性;先用 `$skill-installer create-plan` 安装),Codex 将首先为你的 skill 创建一个计划。

### Skill Installer

要扩展内置 skills 列表,可以使用 `$skill-installer` skill 从 GitHub 上的精选 skills 集中下载 skills:

```bash
$skill-installer linear
```

你也可以提示安装程序从其他仓库下载 skills。

### Plan a New Feature

`$create-plan` 是一个实验性 skill,可以用 `$skill-installer` 安装,让 Codex 研究并创建构建新功能或解决复杂问题的计划:

```bash
$skill-installer create-plan
```

### Access Linear Context

```bash
$skill-installer linear
```

### Access Notion Context

```bash
$skill-installer notion-spec-to-implementation
```

## 最佳实践

1. **明确触发器**: `description` 决定了 skill 何时被自动触发
2. **保持 skill 小巧**: 优先使用窄的、模块化的 skills 而不是大的
3. **优先使用指令而非脚本**: 仅在需要确定性或外部数据时使用脚本
4. **假设无上下文**: 编写指令时假设 Codex 除了输入外什么都不知道
5. **避免歧义**: 使用命令式的、分步的语言
6. **测试触发**: 验证示例提示按预期激活 skill

## 故障排除

### Skill 未出现

如果 skill 在 Codex 中没有显示:

1. **确保 skills 已启用**,并且在启用后重启了 Codex
2. **检查文件名**: 必须精确命名为 `SKILL.md`
3. **检查路径**: 必须在受支持的路径下,例如 `~/.codex/skills`
4. **检查符号链接**: Codex 忽略符号链接目录
5. **检查 YAML**: 无效的 YAML 或超过长度限制的 `name`/`description` 字段会导致跳过 skill

### Skill 未触发

如果 skill 加载但没有自动运行:

1. **最常见的问题是触发器不清晰**: 确保 `description` 明确说明了何时应使用该 skill
2. **测试匹配**: 使用与描述紧密匹配的提示进行测试
3. **处理重叠**: 如果多个 skills 在意图上重叠,缩小描述范围以便 Codex 选择正确的

### 启动验证错误

如果 Codex 在启动时报告验证错误:

1. **修复 `SKILL.md` 中列出的问题**: 最常见的是多行或超长的 `name` 或 `description` 字段
2. **重启 Codex** 以重新加载 skills

## Agent Skills 规范

Codex skills 基于 Agent Skills 规范构建。查看文档以了解更多信息。

**参考资源**:
- 实际模式和示例: [agentskills.io](https://agentskills.io)
- Skills 目录: [github.com/openai/skills](https://github.com/openai/skills)

## 与 Claude Skills 的对比

| 特性 | Codex Skills | Claude Skills |
| --- | --- | --- |
| **优先级顺序** | REPO > USER > ADMIN > SYSTEM | Enterprise > Personal > Project > Plugin |
| **描述长度限制** | 最多 500 字符 | 最多 1024 字符 |
| **名称长度限制** | 最多 100 字符 | 最多 64 字符 |
| **用户目录** | `~/.codex/skills/` | `~/.claude/skills/` |
| **项目目录** | `.codex/skills/` | `.claude/skills/` |
| **系统目录** | `/etc/codex/skills` | `/usr/local/share/agent-skills/` (Unix) |
| **显式调用** | `/skills` 或 `$skill-name` | `/skill-name` |
| **规范来源** | agentskills.io | agentskills.io |

两者都基于相同的 Agent Skills 开放标准,但在实现细节上有所不同。
