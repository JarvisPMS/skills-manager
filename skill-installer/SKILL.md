---
name: skill-installer
description: 安装 Agent Skills 到不同规范标准和级别的技能目录。支持 AgentSkills、Claude Code、Codex 三种规范。支持从本地路径或 Git 仓库安装技能。当用户想要安装、部署或添加新技能时使用。
license: MIT
metadata:
  author: tony
  version: "2.0.0"
  category: development
---

# Skill Installer - 技能安装助手

这个技能帮助您将 Agent Skills 安装到适当的位置,支持多种规范标准(AgentSkills、Claude Code、Codex)和不同级别的安装。

## 使用场景

- 用户想要安装一个新的技能
- 用户需要从 Git 仓库或本地路径部署技能
- 用户想要将技能安装到特定级别（用户级/项目级/系统级）
- 用户需要为特定平台(AgentSkills/Claude Code/Codex)安装技能

## 支持的规范标准

本技能支持三种主流 Agent Skills 规范标准,每种标准有不同的安装路径:

### 1. AgentSkills 标准
- **用户级**: `~/.agent-skills/`
- **项目级**: `<project-root>/.agent-skills/`
- **工作区级**: `<workspace-root>/.agent-skills/`
- **系统级**: `C:\ProgramData\agent-skills\` (Windows) 或 `/usr/local/share/agent-skills/` (Unix)

### 2. Claude Code 标准
- **个人级**: `~/.claude/skills/`
- **项目级**: `<project-root>/.claude/skills/`
- **企业级**: 通过托管设置管理
- **插件级**: 插件捆绑提供

### 3. Codex 标准
- **用户级**: `~/.codex/skills/` 或 `$CODEX_HOME/skills`
- **仓库级**: `<repo-root>/.codex/skills/`
- **管理员级**: `/etc/codex/skills` (Unix)
- **系统级**: Codex 内置

## 安装级别说明

### 1. 用户级（User Level）

**路径约定**：
- Windows: `%USERPROFILE%\.agent-skills\` 或 `%APPDATA%\agent-skills\`
- macOS/Linux: `~/.agent-skills/` 或 `~/.local/share/agent-skills/`

**使用场景**：
- 个人使用的技能
- 跨项目共享的个人工具
- 不希望影响其他用户的技能

**特点**：
- 仅当前用户可访问
- 不需要特殊权限
- 便于个人管理和维护

**示例**：
```
~/.agent-skills/
├── pdf-processor/
├── code-reviewer/
└── data-analyzer/
```

### 2. 项目级（Project Level）

**路径约定**：
- `<项目根目录>/.agent-skills/`
- `<项目根目录>/.skills/`
- `<项目根目录>/skills/`

**使用场景**：
- 项目特定的技能
- 团队协作的技能
- 需要版本控制的技能

**特点**：
- 与项目代码一起管理
- 可以通过 Git 共享给团队
- 不同项目可以有不同版本的同名技能

**示例**：
```
my-project/
├── .agent-skills/
│   ├── deploy-app/
│   └── run-tests/
├── src/
└── README.md
```

### 3. 工作区级（Workspace Level）

**路径约定**：
- `<工作区根目录>/.agent-skills/`
- 适用于包含多个项目的工作区

**使用场景**：
- 多项目工作区共享的技能
- 团队工作区特定的工作流程

**特点**：
- 工作区内所有项目共享
- 适合单一代码库（monorepo）场景

### 4. 系统级（System Level）

**路径约定**：
- Windows: `C:\ProgramData\agent-skills\`
- macOS/Linux: `/usr/local/share/agent-skills/` 或 `/opt/agent-skills/`

**使用场景**：
- 组织范围的标准技能
- 所有用户共享的公共技能
- 系统管理员部署的技能

**特点**：
- 所有用户可访问
- 需要管理员权限安装
- 集中管理和维护

**注意**：安装到系统级通常需要管理员权限。

## 安装工作流程

### 步骤 1: 选择规范标准

询问用户选择目标规范:
- AgentSkills 标准 (默认,开放标准)
- Claude Code 标准 (适用于 Claude)
- Codex 标准 (适用于 OpenAI Codex)

根据所选规范确定后续的安装路径。

### 步骤 2: 确定技能源

询问用户技能来源：
- **本地路径**: 已存在的技能目录
- **Git URL**: 远程 Git 仓库地址
- **技能包**: 压缩文件（.zip, .tar.gz）

**验证**：
- 本地路径：检查是否存在 SKILL.md
- Git URL：检查 URL 格式是否正确
- 压缩包：检查文件是否存在且可读

### 步骤 2: 询问安装级别

向用户展示安装级别选项：
```
请选择安装级别：
1. 用户级 (User) - 仅您使用 [推荐用于个人工具]
2. 项目级 (Project) - 当前项目使用 [推荐用于项目特定技能]
3. 工作区级 (Workspace) - 工作区内所有项目使用
4. 系统级 (System) - 所有用户使用 [需要管理员权限]

您想安装到哪个级别？
```

**默认建议**：
- 如果在项目目录中执行 → 推荐项目级
- 否则 → 推荐用户级

### 步骤 3: 确定目标路径

根据选择的级别，确定安装目标路径：

```python
def get_install_path(level: str, skill_name: str) -> str:
    if level == "user":
        # 用户级
        if os.name == 'nt':  # Windows
            base = os.path.expandvars('%USERPROFILE%\\.agent-skills')
        else:  # macOS/Linux
            base = os.path.expanduser('~/.agent-skills')

    elif level == "project":
        # 项目级 - 查找项目根目录
        base = find_project_root() + '/.agent-skills'

    elif level == "workspace":
        # 工作区级
        base = find_workspace_root() + '/.agent-skills'

    elif level == "system":
        # 系统级
        if os.name == 'nt':  # Windows
            base = 'C:\\ProgramData\\agent-skills'
        else:  # macOS/Linux
            base = '/usr/local/share/agent-skills'

    return os.path.join(base, skill_name)
```

**显示目标路径**，询问用户确认：
```
将安装到: /path/to/skills/skill-name
是否继续？(y/n)
```

### 步骤 4: 验证技能格式

在安装前，验证技能是否符合规范：

**必需验证项**：
- [ ] 存在 SKILL.md 文件
- [ ] SKILL.md 包含有效的 YAML frontmatter
- [ ] 存在必需字段：name, description
- [ ] name 字段符合命名规范
- [ ] description 字段非空且长度合适
- [ ] 目录名与 name 字段一致

**可选验证项**：
- [ ] scripts/ 目录中的脚本是否可执行
- [ ] 引用的文件路径是否存在
- [ ] 许可证文件是否存在（如果声明了）

**如果验证失败**：
- 显示详细错误信息
- 询问是否继续安装
- 建议用户修复问题

### 步骤 5: 执行安装

根据技能源类型执行相应的安装操作：

#### 从本地路径安装
```bash
# 复制整个技能目录
cp -r /source/skill-name /target/path/skill-name
```

#### 从 Git 仓库安装
```bash
# 克隆仓库
git clone <git-url> /target/path/skill-name

# 或使用子模块（项目级）
cd project-root
git submodule add <git-url> .agent-skills/skill-name
```

#### 从压缩包安装
```bash
# 解压到目标位置
unzip skill-package.zip -d /target/path/
```

**处理冲突**：
如果目标路径已存在同名技能：
```
⚠️  技能 'skill-name' 已存在
请选择操作：
1. 覆盖 (Overwrite)
2. 跳过 (Skip)
3. 备份后覆盖 (Backup & Overwrite)
4. 取消安装 (Cancel)
```

### 步骤 6: 设置权限（如果需要）

**系统级安装**：
- 可能需要 sudo 权限
- 提示用户输入密码

**脚本权限**：
- 如果包含 scripts/ 目录
- 询问是否设置执行权限

```bash
chmod +x /target/path/skill-name/scripts/*.sh
chmod +x /target/path/skill-name/scripts/*.py
```

### 步骤 7: 验证安装

安装完成后，执行验证：
1. 检查文件是否正确复制
2. 验证 SKILL.md 可读
3. 检查目录结构完整性

### 步骤 8: 报告结果

向用户报告安装结果：
```
✅ 成功安装技能: skill-name

安装位置: /path/to/skills/skill-name
安装级别: 用户级
技能描述: [从 SKILL.md 读取的描述]

下一步：
- 重启或重新加载您的代理以识别新技能
- 使用 /skill-name 或通过描述触发技能
- 查看 /path/to/skills/skill-name/SKILL.md 了解详细使用说明
```

## 高级功能

### 批量安装

支持从配置文件批量安装多个技能：

**skills.yaml 示例**：
```yaml
skills:
  - name: pdf-processor
    source: https://github.com/org/pdf-processor.git
    level: user

  - name: code-reviewer
    source: ./local/code-reviewer
    level: project

  - name: data-analyzer
    source: https://github.com/org/data-analyzer.git
    level: workspace
```

**命令**：
```bash
python scripts/batch_install.py skills.yaml
```

### 更新技能

支持更新已安装的技能：
1. 检测技能源（如果是 Git 仓库）
2. 拉取最新更改
3. 验证更新后的技能
4. 备份旧版本（可选）

### 卸载技能

支持安全卸载技能：
1. 确认要卸载的技能
2. 可选：备份技能数据
3. 删除技能目录
4. 清理相关配置

## 配置文件

### 全局配置

**路径**: `~/.agent-skills/config.yaml`

```yaml
# 默认安装级别
default_install_level: user

# 自定义安装路径
install_paths:
  user: ~/.agent-skills
  project: ./.agent-skills
  system: /usr/local/share/agent-skills

# 安装选项
options:
  verify_before_install: true
  backup_on_overwrite: true
  set_script_permissions: true

# 信任的技能源
trusted_sources:
  - https://github.com/agentskills/*
  - https://github.com/myorg/*
```

### 项目配置

**路径**: `<project>/.agent-skills/config.yaml`

```yaml
# 项目技能配置
skills:
  - pdf-processor
  - code-reviewer

# 技能源
sources:
  - type: git
    url: https://github.com/myorg/project-skills.git
```

## 安全考虑

### 验证技能源
- ⚠️ 从不受信任的源安装技能存在安全风险
- 建议只从可信来源安装技能
- 检查技能代码，特别是 scripts/ 目录

### 权限检查
- 系统级安装需要管理员权限
- 项目级安装需要项目写权限
- 验证用户有足够权限

### 脚本执行
- 不自动执行技能中的脚本
- 首次执行前询问用户确认
- 考虑在沙箱环境中运行脚本

## 故障排除

### 常见问题

**问题 1: 权限被拒绝**
```
错误: Permission denied
解决: 使用 sudo 安装系统级技能，或选择用户级安装
```

**问题 2: 技能已存在**
```
错误: Skill already exists
解决: 选择覆盖、备份或使用不同的技能名称
```

**问题 3: 无效的技能格式**
```
错误: Invalid SKILL.md format
解决: 检查 YAML frontmatter 语法，确保必需字段存在
```

**问题 4: Git 克隆失败**
```
错误: Failed to clone repository
解决: 检查 Git URL、网络连接和访问权限
```

**问题 5: 找不到项目根目录**
```
错误: Could not find project root
解决: 在项目目录中执行，或手动指定项目路径
```

## 命令行接口

### 基本用法

```bash
# 交互式安装
python scripts/install_skill.py

# 指定技能源和级别
python scripts/install_skill.py --source ./my-skill --level user

# 从 Git 安装
python scripts/install_skill.py --source https://github.com/org/skill.git --level project

# 批量安装
python scripts/install_skill.py --batch skills.yaml
```

### 选项说明

```
--source, -s      技能源（路径、Git URL 或压缩包）
--level, -l       安装级别（user/project/workspace/system）
--name, -n        技能名称（可选，默认从源自动检测）
--force, -f       强制覆盖已存在的技能
--no-verify       跳过安装前验证
--backup, -b      覆盖前备份现有技能
--batch           批量安装配置文件
```

## 集成指南

### 与 Claude Code 集成

Claude Code 会自动扫描以下位置的技能：
1. 用户级: `~/.agent-skills/`
2. 项目级: `<project>/.agent-skills/`

安装技能后，重启 Claude Code 或使用命令刷新技能列表。

### 与其他代理集成

确保您的代理配置了正确的技能扫描路径。参考 [Integrate skills](https://agentskills.io/integrate-skills) 文档。

## 参考资料

- [Agent Skills 官方文档](https://agentskills.io)
- [技能规范](https://agentskills.io/specification)
- [集成指南](https://agentskills.io/integrate-skills)
- [安装路径约定参考](references/INSTALL-PATHS.md)

## 示例

### 示例 1: 安装本地技能到用户级

```
用户: "安装技能 ./my-custom-skill"

助手步骤:
1. 检测到本地路径源
2. 验证 SKILL.md 存在
3. 询问安装级别 → 用户选择 "user"
4. 确认目标路径: ~/.agent-skills/my-custom-skill
5. 复制文件
6. 验证安装
7. 报告成功
```

### 示例 2: 从 Git 安装到项目级

```
用户: "从 https://github.com/org/pdf-tools.git 安装技能到项目"

助手步骤:
1. 检测到 Git URL 源
2. 验证 Git URL 格式
3. 询问安装级别 → 用户选择 "project"
4. 查找项目根目录
5. 确认目标路径: ./project/.agent-skills/pdf-tools
6. 克隆仓库
7. 验证技能格式
8. 报告成功
```

### 示例 3: 系统级安装（需要 sudo）

```
用户: "安装 code-standards 技能到系统级"

助手步骤:
1. 询问技能源
2. 用户选择 "system" 级别
3. 警告需要管理员权限
4. 确认目标: /usr/local/share/agent-skills/code-standards
5. 请求 sudo 权限
6. 复制文件
7. 设置适当的权限
8. 验证所有用户可访问
9. 报告成功
```
