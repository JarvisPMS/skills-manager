#!/usr/bin/env python3
"""
Skill Installer Script

这个脚本帮助将 Agent Skills 安装到不同规范标准和级别的目录。
支持 AgentSkills、Claude Code、Codex 三种规范。
"""

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import yaml


class SkillStandard(Enum):
    """技能规范标准"""
    AGENTSKILLS = "agentskills"
    CLAUDE = "claude"
    CODEX = "codex"


# 规范配置
STANDARD_CONFIG = {
    SkillStandard.AGENTSKILLS: {
        "name": "AgentSkills",
        "display_name": "AgentSkills 标准",
        "user_dir": ".agent-skills",
        "project_dir": ".agent-skills",
        "system_windows": "C:/ProgramData/agent-skills",
        "system_unix": "/usr/local/share/agent-skills"
    },
    SkillStandard.CLAUDE: {
        "name": "Claude",
        "display_name": "Claude Code 标准",
        "user_dir": ".claude/skills",
        "project_dir": ".claude/skills",
        "system_windows": None,
        "system_unix": None
    },
    SkillStandard.CODEX: {
        "name": "Codex",
        "display_name": "OpenAI Codex 标准",
        "user_dir": ".codex/skills",
        "project_dir": ".codex/skills",
        "system_windows": None,
        "system_unix": "/etc/codex/skills"
    }
}


class SkillInstaller:
    """技能安装器"""

    INSTALL_LEVELS = ['user', 'project', 'workspace', 'system']

    def __init__(self, standard: SkillStandard = SkillStandard.AGENTSKILLS):
        self.standard = standard
        self.standard_config = STANDARD_CONFIG[standard]
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path.home() / '.agent-skills' / 'config.yaml'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {
            'default_install_level': 'user',
            'options': {
                'verify_before_install': True,
                'backup_on_overwrite': True,
                'set_script_permissions': True
            }
        }

    def get_user_skills_dir(self) -> Path:
        """获取用户级技能目录(根据规范)"""
        # 检查环境变量覆盖
        env_var_map = {
            SkillStandard.AGENTSKILLS: 'AGENT_SKILLS_USER_DIR',
            SkillStandard.CLAUDE: 'CLAUDE_SKILLS_DIR',
            SkillStandard.CODEX: 'CODEX_HOME'
        }

        env_var = env_var_map.get(self.standard)
        if env_var and env_var in os.environ:
            base_path = Path(os.environ[env_var])
            if self.standard == SkillStandard.CODEX:
                return base_path / 'skills'
            return base_path

        # 使用规范默认路径
        user_dir = self.standard_config["user_dir"]
        return Path.home() / user_dir

    def find_project_root(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """查找项目根目录"""
        if start_path is None:
            start_path = Path.cwd()

        current = start_path.resolve()
        project_markers = [
            '.git', 'package.json', 'pyproject.toml',
            'Cargo.toml', 'pom.xml', 'go.mod', 'setup.py'
        ]

        while current != current.parent:
            if any((current / marker).exists() for marker in project_markers):
                return current
            current = current.parent

        return None

    def get_project_skills_dir(self) -> Optional[Path]:
        """获取项目级技能目录(根据规范)"""
        project_root = self.find_project_root()
        if project_root:
            project_dir = self.standard_config["project_dir"]
            return project_root / project_dir
        return None

    def get_system_skills_dir(self) -> Path:
        """获取系统级技能目录(根据规范)"""
        if 'AGENT_SKILLS_SYSTEM_DIR' in os.environ:
            return Path(os.environ['AGENT_SKILLS_SYSTEM_DIR'])

        if os.name == 'nt':  # Windows
            system_path = self.standard_config["system_windows"]
            if system_path:
                return Path(system_path)
            raise ValueError(f"{self.standard_config['display_name']} 不支持 Windows 系统级安装")
        else:  # macOS/Linux
            system_path = self.standard_config["system_unix"]
            if system_path:
                return Path(system_path)
            raise ValueError(f"{self.standard_config['display_name']} 不支持 Unix 系统级安装")

    def get_install_path(self, level: str, skill_name: str) -> Path:
        """根据级别获取安装路径"""
        if level == 'user':
            base = self.get_user_skills_dir()
        elif level == 'project':
            base = self.get_project_skills_dir()
            if base is None:
                raise ValueError("找不到项目根目录")
        elif level == 'workspace':
            # 简化：与项目级相同，实际应用中可能需要更复杂的逻辑
            base = self.get_project_skills_dir()
            if base is None:
                raise ValueError("找不到工作区根目录")
        elif level == 'system':
            base = self.get_system_skills_dir()
        else:
            raise ValueError(f"无效的安装级别: {level}")

        return base / skill_name

    def validate_skill(self, skill_path: Path) -> Tuple[bool, str]:
        """验证技能格式"""
        skill_md = skill_path / 'SKILL.md'
        if not skill_md.exists():
            return False, "找不到 SKILL.md 文件"

        try:
            content = skill_md.read_text(encoding='utf-8')

            # 检查 YAML frontmatter
            if not content.startswith('---'):
                return False, "SKILL.md 必须以 YAML frontmatter 开头"

            # 提取 frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return False, "YAML frontmatter 格式错误"

            frontmatter = yaml.safe_load(parts[1])

            # 验证必需字段
            if 'name' not in frontmatter:
                return False, "缺少必需字段: name"
            if 'description' not in frontmatter:
                return False, "缺少必需字段: description"

            # 验证 name 格式
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9-]+$', name):
                return False, f"技能名称格式错误: {name}"
            if name.startswith('-') or name.endswith('-'):
                return False, f"技能名称不能以连字符开头或结尾: {name}"
            if '--' in name:
                return False, f"技能名称不能包含连续连字符: {name}"

            # 验证目录名与 name 一致
            if skill_path.name != name:
                return False, f"目录名 ({skill_path.name}) 与技能名称 ({name}) 不一致"

            # 验证 description
            description = frontmatter['description']
            if not description or len(description) > 1024:
                return False, "描述必须在 1-1024 字符之间"

            return True, "验证通过"

        except Exception as e:
            return False, f"验证时出错: {str(e)}"

    def install_from_local(
        self,
        source_path: Path,
        target_path: Path,
        backup: bool = False
    ) -> Tuple[bool, str]:
        """从本地路径安装技能"""
        try:
            # 检查源路径
            if not source_path.exists():
                return False, f"源路径不存在: {source_path}"

            # 验证技能
            valid, msg = self.validate_skill(source_path)
            if not valid:
                return False, f"技能验证失败: {msg}"

            # 处理已存在的目标
            if target_path.exists():
                if backup:
                    backup_path = target_path.parent / f"{target_path.name}.backup"
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.move(str(target_path), str(backup_path))
                    print(f"已备份到: {backup_path}")
                else:
                    shutil.rmtree(target_path)

            # 创建父目录
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制技能
            shutil.copytree(source_path, target_path)

            # 设置脚本权限（Unix-like 系统）
            if os.name != 'nt':
                scripts_dir = target_path / 'scripts'
                if scripts_dir.exists():
                    for script in scripts_dir.glob('*'):
                        if script.is_file() and script.suffix in ['.sh', '.py']:
                            script.chmod(0o755)

            return True, f"成功安装到: {target_path}"

        except Exception as e:
            return False, f"安装失败: {str(e)}"

    def install_from_git(
        self,
        git_url: str,
        target_path: Path,
        backup: bool = False
    ) -> Tuple[bool, str]:
        """从 Git 仓库安装技能"""
        try:
            # 检查 git 是否可用
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return False, "Git 未安装或不可用"

            # 处理已存在的目标
            if target_path.exists():
                if backup:
                    backup_path = target_path.parent / f"{target_path.name}.backup"
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.move(str(target_path), str(backup_path))
                    print(f"已备份到: {backup_path}")
                else:
                    shutil.rmtree(target_path)

            # 创建父目录
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 克隆仓库
            result = subprocess.run(
                ['git', 'clone', git_url, str(target_path)],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return False, f"Git 克隆失败: {result.stderr}"

            # 验证技能
            valid, msg = self.validate_skill(target_path)
            if not valid:
                shutil.rmtree(target_path)
                return False, f"技能验证失败: {msg}"

            # 设置脚本权限（Unix-like 系统）
            if os.name != 'nt':
                scripts_dir = target_path / 'scripts'
                if scripts_dir.exists():
                    for script in scripts_dir.glob('*'):
                        if script.is_file() and script.suffix in ['.sh', '.py']:
                            script.chmod(0o755)

            return True, f"成功从 Git 安装到: {target_path}"

        except Exception as e:
            return False, f"安装失败: {str(e)}"

    def check_permissions(self, path: Path, level: str) -> Tuple[bool, str]:
        """检查是否有足够的权限"""
        if level == 'system' and os.name != 'nt':
            # Unix-like 系统检查是否为 root
            if os.geteuid() != 0:
                return False, "系统级安装需要 sudo 权限"

        # 检查写权限
        parent = path.parent
        if parent.exists():
            if not os.access(parent, os.W_OK):
                return False, f"没有写权限: {parent}"
        else:
            # 递归检查父目录
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            if not os.access(parent, os.W_OK):
                return False, f"没有写权限: {parent}"

        return True, "权限检查通过"


def interactive_install():
    """交互式安装"""
    print("=== Agent Skill Installer ===\n")

    # 步骤 1: 选择规范标准
    print("步骤 1: 选择规范标准")
    print("1. AgentSkills 标准 (默认,开放标准)")
    print("2. Claude Code 标准 (适用于 Claude)")
    print("3. Codex 标准 (适用于 OpenAI Codex)")
    print()

    standard_choice = input("请选择规范标准 (1-3, 默认 1): ").strip()
    if not standard_choice:
        standard_choice = "1"

    standard_map = {
        "1": SkillStandard.AGENTSKILLS,
        "2": SkillStandard.CLAUDE,
        "3": SkillStandard.CODEX
    }

    if standard_choice not in standard_map:
        print("❌ 无效的选择，使用默认值: AgentSkills")
        standard = SkillStandard.AGENTSKILLS
    else:
        standard = standard_map[standard_choice]

    installer = SkillInstaller(standard=standard)
    config = STANDARD_CONFIG[standard]
    print(f"\n✓ 已选择: {config['display_name']}\n")

    # 步骤 2: 获取技能源
    print("步骤 2: 技能源")
    print("1. 本地路径")
    print("2. Git 仓库 URL")
    source_type = input("请选择技能源类型 (1/2): ").strip()

    if source_type == '1':
        source_path = input("本地路径: ").strip()
        source_path = Path(source_path).expanduser().resolve()
        if not source_path.exists():
            print(f"❌ 路径不存在: {source_path}")
            return 1
        skill_name = source_path.name
        is_git = False
    elif source_type == '2':
        git_url = input("Git 仓库 URL: ").strip()
        skill_name = Path(git_url).stem
        is_git = True
    else:
        print("❌ 无效的选择")
        return 1

    # 步骤 2: 询问安装级别
    print("\n步骤 2: 安装级别")
    print("1. 用户级 (User) - 仅您使用")
    print("2. 项目级 (Project) - 当前项目使用")
    print("3. 工作区级 (Workspace) - 工作区内所有项目使用")
    print("4. 系统级 (System) - 所有用户使用 [需要管理员权限]")

    # 提供默认建议
    project_root = installer.find_project_root()
    if project_root:
        print(f"\n💡 检测到项目根目录: {project_root}")
        print("   建议选择: 2 (项目级)")
    else:
        print("\n💡 未检测到项目目录")
        print("   建议选择: 1 (用户级)")

    level_choice = input("\n请选择安装级别 (1-4): ").strip()
    level_map = {'1': 'user', '2': 'project', '3': 'workspace', '4': 'system'}

    if level_choice not in level_map:
        print("❌ 无效的选择")
        return 1

    level = level_map[level_choice]

    # 步骤 3: 确定目标路径
    try:
        target_path = installer.get_install_path(level, skill_name)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    print(f"\n将安装到: {target_path}")
    confirm = input("是否继续？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return 0

    # 步骤 4: 检查权限
    has_permission, msg = installer.check_permissions(target_path, level)
    if not has_permission:
        print(f"❌ {msg}")
        if level == 'system' and os.name != 'nt':
            print("提示: 使用 sudo python3 install_skill.py 运行")
        return 1

    # 步骤 5: 检查冲突
    backup = False
    if target_path.exists():
        print(f"\n⚠️  技能已存在: {skill_name}")
        print("请选择操作：")
        print("1. 覆盖 (Overwrite)")
        print("2. 跳过 (Skip)")
        print("3. 备份后覆盖 (Backup & Overwrite)")
        print("4. 取消 (Cancel)")

        choice = input("您的选择 (1-4): ").strip()
        if choice == '2':
            print("已跳过")
            return 0
        elif choice == '3':
            backup = True
        elif choice == '4':
            print("已取消")
            return 0
        elif choice != '1':
            print("❌ 无效的选择")
            return 1

    # 步骤 6: 执行安装
    print(f"\n安装中...")

    if is_git:
        success, msg = installer.install_from_git(git_url, target_path, backup)
    else:
        success, msg = installer.install_from_local(source_path, target_path, backup)

    if success:
        print(f"\n✅ {msg}")

        # 读取技能描述
        skill_md = target_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')
        parts = content.split('---', 2)
        frontmatter = yaml.safe_load(parts[1])
        description = frontmatter.get('description', '')

        print(f"\n技能信息:")
        print(f"  名称: {skill_name}")
        print(f"  描述: {description}")
        print(f"  级别: {level}")
        print(f"  位置: {target_path}")

        print(f"\n下一步:")
        print(f"  - 重启或重新加载您的代理以识别新技能")
        print(f"  - 查看 {target_path}/SKILL.md 了解使用说明")

        return 0
    else:
        print(f"\n❌ {msg}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(interactive_install())
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
