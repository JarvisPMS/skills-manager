---
name: skill-creator
description: 帮助用户创建符合多种规范标准的新技能。支持 AgentSkills、Claude Code、Codex 三种规范。支持自动模式（快速生成）和分步引导模式（交互式创建）。当用户想要创建、生成或制作新的 Agent Skill 时使用此技能。
license: MIT
metadata:
  author: tony
  version: "2.0.0"
  category: development
---

# Skill Creator - 技能创建助手

这个技能帮助您创建符合多种规范标准(AgentSkills、Claude Code、Codex)的新技能。

## 使用场景

- 用户想要创建一个新的 Agent Skill
- 用户需要生成技能模板
- 用户想要将现有的工作流程转换为技能
- 用户需要为特定平台(AgentSkills/Claude Code/Codex)创建技能

## 支持的规范标准

本技能支持三种主流 Agent Skills 规范标准,每种标准有其特定的路径约定和字段限制:

### 1. AgentSkills 标准 (默认)

**适用平台**: 开放标准,适用于所有兼容 AgentSkills 规范的平台

**技能保存路径**:
- **用户级**: `~/.agent-skills/`
- **项目级**: `<project-root>/.agent-skills/`
- **工作区级**: `<workspace-root>/.agent-skills/`
- **系统级**:
  - Windows: `C:\ProgramData\agent-skills\`
  - Unix/Linux: `/usr/local/share/agent-skills/`

**字段限制**:
- `name`: 1-64字符,仅小写字母、数字和连字符
- `description`: 1-1024字符

**参考文档**: `doc/AgentSkills.md`

### 2. Claude Code 标准

**适用平台**: Claude Code CLI 和 Claude.ai

**技能保存路径**:
- **个人级**: `~/.claude/skills/`
- **项目级**: `<project-root>/.claude/skills/`
- **企业级**: 通过托管设置管理
- **插件级**: 插件捆绑提供

**字段限制**:
- `name`: 1-64字符,仅小写字母、数字和连字符
- `description`: 1-1024字符
- 支持额外字段: `allowed-tools`, `model`, `context`, `agent`, `hooks`, `user-invocable`

**参考文档**: `doc/ClaudeSkills.md`

### 3. Codex 标准

**适用平台**: OpenAI Codex 和相关工具

**技能保存路径** (按优先级):
- **仓库级**:
  - `$CWD/.codex/skills/` (当前工作目录)
  - `$CWD/../.codex/skills/` (父目录)
  - `$REPO_ROOT/.codex/skills/` (仓库根目录)
- **用户级**: `~/.codex/skills/` 或 `$CODEX_HOME/skills`
- **管理员级**: `/etc/codex/skills`
- **系统级**: Codex 内置

**字段限制**:
- `name`: 最多100字符,非空
- `description`: 最多500字符,非空
- 简化的 metadata 结构

**参考文档**: `doc/CodexSkills.md`

## 两种创建模式

### 1. 自动模式（Auto Mode）

**触发条件**：用户直接描述了技能的完整需求，包括名称、功能描述等核心信息。

**工作流程**：
1. 从用户描述中提取技能信息
2. 验证技能名称是否符合规范（1-64字符，仅小写字母、数字和连字符）
3. 自动生成完整的目录结构
4. 创建 SKILL.md 文件，包含：
   - 符合规范的 YAML frontmatter
   - 清晰的 Markdown 指令内容
5. 根据需要创建 scripts/、references/、assets/ 目录
6. 生成示例脚本或参考文档（如果需要）
7. 验证生成的技能结构
8. 向用户报告创建结果

**示例**：
```
用户: "帮我创建一个名为 pdf-processor 的技能，用于处理 PDF 文件的提取和合并"
助手: [自动生成完整的技能结构]
```

### 2. 分步引导模式（Guided Mode）

**触发条件**：
- 用户请求"引导我创建技能"
- 用户信息不完整，需要更多输入
- 用户明确想要交互式创建过程

**工作流程**：

**步骤 1: 选择规范标准**
- 询问用户选择目标规范:
  1. AgentSkills 标准 (默认,开放标准)
  2. Claude Code 标准 (适用于 Claude)
  3. Codex 标准 (适用于 OpenAI Codex)
- 显示所选规范的字段限制和路径约定
- 根据所选规范调整后续验证规则

**步骤 2: 收集基本信息**
- 询问技能名称（提示所选规范的要求）
- 根据所选规范验证名称格式：
  - **AgentSkills/Claude**: 1-64字符,仅小写字母、数字和连字符,不能以连字符开头或结尾,不能包含连续连字符
  - **Codex**: 最多100字符,非空,单行
- 如果不符合规范，提供修正建议

**步骤 3: 技能描述**
- 询问技能的功能描述
- 提示应包含：
  - 技能的作用（做什么）
  - 使用场景（何时使用）
  - 关键词（帮助代理识别）
- 根据所选规范验证描述长度：
  - **AgentSkills/Claude**: 1-1024字符
  - **Codex**: 最多500字符

**步骤 4: 可选信息**
询问是否需要添加：
- 许可证信息（license）
- 兼容性要求（compatibility）
- 自定义元数据（metadata）
- 预批准工具列表（allowed-tools, Claude 标准专用）
- 其他 Claude 专用字段（model, context, agent, hooks 等）

**步骤 5: 附加资源**
询问是否需要：
- 脚本文件（scripts/）- 询问脚本语言和功能
- 参考文档（references/）- 询问需要哪些参考材料
- 资源文件（assets/）- 询问需要哪些模板或数据

**步骤 6: 生成结构**
- 创建技能目录（根据所选规范确定路径）
- 生成 SKILL.md 文件（根据所选规范调整字段）
- 创建所需的子目录
- 生成示例文件（如果用户选择）

**步骤 7: 验证和确认**
- 显示生成的目录结构
- 显示 SKILL.md 内容摘要
- 询问是否需要修改
- 确认完成

## 技能规范验证清单

创建技能时，必须验证以下规范：

### 名称验证（name）
- [ ] 长度在 1-64 字符之间
- [ ] 仅包含小写字母、数字和连字符
- [ ] 不以连字符开头或结尾
- [ ] 不包含连续连字符（--）
- [ ] 目录名与技能名称一致

### 描述验证（description）
- [ ] 长度在 1-1024 字符之间
- [ ] 非空
- [ ] 包含功能说明
- [ ] 包含使用场景
- [ ] 包含相关关键词

### 文件结构验证
- [ ] 存在 SKILL.md 文件
- [ ] YAML frontmatter 格式正确
- [ ] 必需字段存在（name, description）
- [ ] Markdown 内容清晰完整

### 可选字段验证
- [ ] license: 简短的许可证名称或文件引用
- [ ] compatibility: 如果提供，长度 ≤ 500 字符
- [ ] metadata: 键值对格式正确
- [ ] allowed-tools: 空格分隔的工具列表

## SKILL.md 模板

```markdown
---
name: {{skill-name}}
description: {{description}}
{{#if license}}
license: {{license}}
{{/if}}
{{#if compatibility}}
compatibility: {{compatibility}}
{{/if}}
{{#if metadata}}
metadata:
{{#each metadata}}
  {{@key}}: {{this}}
{{/each}}
{{/if}}
{{#if allowed-tools}}
allowed-tools: {{allowed-tools}}
{{/if}}
---

# {{Skill Title}}

## 使用场景

描述何时使用此技能...

## 功能说明

### 主要功能 1

详细说明...

### 主要功能 2

详细说明...

## 使用步骤

1. 步骤 1
2. 步骤 2
3. 步骤 3

## 示例

提供使用示例...

## 注意事项

列出重要的注意事项...

## 参考资料

{{#if references}}
- [参考文档](references/REFERENCE.md)
{{/if}}
```

## 目录结构模板

```
{{skill-name}}/
├── SKILL.md                    # 必需
{{#if scripts}}
├── scripts/                    # 可选
│   ├── {{script-name}}.py
│   └── README.md
{{/if}}
{{#if references}}
├── references/                 # 可选
│   ├── REFERENCE.md
│   └── {{additional-docs}}.md
{{/if}}
{{#if assets}}
└── assets/                     # 可选
    ├── templates/
    └── data/
{{/if}}
```

## 最佳实践

1. **保持简洁**：SKILL.md 建议少于 500 行，详细内容放在 references/
2. **渐进式披露**：将详细参考资料拆分为单独的文件
3. **清晰的指令**：使用步骤编号、示例和边界情况说明
4. **自包含脚本**：脚本应处理错误并提供清晰的错误消息
5. **版本控制**：在 metadata 中记录版本号

## 错误处理

### 常见错误及解决方案

**错误 1: 技能名称不符合规范**
- 检查是否包含大写字母
- 检查是否有非法字符
- 检查连字符位置

**错误 2: 描述过长或过短**
- 确保描述在 1-1024 字符之间
- 描述应包含足够的上下文信息

**错误 3: YAML frontmatter 格式错误**
- 检查缩进是否正确
- 检查冒号后是否有空格
- 检查引号是否匹配

## 验证技能

创建完成后，使用以下方法验证：

1. **手动检查**：
   - 阅读 SKILL.md 是否清晰
   - 检查所有文件路径是否正确
   - 确认示例是否有效

2. **使用 skills-ref 工具**（如果可用）：
   ```bash
   skills-ref validate ./{{skill-name}}
   ```

3. **测试执行**：
   - 尝试在代理中加载技能
   - 执行示例场景
   - 验证脚本是否可运行

## 后续步骤

创建技能后，您可以：
1. 使用 skill-installer 技能安装到指定位置
2. 手动测试技能功能
3. 根据使用情况迭代改进
4. 分享给团队或社区

## 参考资料

- [Agent Skills 官方文档](https://agentskills.io)
- [规范文档](https://agentskills.io/specification)
- [示例技能](https://github.com/agentskills/agentskills)
