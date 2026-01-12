#!/usr/bin/env python3
"""
Skill Lister Script

列出和查看已安装的 Agent Skills。
支持 AgentSkills、Claude Code、Codex 三种规范。
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import yaml
from datetime import datetime


class SkillStandard(Enum):
    """技能规范标准"""
    AGENTSKILLS = "agentskills"
    CLAUDE = "claude"
    CODEX = "codex"
    ALL = "all"  # 扫描所有规范


# 规范配置
STANDARD_CONFIG = {
    SkillStandard.AGENTSKILLS: {
        "name": "AgentSkills",
        "user_dir": ".agent-skills",
        "project_dir": ".agent-skills",
        "system_windows": "C:/ProgramData/agent-skills",
        "system_unix": "/usr/local/share/agent-skills"
    },
    SkillStandard.CLAUDE: {
        "name": "Claude",
        "user_dir": ".claude/skills",
        "project_dir": ".claude/skills",
        "system_windows": None,
        "system_unix": None
    },
    SkillStandard.CODEX: {
        "name": "Codex",
        "user_dir": ".codex/skills",
        "project_dir": ".codex/skills",
        "system_windows": None,
        "system_unix": "/etc/codex/skills"
    }
}


class SkillInfo:
    """技能信息类"""

    def __init__(self, path: Path, level: str):
        self.path = path
        self.level = level
        self.name = ""
        self.description = ""
        self.version = None
        self.author = None
        self.license = None
        self.compatibility = None
        self.metadata = {}
        self.allowed_tools = []
        self.has_scripts = False
        self.has_references = False
        self.has_assets = False
        self.is_valid = False
        self.errors = []
        self.warnings = []

        self._parse()

    def _parse(self):
        """解析技能元数据"""
        skill_md = self.path / 'SKILL.md'

        if not skill_md.exists():
            self.errors.append("缺少 SKILL.md 文件")
            return

        try:
            content = skill_md.read_text(encoding='utf-8')

            # 检查 YAML frontmatter
            if not content.startswith('---'):
                self.errors.append("SKILL.md 必须以 YAML frontmatter 开头")
                return

            # 提取 frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                self.errors.append("YAML frontmatter 格式错误")
                return

            frontmatter = yaml.safe_load(parts[1])

            # 提取必需字段
            if 'name' not in frontmatter:
                self.errors.append("缺少必需字段: name")
                return
            self.name = frontmatter['name']

            if 'description' not in frontmatter:
                self.errors.append("缺少必需字段: description")
                return
            self.description = frontmatter['description']

            # 验证目录名与技能名称一致
            if self.path.name != self.name:
                self.warnings.append(
                    f"目录名 ({self.path.name}) 与技能名称 ({self.name}) 不一致"
                )

            # 提取可选字段
            self.license = frontmatter.get('license')
            self.compatibility = frontmatter.get('compatibility')
            self.metadata = frontmatter.get('metadata', {})

            if isinstance(self.metadata, dict):
                self.version = self.metadata.get('version')
                self.author = self.metadata.get('author')

            allowed_tools = frontmatter.get('allowed-tools', '')
            if allowed_tools:
                self.allowed_tools = allowed_tools.split()

            # 检查附加目录
            self.has_scripts = (self.path / 'scripts').exists()
            self.has_references = (self.path / 'references').exists()
            self.has_assets = (self.path / 'assets').exists()

            self.is_valid = True

        except yaml.YAMLError as e:
            self.errors.append(f"YAML 解析错误: {str(e)}")
        except Exception as e:
            self.errors.append(f"解析失败: {str(e)}")

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'path': str(self.path),
            'level': self.level,
            'version': self.version,
            'author': self.author,
            'license': self.license,
            'compatibility': self.compatibility,
            'metadata': self.metadata,
            'allowed_tools': self.allowed_tools,
            'has_scripts': self.has_scripts,
            'has_references': self.has_references,
            'has_assets': self.has_assets,
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


class SkillLister:
    """技能列表器"""

    def __init__(self, standard: SkillStandard = SkillStandard.ALL):
        self.standard = standard
        self.skills = []
        self.level_colors = {
            'user': '\033[94m',      # 蓝色
            'project': '\033[92m',   # 绿色
            'workspace': '\033[93m', # 黄色
            'system': '\033[95m',    # 紫色
        }
        self.reset_color = '\033[0m'
        self.use_color = True

    def get_user_skills_dir(self, std: SkillStandard) -> Optional[Path]:
        """获取用户级技能目录(根据规范)"""
        if std == SkillStandard.ALL:
            return None

        config = STANDARD_CONFIG[std]
        user_dir = config["user_dir"]
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
        """获取项目级技能目录"""
        project_root = self.find_project_root()
        if project_root:
            skills_dir = project_root / '.agent-skills'
            if skills_dir.exists():
                return skills_dir
        return None

    def get_system_skills_dir(self) -> Optional[Path]:
        """获取系统级技能目录"""
        if 'AGENT_SKILLS_SYSTEM_DIR' in os.environ:
            return Path(os.environ['AGENT_SKILLS_SYSTEM_DIR'])

        if os.name == 'nt':  # Windows
            return Path('C:/ProgramData/agent-skills')
        else:  # macOS/Linux
            return Path('/usr/local/share/agent-skills')

    def get_all_skills_dirs(self) -> List[Tuple[Path, str]]:
        """获取所有技能目录（路径, 级别）"""
        dirs = []

        # 确定要扫描的规范
        if self.standard == SkillStandard.ALL:
            standards = [SkillStandard.AGENTSKILLS, SkillStandard.CLAUDE, SkillStandard.CODEX]
        else:
            standards = [self.standard]

        # 扫描每个规范的路径
        for std in standards:
            config = STANDARD_CONFIG[std]

            # 用户级
            user_dir = self.get_user_skills_dir(std)
            if user_dir and user_dir.exists():
                dirs.append((user_dir, f'user-{config["name"]}'))

            # 项目级
            project_root = self.find_project_root()
            if project_root:
                project_dir = project_root / config["project_dir"]
                if project_dir.exists():
                    dirs.append((project_dir, f'project-{config["name"]}'))

            # 系统级
            if os.name == 'nt':
                sys_path = config.get("system_windows")
            else:
                sys_path = config.get("system_unix")

            if sys_path:
                sys_dir = Path(sys_path)
                if sys_dir.exists():
                    dirs.append((sys_dir, f'system-{config["name"]}'))

        return dirs

    def scan_skills(self, paths: Optional[List[Tuple[Path, str]]] = None) -> List[SkillInfo]:
        """扫描技能"""
        if paths is None:
            paths = self.get_all_skills_dirs()

        skills = []

        for skill_dir, level in paths:
            if not skill_dir.exists():
                continue

            # 列出所有子目录
            try:
                for item in skill_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        skill_info = SkillInfo(item, level)
                        skills.append(skill_info)
            except PermissionError:
                print(f"⚠️  警告: 无法读取 {skill_dir} (权限被拒绝)", file=sys.stderr)

        return skills

    def filter_skills(
        self,
        skills: List[SkillInfo],
        search: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[SkillInfo]:
        """过滤技能"""
        result = skills

        # 按级别过滤
        if level:
            result = [s for s in result if s.level == level]

        # 按关键词搜索
        if search:
            search_lower = search.lower()
            result = [
                s for s in result
                if search_lower in s.name.lower() or
                search_lower in s.description.lower() or
                (s.author and search_lower in s.author.lower())
            ]

        return result

    def colorize(self, text: str, level: str) -> str:
        """添加颜色"""
        if not self.use_color:
            return text
        color = self.level_colors.get(level, '')
        return f"{color}{text}{self.reset_color}"

    def format_list(self, skills: List[SkillInfo], group_by_level: bool = True) -> str:
        """格式化为列表"""
        if not skills:
            return "❌ 未找到技能"

        lines = []
        lines.append(f"\n📚 已安装的技能 (共 {len(skills)} 个)\n")

        if group_by_level:
            # 按级别分组
            grouped = {}
            for skill in skills:
                if skill.level not in grouped:
                    grouped[skill.level] = []
                grouped[skill.level].append(skill)

            level_names = {
                'user': '用户级',
                'project': '项目级',
                'workspace': '工作区级',
                'system': '系统级',
                'custom': '自定义'
            }

            level_order = ['project', 'workspace', 'user', 'system', 'custom']

            for level in level_order:
                if level not in grouped:
                    continue

                level_skills = sorted(grouped[level], key=lambda s: s.name)
                level_name = level_names.get(level, level)

                # 获取第一个技能的路径作为级别路径
                if level_skills:
                    level_path = level_skills[0].path.parent

                lines.append(f"\n【{level_name}】 ({level_path})")

                for i, skill in enumerate(level_skills, 1):
                    lines.append(f"  {i}. {self.colorize(skill.name, skill.level)}")

                    if skill.is_valid:
                        desc = skill.description
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        lines.append(f"     描述: {desc}")

                        if skill.version:
                            lines.append(f"     版本: {skill.version}")
                    else:
                        lines.append(f"     ❌ 错误: {', '.join(skill.errors)}")

                    if skill.warnings:
                        for warning in skill.warnings:
                            lines.append(f"     ⚠️  警告: {warning}")

        else:
            # 不分组，按名称排序
            sorted_skills = sorted(skills, key=lambda s: s.name)
            for i, skill in enumerate(sorted_skills, 1):
                lines.append(f"\n{i}. {self.colorize(skill.name, skill.level)}")
                lines.append(f"   描述: {skill.description}")
                lines.append(f"   级别: {skill.level}")
                lines.append(f"   路径: {skill.path}")

        return '\n'.join(lines)

    def format_table(self, skills: List[SkillInfo]) -> str:
        """格式化为表格"""
        if not skills:
            return "❌ 未找到技能"

        # 计算列宽
        max_name = max(len(s.name) for s in skills) if skills else 10
        max_desc = 40
        max_version = 8
        max_level = 6

        # 表头
        lines = []
        header = f"| {'名称':<{max_name}} | {'描述':<{max_desc}} | {'版本':<{max_version}} | {'级别':<{max_level}} |"
        separator = f"|{'-' * (max_name + 2)}|{'-' * (max_desc + 2)}|{'-' * (max_version + 2)}|{'-' * (max_level + 2)}|"

        lines.append(header)
        lines.append(separator)

        # 数据行
        sorted_skills = sorted(skills, key=lambda s: (s.level, s.name))
        for skill in sorted_skills:
            name = skill.name[:max_name]
            desc = skill.description[:max_desc - 3] + "..." if len(skill.description) > max_desc else skill.description
            version = skill.version or "N/A"
            level = skill.level

            line = f"| {name:<{max_name}} | {desc:<{max_desc}} | {version:<{max_version}} | {level:<{max_level}} |"
            lines.append(line)

        return '\n'.join(lines)

    def format_detail(self, skill: SkillInfo) -> str:
        """格式化详细信息"""
        lines = []
        lines.append(f"\n📋 技能详细信息\n")
        lines.append(f"名称: {self.colorize(skill.name, skill.level)}")
        lines.append(f"描述: {skill.description}")
        lines.append(f"路径: {skill.path}")
        lines.append(f"级别: {skill.level}")

        if skill.version:
            lines.append(f"版本: {skill.version}")
        if skill.author:
            lines.append(f"作者: {skill.author}")
        if skill.license:
            lines.append(f"许可证: {skill.license}")
        if skill.compatibility:
            lines.append(f"兼容性: {skill.compatibility}")

        # 目录结构
        lines.append(f"\n目录结构:")
        lines.append(f"  ├── SKILL.md")
        if skill.has_scripts:
            script_count = len(list((skill.path / 'scripts').glob('*')))
            lines.append(f"  ├── scripts/ ({script_count} 个文件)")
        if skill.has_references:
            ref_count = len(list((skill.path / 'references').glob('*')))
            lines.append(f"  ├── references/ ({ref_count} 个文件)")
        if skill.has_assets:
            lines.append(f"  └── assets/")

        # 元数据
        if skill.metadata:
            lines.append(f"\n元数据:")
            for key, value in skill.metadata.items():
                lines.append(f"  {key}: {value}")

        # 允许的工具
        if skill.allowed_tools:
            lines.append(f"\n允许的工具:")
            for tool in skill.allowed_tools:
                lines.append(f"  - {tool}")

        # 错误和警告
        if skill.errors:
            lines.append(f"\n❌ 错误:")
            for error in skill.errors:
                lines.append(f"  - {error}")

        if skill.warnings:
            lines.append(f"\n⚠️  警告:")
            for warning in skill.warnings:
                lines.append(f"  - {warning}")

        # 完整的 SKILL.md 内容（可选）
        skill_md = skill.path / 'SKILL.md'
        if skill_md.exists():
            lines.append(f"\n{'=' * 60}")
            lines.append(f"完整的 SKILL.md 内容:")
            lines.append(f"{'=' * 60}\n")
            lines.append(skill_md.read_text(encoding='utf-8'))

        return '\n'.join(lines)

    def format_json(self, skills: List[SkillInfo]) -> str:
        """格式化为 JSON"""
        data = {
            'total_count': len(skills),
            'timestamp': datetime.now().isoformat(),
            'skills': [s.to_dict() for s in skills]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def check_format(self, skills: List[SkillInfo]) -> str:
        """检查格式"""
        lines = []
        lines.append(f"\n🔍 技能格式检查\n")

        correct = 0
        warnings = 0
        errors = 0

        for skill in sorted(skills, key=lambda s: s.name):
            if skill.is_valid and not skill.warnings:
                lines.append(f"✅ {skill.name}: 格式正确")
                correct += 1
            elif skill.is_valid and skill.warnings:
                lines.append(f"⚠️  {skill.name}: 警告")
                warnings += 1
                for warning in skill.warnings:
                    lines.append(f"   - {warning}")
            else:
                lines.append(f"❌ {skill.name}: 错误")
                errors += 1
                for error in skill.errors:
                    lines.append(f"   - {error}")

        lines.append(f"\n总结: {len(skills)} 个技能，{correct} 个正确，{warnings} 个警告，{errors} 个错误")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='列出和查看已安装的 Agent Skills',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-p', '--path',
        help='扫描指定路径而非默认路径'
    )
    parser.add_argument(
        '-l', '--level',
        choices=['user', 'project', 'workspace', 'system'],
        help='仅显示特定级别的技能'
    )
    parser.add_argument(
        '-s', '--search',
        help='搜索包含关键词的技能'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['list', 'table', 'json'],
        default='list',
        help='输出格式 (默认: list)'
    )
    parser.add_argument(
        '-d', '--detail',
        help='显示特定技能的详细信息'
    )
    parser.add_argument(
        '-c', '--check',
        action='store_true',
        help='检查技能格式问题'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用颜色输出'
    )
    parser.add_argument(
        '--no-group',
        action='store_true',
        help='不按级别分组'
    )

    args = parser.parse_args()

    lister = SkillLister()

    if args.no_color:
        lister.use_color = False

    # 扫描技能
    if args.path:
        custom_path = Path(args.path)
        if not custom_path.exists():
            print(f"❌ 路径不存在: {custom_path}", file=sys.stderr)
            return 1
        paths = [(custom_path, 'custom')]
        skills = lister.scan_skills(paths)
    else:
        skills = lister.scan_skills()

    # 过滤技能
    skills = lister.filter_skills(skills, args.search, args.level)

    # 显示详细信息
    if args.detail:
        matching = [s for s in skills if s.name == args.detail]
        if not matching:
            print(f"❌ 未找到技能: {args.detail}", file=sys.stderr)
            return 1
        print(lister.format_detail(matching[0]))
        return 0

    # 检查格式
    if args.check:
        print(lister.check_format(skills))
        return 0

    # 显示列表
    if args.format == 'list':
        print(lister.format_list(skills, not args.no_group))
    elif args.format == 'table':
        print(lister.format_table(skills))
    elif args.format == 'json':
        print(lister.format_json(skills))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
