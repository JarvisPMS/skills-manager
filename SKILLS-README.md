# Agent Skills 工具集

本目录包含三个用于管理 Agent Skills 的技能：

1. **skill-creator** - 创建新技能
2. **skill-installer** - 安装技能到不同级别
3. **skill-lister** - 列出和查看已安装的技能

## 快速开始

### 安装这些技能

首先，您需要将这两个技能安装到您的代理中。推荐安装到用户级：

```bash
# 创建用户级技能目录
mkdir -p ~/.agent-skills

# 复制技能
cp -r skill-creator ~/.agent-skills/
cp -r skill-installer ~/.agent-skills/
cp -r skill-lister ~/.agent-skills/
```

重启您的代理以识别新技能。

## 技能 1: skill-creator

创建符合 Agent Skills 规范的新技能。

### 使用方式

#### 方式 1: 通过代理自动模式

直接告诉代理您想创建的技能：

```
"帮我创建一个名为 markdown-formatter 的技能，用于格式化 Markdown 文档"
```

代理会自动：
- 验证技能名称
- 生成 SKILL.md 文件
- 创建目录结构
- 添加必要的模板

#### 方式 2: 通过代理分步引导模式

请求交互式创建：

```
"引导我创建一个新技能"
```

代理会逐步询问：
- 技能名称
- 功能描述
- 可选信息（许可证、元数据等）
- 是否需要脚本、参考文档或资源文件

#### 方式 3: 直接运行脚本

使用提供的 Python 脚本：

```bash
cd skill-creator/scripts
python3 create_skill.py
```

按照交互式提示创建技能。

### 功能特点

- ✅ 自动验证技能名称格式
- ✅ 提供名称修正建议
- ✅ 生成符合规范的 SKILL.md
- ✅ 创建可选的目录结构（scripts/、references/、assets/）
- ✅ 包含详细的使用说明和最佳实践

### 参考文档

- `skill-creator/SKILL.md` - 完整的技能说明
- `skill-creator/references/NAME-VALIDATION.md` - 名称验证规则详解

## 技能 2: skill-installer

安装 Agent Skills 到不同级别的目录。

### 使用方式

#### 方式 1: 通过代理安装

告诉代理您想安装的技能：

```
"安装技能 ./my-custom-skill 到用户级"
```

或从 Git 安装：

```
"从 https://github.com/org/pdf-tools.git 安装技能到项目级"
```

代理会：
- 询问安装级别（如果未指定）
- 验证技能格式
- 检查权限
- 处理冲突
- 执行安装

#### 方式 2: 直接运行脚本

使用提供的 Python 脚本：

```bash
cd skill-installer/scripts
python3 install_skill.py
```

按照交互式提示完成安装。

### 安装级别

#### 1. 用户级（User）
- **路径**: `~/.agent-skills/`
- **用途**: 个人使用的技能
- **权限**: 无需特殊权限

#### 2. 项目级（Project）
- **路径**: `<project>/.agent-skills/`
- **用途**: 项目特定的技能，可通过 Git 共享
- **权限**: 项目写权限

#### 3. 工作区级（Workspace）
- **路径**: `<workspace>/.agent-skills/`
- **用途**: 多项目工作区共享
- **权限**: 工作区写权限

#### 4. 系统级（System）
- **路径**: `/usr/local/share/agent-skills/` (macOS/Linux)
- **路径**: `C:\ProgramData\agent-skills\` (Windows)
- **用途**: 所有用户共享
- **权限**: 需要管理员/sudo 权限

### 功能特点

- ✅ 支持本地路径和 Git 仓库
- ✅ 自动验证技能格式
- ✅ 智能级别推荐（项目内推荐项目级）
- ✅ 权限检查和提示
- ✅ 冲突处理（覆盖/跳过/备份）
- ✅ 自动设置脚本执行权限

### 参考文档

- `skill-installer/SKILL.md` - 完整的技能说明
- `skill-installer/references/INSTALL-PATHS.md` - 安装路径详解

## 技能 3: skill-lister

列出和查看已安装的 Agent Skills。

### 使用方式

#### 方式 1: 通过代理列出所有技能

最简单的用法：

```
"列出所有已安装的技能"
```

代理会自动扫描所有默认路径并显示技能列表。

#### 方式 2: 列出特定级别的技能

```
"列出用户级的技能"
"列出项目级的技能"
```

#### 方式 3: 搜索特定功能的技能

```
"搜索关于 PDF 的技能"
"查找数据分析相关的技能"
```

#### 方式 4: 查看技能详细信息

```
"显示 pdf-processor 技能的详细信息"
```

#### 方式 5: 直接运行脚本

```bash
cd skill-lister/scripts
python3 list_skills.py

# 搜索技能
python3 list_skills.py --search pdf

# 显示详细信息
python3 list_skills.py --detail skill-name
```

### 功能特点

- ✅ 自动扫描所有默认技能目录
- ✅ 支持扫描自定义路径
- ✅ 显示技能元数据（名称、描述、版本等）
- ✅ 按级别分组显示
- ✅ 支持关键词搜索和过滤
- ✅ 检测技能格式问题

### 输出示例

```
📚 已安装的技能 (共 3 个)

【用户级】 (~/.agent-skills/)
  1. pdf-processor
     描述: 处理 PDF 文件的提取、合并和转换
     版本: 1.2.0

  2. code-reviewer
     描述: 自动代码审查和质量检查工具
     版本: 2.0.1

【项目级】 (./my-project/.agent-skills/)
  3. deploy-app
     描述: 项目部署自动化脚本
     版本: 1.0.0
```

### 参考文档

- `skill-lister/SKILL.md` - 完整的技能说明
- `skill-lister/references/SCANNING-STRATEGY.md` - 扫描策略详解

## 完整工作流程示例

### 示例 1: 创建并安装个人技能

```bash
# 步骤 1: 创建技能
# 告诉代理："创建一个名为 note-taker 的技能，用于记录和组织笔记"

# 步骤 2: 安装到用户级
# 告诉代理："安装技能 ./note-taker 到用户级"

# 步骤 3: 使用技能
# 重启代理，然后使用新技能
```

### 示例 2: 创建团队共享的项目技能

```bash
# 在项目目录中

# 步骤 1: 创建技能
cd my-project
# 告诉代理："引导我创建一个技能"
# 按提示创建 deploy-app 技能

# 步骤 2: 安装到项目级
# 告诉代理："安装技能 ./deploy-app 到项目级"

# 步骤 3: 提交到版本控制
git add .agent-skills/deploy-app/
git commit -m "Add deployment skill"
git push

# 团队成员拉取后即可使用
```

### 示例 3: 从 GitHub 安装开源技能

```bash
# 告诉代理：
"从 https://github.com/agentskills/pdf-processor.git 安装技能"

# 代理会询问安装级别，选择 "user" 即可
```

## Agent Skills 规范摘要

### 必需结构

```
skill-name/
└── SKILL.md          # 必需
```

### SKILL.md 格式

```markdown
---
name: skill-name                    # 必需：1-64字符，小写字母+数字+连字符
description: 描述技能功能和使用场景    # 必需：1-1024字符
license: MIT                        # 可选
metadata:                           # 可选
  author: your-name
  version: "1.0"
---

# 技能标题

技能说明...
```

### 可选目录

- `scripts/` - 可执行脚本
- `references/` - 参考文档
- `assets/` - 模板和资源

### 命名规则

✅ **有效示例**:
- `pdf-processor`
- `code-reviewer`
- `data-analyzer-v2`

❌ **无效示例**:
- `PDF-Processor` (包含大写)
- `pdf_processor` (包含下划线)
- `-pdf` (以连字符开头)
- `pdf--processor` (连续连字符)

## 故障排除

### 问题：代理识别不到新技能

**解决**：
1. 确认技能已安装到正确的目录
2. 重启代理
3. 检查 SKILL.md 格式是否正确

### 问题：技能名称验证失败

**解决**：
1. 使用 skill-creator 自动生成（会自动修正）
2. 检查名称是否符合规范（小写、数字、连字符）
3. 使用脚本的建议功能

### 问题：安装权限被拒绝

**解决**：
- 用户级：检查主目录权限
- 项目级：确认在项目目录中执行
- 系统级：使用 `sudo` (Linux/macOS) 或管理员权限 (Windows)

### 问题：Git 克隆失败

**解决**：
1. 检查 Git 是否已安装：`git --version`
2. 验证 Git URL 是否正确
3. 检查网络连接
4. 确认有访问权限（私有仓库）

## 依赖要求

### skill-creator
- Python 3.6+
- PyYAML (用于解析 YAML)

### skill-installer
- Python 3.6+
- PyYAML
- Git (用于从 Git 安装)

### skill-lister
- Python 3.6+
- PyYAML (用于解析 YAML)

### 安装依赖

```bash
pip install pyyaml
```

## 进一步学习

### 官方资源

- [Agent Skills 官方网站](https://agentskills.io)
- [规范文档](https://agentskills.io/specification)
- [集成指南](https://agentskills.io/integrate-skills)
- [示例技能](https://github.com/agentskills/agentskills)

### 社区资源

- [GitHub 组织](https://github.com/agentskills)
- 社区贡献的技能库

## 贡献

如果您创建了有用的技能，考虑：
- 在 GitHub 上开源分享
- 提交到 Agent Skills 社区
- 在团队内部分享

## 许可证

这三个技能采用 MIT 许可证。

---

**创建者**: Tony
**版本**: 1.0.0
**最后更新**: 2026-01-12
