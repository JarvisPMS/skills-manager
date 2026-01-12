# 技能安装路径约定

本文档详细说明了不同操作系统和安装级别的技能安装路径约定。

## 路径优先级

当代理扫描技能时，通常按以下优先级顺序：

1. **项目级** - 优先级最高（覆盖其他级别的同名技能）
2. **工作区级** - 次优先级
3. **用户级** - 第三优先级
4. **系统级** - 优先级最低

这意味着如果多个级别存在同名技能，项目级的技能会被优先使用。

## 用户级路径

### Windows

**推荐路径**：
```
%USERPROFILE%\.agent-skills\
```
实际路径示例：`C:\Users\YourName\.agent-skills\`

**备选路径**：
```
%APPDATA%\agent-skills\
```
实际路径示例：`C:\Users\YourName\AppData\Roaming\agent-skills\`

### macOS

**推荐路径**：
```
~/.agent-skills/
```
实际路径示例：`/Users/YourName/.agent-skills/`

**备选路径**：
```
~/Library/Application Support/agent-skills/
```
实际路径示例：`/Users/YourName/Library/Application Support/agent-skills/`

### Linux

**推荐路径**：
```
~/.agent-skills/
```
实际路径示例：`/home/username/.agent-skills/`

**备选路径**：
```
~/.local/share/agent-skills/
```
实际路径示例：`/home/username/.local/share/agent-skills/`

**XDG 规范路径**：
```
$XDG_DATA_HOME/agent-skills/
```
如果 `$XDG_DATA_HOME` 未设置，默认为 `~/.local/share/`

## 项目级路径

### 所有操作系统

项目级技能通常放在项目根目录下：

**推荐路径**（隐藏目录）：
```
<project-root>/.agent-skills/
```

**备选路径**（可见目录）：
```
<project-root>/skills/
<project-root>/.skills/
```

### 如何查找项目根目录

按以下顺序查找：

1. 包含 `.git` 目录的目录
2. 包含 `package.json` 的目录（Node.js 项目）
3. 包含 `pyproject.toml` 或 `setup.py` 的目录（Python 项目）
4. 包含 `Cargo.toml` 的目录（Rust 项目）
5. 包含 `pom.xml` 或 `build.gradle` 的目录（Java 项目）
6. 包含 `.agent-skills` 目录的父目录

### 示例结构

```
my-project/
├── .git/
├── .agent-skills/           # 项目级技能
│   ├── deploy-app/
│   ├── run-tests/
│   └── generate-docs/
├── src/
├── tests/
└── README.md
```

## 工作区级路径

### 所有操作系统

工作区级技能放在工作区根目录：

```
<workspace-root>/.agent-skills/
```

### 工作区场景

**单一代码库（Monorepo）**：
```
monorepo/
├── .agent-skills/           # 工作区级技能（所有包共享）
│   ├── shared-linter/
│   └── common-deploy/
├── packages/
│   ├── package-a/
│   │   └── .agent-skills/   # package-a 特定技能
│   └── package-b/
│       └── .agent-skills/   # package-b 特定技能
└── README.md
```

**VS Code 工作区**：
```
my-workspace/
├── .agent-skills/           # 工作区级技能
├── project-1/
│   └── .agent-skills/       # project-1 特定技能
└── project-2/
    └── .agent-skills/       # project-2 特定技能
```

## 系统级路径

### Windows

**推荐路径**：
```
C:\ProgramData\agent-skills\
```

**备选路径**：
```
C:\Program Files\agent-skills\
```

### macOS

**推荐路径**：
```
/usr/local/share/agent-skills/
```

**备选路径**：
```
/Library/Application Support/agent-skills/
/opt/agent-skills/
```

### Linux

**推荐路径**：
```
/usr/local/share/agent-skills/
```

**备选路径**：
```
/usr/share/agent-skills/
/opt/agent-skills/
```

## 环境变量配置

可以使用环境变量自定义技能路径：

### AGENT_SKILLS_PATH

指定额外的技能搜索路径（类似 PATH 变量）：

**Windows**：
```cmd
set AGENT_SKILLS_PATH=C:\custom\skills;D:\more\skills
```

**macOS/Linux**：
```bash
export AGENT_SKILLS_PATH=/custom/skills:/more/skills
```

### AGENT_SKILLS_USER_DIR

覆盖默认的用户级技能目录：

```bash
export AGENT_SKILLS_USER_DIR=/custom/user/skills
```

### AGENT_SKILLS_SYSTEM_DIR

覆盖默认的系统级技能目录：

```bash
export AGENT_SKILLS_SYSTEM_DIR=/custom/system/skills
```

## 路径解析函数

### Python 实现

```python
import os
from pathlib import Path
from typing import List, Optional

def get_user_skills_dir() -> Path:
    """获取用户级技能目录"""
    # 优先使用环境变量
    if 'AGENT_SKILLS_USER_DIR' in os.environ:
        return Path(os.environ['AGENT_SKILLS_USER_DIR'])

    # 默认路径
    if os.name == 'nt':  # Windows
        return Path.home() / '.agent-skills'
    else:  # macOS/Linux
        # 遵循 XDG 规范
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            return Path(xdg_data_home) / 'agent-skills'
        return Path.home() / '.agent-skills'

def get_project_skills_dir(start_path: Optional[Path] = None) -> Optional[Path]:
    """查找项目级技能目录"""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # 向上查找项目根目录
    while current != current.parent:
        # 检查项目标识文件
        if any((current / marker).exists() for marker in [
            '.git', 'package.json', 'pyproject.toml',
            'Cargo.toml', 'pom.xml', 'go.mod'
        ]):
            skills_dir = current / '.agent-skills'
            return skills_dir if skills_dir.exists() else None

        current = current.parent

    return None

def get_system_skills_dir() -> Path:
    """获取系统级技能目录"""
    # 优先使用环境变量
    if 'AGENT_SKILLS_SYSTEM_DIR' in os.environ:
        return Path(os.environ['AGENT_SKILLS_SYSTEM_DIR'])

    # 默认路径
    if os.name == 'nt':  # Windows
        return Path('C:/ProgramData/agent-skills')
    elif os.uname().sysname == 'Darwin':  # macOS
        return Path('/usr/local/share/agent-skills')
    else:  # Linux
        return Path('/usr/local/share/agent-skills')

def get_all_skills_dirs() -> List[Path]:
    """获取所有技能目录（按优先级排序）"""
    dirs = []

    # 1. 项目级（最高优先级）
    project_dir = get_project_skills_dir()
    if project_dir:
        dirs.append(project_dir)

    # 2. 用户级
    user_dir = get_user_skills_dir()
    if user_dir.exists():
        dirs.append(user_dir)

    # 3. 系统级（最低优先级）
    system_dir = get_system_skills_dir()
    if system_dir.exists():
        dirs.append(system_dir)

    # 4. 环境变量指定的额外路径
    if 'AGENT_SKILLS_PATH' in os.environ:
        extra_paths = os.environ['AGENT_SKILLS_PATH'].split(
            ';' if os.name == 'nt' else ':'
        )
        dirs.extend(Path(p) for p in extra_paths if Path(p).exists())

    return dirs
```

## 权限要求

### 用户级
- ✅ 无需特殊权限
- ✅ 普通用户可读写

### 项目级
- ✅ 需要项目目录写权限
- ✅ 通常与项目文件权限相同

### 工作区级
- ✅ 需要工作区目录写权限

### 系统级
- ⚠️ 需要管理员/root 权限
- ⚠️ 安装: Windows (管理员), macOS/Linux (sudo)
- ✅ 读取: 所有用户可读

## 最佳实践

1. **优先使用用户级**：个人工具和跨项目技能
2. **项目级用于协作**：团队共享的技能通过 Git 管理
3. **避免系统级**：除非确实需要全局共享
4. **使用版本控制**：项目级技能应该纳入版本控制
5. **文档化自定义路径**：如果使用环境变量，在项目文档中说明

## 故障排除

### 问题：找不到技能

**检查清单**：
1. 确认技能目录存在
2. 确认 SKILL.md 文件存在
3. 检查路径权限
4. 验证环境变量设置
5. 确认代理配置的扫描路径

### 问题：权限被拒绝

**解决方案**：
- 用户级：检查主目录权限
- 项目级：检查项目目录权限
- 系统级：使用管理员权限安装

### 问题：技能冲突

当多个级别存在同名技能时：
- 按优先级使用（项目 > 工作区 > 用户 > 系统）
- 使用绝对路径明确指定
- 考虑重命名低优先级的技能
