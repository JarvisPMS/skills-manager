# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 **Agent Skills 管理工具集**,包含三个独立技能用于创建、安装和列出 Agent Skills。每个技能都是一个自包含的模块,支持多种规范标准。

### 核心组件

1. **skill-creator** - 创建符合多种规范标准的新技能
2. **skill-installer** - 安装技能到不同规范标准和级别目录
3. **skill-lister** - 列出和查看不同规范标准的已安装技能

### 支持的规范标准

项目支持三种主流 Agent Skills 规范标准:

1. **AgentSkills 标准** - 开放标准,适用于所有兼容平台
   - 路径: `~/.agent-skills/`, `.agent-skills/`, `/usr/local/share/agent-skills/`

2. **Claude Code 标准** - Claude Code CLI 和 Claude.ai
   - 路径: `~/.claude/skills/`, `.claude/skills/`

3. **Codex 标准** - OpenAI Codex 和相关工具
   - 路径: `~/.codex/skills/`, `.codex/skills/`, `/etc/codex/skills`

## 常用命令

### 运行脚本

每个技能都有独立的 Python 脚本:

```bash
# 创建技能
python skill-creator/scripts/create_skill.py

# 安装技能
python skill-installer/scripts/install_skill.py

# 列出技能
python skill-lister/scripts/list_skills.py
```

### 依赖安装

所有脚本都需要 PyYAML:

```bash
pip install pyyaml
```

## 架构要点

### 多规范支持架构

项目采用统一的架构支持多种规范标准,主要差异在于:

#### 1. 路径差异

不同规范使用不同的默认路径:

| 级别 | AgentSkills | Claude Code | Codex |
|------|-------------|-------------|-------|
| 用户级 | `~/.agent-skills/` | `~/.claude/skills/` | `~/.codex/skills/` |
| 项目级 | `.agent-skills/` | `.claude/skills/` | `.codex/skills/` |
| 系统级 | `/usr/local/share/agent-skills/` | N/A | `/etc/codex/skills` |

#### 2. 字段限制差异

| 字段 | AgentSkills | Claude | Codex |
|------|-------------|--------|-------|
| name 最大长度 | 64字符 | 64字符 | 100字符 |
| description 最大长度 | 1024字符 | 1024字符 | 500字符 |
| 名称模式 | 严格 (小写+连字符) | 严格 | 宽松 |

### Agent Skills 基本规范

所有技能必须遵循以下核心结构:

**必需结构:**
```
skill-name/
└── SKILL.md          # 必需:包含 YAML frontmatter 和 Markdown 指令
```

**SKILL.md frontmatter 必需字段:**
- `name`: 技能名称 (根据规范有不同限制)
- `description`: 功能描述 (根据规范有不同限制)

**可选字段:**
- `license`: 许可证
- `metadata`: 自定义元数据(author, version, category 等)
- `compatibility`: 兼容性说明
- `allowed-tools`: 预批准工具列表

**可选目录:**
- `scripts/` - 可执行脚本
- `references/` - 参考文档
- `assets/` - 模板和资源

### 命名规范验证

skill-creator 实现了严格的名称验证 (`create_skill.py:15-36`):

- 正则表达式: `^[a-z0-9-]+$`
- 不能以连字符开头/结尾
- 不能包含连续连字符 (`--`)
- 长度 1-64 字符

无效名称会自动建议修正 (`create_skill.py:39-51`)。

### 安装级别系统

skill-installer 支持四个安装级别 (`install_skill.py:142-166`):

1. **用户级 (User)** - `~/.agent-skills/`
   - 个人使用,无需特殊权限

2. **项目级 (Project)** - `<project>/.agent-skills/`
   - 项目特定,可通过 Git 共享
   - 需要检测项目根目录

3. **工作区级 (Workspace)** - `<workspace>/.agent-skills/`
   - 多项目工作区共享

4. **系统级 (System)** - `/usr/local/share/agent-skills/` (Unix) 或 `C:\ProgramData\agent-skills\` (Windows)
   - 所有用户共享,需要管理员权限

### 路径解析策略

skill-lister 实现了多层级扫描策略:

1. 默认路径按优先级扫描
2. 支持环境变量 `AGENT_SKILLS_PATH`
3. 自动向上查找项目根目录
4. 跨平台路径处理 (Windows/macOS/Linux)

## 技能工作模式

### skill-creator 的两种模式

1. **自动模式**: 用户提供完整信息时直接生成
2. **分步引导模式**: 交互式询问各项配置

代理需要根据用户输入判断使用哪种模式。

### skill-installer 的冲突处理

安装时若目标已存在同名技能,提供选项:
- 覆盖 (Overwrite)
- 跳过 (Skip)
- 备份后覆盖 (Backup & Overwrite)
- 取消 (Cancel)

### skill-lister 的输出格式

支持多种输出格式:
- 简洁列表 (默认)
- 表格模式
- 详细信息模式
- JSON 格式 (程序化处理)

## 重要约定

### YAML Frontmatter 格式

所有 SKILL.md 文件必须以 YAML frontmatter 开始:

```markdown
---
name: skill-name
description: 描述内容
license: MIT
metadata:
  author: name
  version: "1.0.0"
---

# 技能标题

Markdown 内容...
```

### 脚本可执行性

安装技能时,scripts/ 目录下的脚本应设置执行权限:

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### 项目根目录检测

对于项目级安装,需要向上查找包含以下标记的目录:
- `.git/`
- `package.json`
- `pyproject.toml`
- `.agent-skills/`

## 跨平台考虑

### 路径分隔符
- 使用 `os.path.join()` 或 `pathlib.Path`
- 避免硬编码 `/` 或 `\`

### 用户目录
- Windows: `%USERPROFILE%` 或 `%APPDATA%`
- Unix: `~` (通过 `os.path.expanduser()`)

### 系统目录
- Windows: `C:\ProgramData\`
- macOS/Linux: `/usr/local/share/`

## 验证清单

修改任何技能文件时,确保:

1. YAML frontmatter 格式正确
2. name 字段符合命名规范
3. description 在长度限制内
4. 目录名与 name 字段一致
5. 如果包含脚本,处理好文件权限
6. 跨平台路径兼容性

## 技能间协作

这三个技能设计为配合使用:

1. **创建工作流**: skill-creator → skill-installer
   - 创建技能后立即安装到指定位置

2. **验证工作流**: skill-installer → skill-lister
   - 安装后验证技能是否正确识别

3. **参考工作流**: skill-lister → skill-creator
   - 查看现有技能作为创建新技能的参考
