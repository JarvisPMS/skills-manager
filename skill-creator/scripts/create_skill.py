#!/usr/bin/env python3
"""
Skill Creator Script

这个脚本帮助自动创建符合 Agent Skills 规范的技能结构。
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def validate_skill_name(name: str) -> Tuple[bool, str]:
    """
    验证技能名称是否符合规范

    返回: (是否有效, 错误消息或空字符串)
    """
    if len(name) < 1:
        return False, "名称不能为空"
    if len(name) > 64:
        return False, f"名称过长 ({len(name)} 字符)，最多 64 字符"

    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "名称只能包含小写字母、数字和连字符"

    if name.startswith('-'):
        return False, "名称不能以连字符开头"
    if name.endswith('-'):
        return False, "名称不能以连字符结尾"
    if '--' in name:
        return False, "名称不能包含连续连字符"

    return True, ""


def suggest_valid_name(invalid_name: str) -> str:
    """为无效名称提供修正建议"""
    # 转小写
    name = invalid_name.lower()

    # 替换非法字符为连字符
    name = re.sub(r'[^a-z0-9-]+', '-', name)

    # 合并连续连字符
    name = re.sub(r'-+', '-', name)

    # 移除首尾连字符
    name = name.strip('-')

    # 截断到 64 字符
    if len(name) > 64:
        name = name[:64].rstrip('-')

    return name


def validate_description(description: str) -> Tuple[bool, str]:
    """验证描述是否符合规范"""
    if len(description) < 1:
        return False, "描述不能为空"
    if len(description) > 1024:
        return False, f"描述过长 ({len(description)} 字符)，最多 1024 字符"
    return True, ""


def generate_frontmatter(
    name: str,
    description: str,
    license: Optional[str] = None,
    compatibility: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    allowed_tools: Optional[List[str]] = None
) -> str:
    """生成 YAML frontmatter"""
    lines = ["---", f"name: {name}", f"description: {description}"]

    if license:
        lines.append(f"license: {license}")

    if compatibility:
        lines.append(f"compatibility: {compatibility}")

    if metadata:
        lines.append("metadata:")
        for key, value in metadata.items():
            lines.append(f"  {key}: {value}")

    if allowed_tools:
        lines.append(f"allowed-tools: {' '.join(allowed_tools)}")

    lines.append("---")
    return "\n".join(lines)


def generate_skill_md(
    name: str,
    description: str,
    title: Optional[str] = None,
    **kwargs
) -> str:
    """生成完整的 SKILL.md 内容"""
    if title is None:
        title = name.replace('-', ' ').title()

    frontmatter = generate_frontmatter(name, description, **kwargs)

    body = f"""
# {title}

## 使用场景

{description}

## 功能说明

### 主要功能

在此描述技能的主要功能...

## 使用步骤

1. 第一步
2. 第二步
3. 第三步

## 示例

提供使用示例...

## 注意事项

列出重要的注意事项...
"""

    return frontmatter + "\n" + body


def create_skill_structure(
    base_path: str,
    name: str,
    description: str,
    include_scripts: bool = False,
    include_references: bool = False,
    include_assets: bool = False,
    **kwargs
) -> Tuple[bool, str]:
    """
    创建技能目录结构

    返回: (是否成功, 消息)
    """
    # 验证名称
    valid, error = validate_skill_name(name)
    if not valid:
        return False, f"名称验证失败: {error}"

    # 验证描述
    valid, error = validate_description(description)
    if not valid:
        return False, f"描述验证失败: {error}"

    # 创建技能目录
    skill_path = Path(base_path) / name
    if skill_path.exists():
        return False, f"技能目录已存在: {skill_path}"

    try:
        skill_path.mkdir(parents=True, exist_ok=False)

        # 创建 SKILL.md
        skill_md_content = generate_skill_md(name, description, **kwargs)
        (skill_path / "SKILL.md").write_text(skill_md_content, encoding='utf-8')

        # 创建可选目录
        if include_scripts:
            scripts_path = skill_path / "scripts"
            scripts_path.mkdir()
            (scripts_path / "README.md").write_text(
                "# Scripts\n\n在此放置可执行脚本。\n",
                encoding='utf-8'
            )

        if include_references:
            refs_path = skill_path / "references"
            refs_path.mkdir()
            (refs_path / "REFERENCE.md").write_text(
                f"# {name.replace('-', ' ').title()} - 参考文档\n\n详细的技术参考文档。\n",
                encoding='utf-8'
            )

        if include_assets:
            assets_path = skill_path / "assets"
            assets_path.mkdir()
            (assets_path / "README.md").write_text(
                "# Assets\n\n模板、图片和其他资源文件。\n",
                encoding='utf-8'
            )

        return True, f"成功创建技能: {skill_path}"

    except Exception as e:
        return False, f"创建技能时出错: {str(e)}"


def interactive_create():
    """交互式创建技能"""
    print("=== Agent Skill Creator ===\n")

    # 获取技能名称
    while True:
        name_input = input("技能名称 (小写字母、数字和连字符): ").strip()
        valid, error = validate_skill_name(name_input)

        if valid:
            name = name_input
            break
        else:
            print(f"❌ {error}")
            suggestion = suggest_valid_name(name_input)
            if suggestion and suggestion != name_input:
                use_suggestion = input(f"建议使用: {suggestion} (y/n)? ").strip().lower()
                if use_suggestion == 'y':
                    name = suggestion
                    break

    # 获取描述
    while True:
        description = input("\n技能描述 (1-1024 字符): ").strip()
        valid, error = validate_description(description)

        if valid:
            break
        else:
            print(f"❌ {error}")

    # 可选信息
    print("\n=== 可选信息 ===")
    license_input = input("许可证 (可选，直接回车跳过): ").strip()
    license = license_input if license_input else None

    compatibility_input = input("兼容性要求 (可选): ").strip()
    compatibility = compatibility_input if compatibility_input else None

    # 元数据
    metadata = {}
    add_metadata = input("添加元数据? (y/n): ").strip().lower()
    if add_metadata == 'y':
        metadata['author'] = input("  作者: ").strip()
        metadata['version'] = input("  版本: ").strip()

    # 附加目录
    print("\n=== 附加资源 ===")
    include_scripts = input("包含 scripts/ 目录? (y/n): ").strip().lower() == 'y'
    include_references = input("包含 references/ 目录? (y/n): ").strip().lower() == 'y'
    include_assets = input("包含 assets/ 目录? (y/n): ").strip().lower() == 'y'

    # 创建路径
    base_path = input("\n创建位置 (默认当前目录): ").strip()
    if not base_path:
        base_path = "."

    # 创建技能
    print("\n创建技能中...")
    success, message = create_skill_structure(
        base_path=base_path,
        name=name,
        description=description,
        license=license,
        compatibility=compatibility,
        metadata=metadata if metadata else None,
        include_scripts=include_scripts,
        include_references=include_references,
        include_assets=include_assets
    )

    if success:
        print(f"\n✅ {message}")
        print(f"\n技能结构:")
        skill_path = Path(base_path) / name
        for root, dirs, files in os.walk(skill_path):
            level = root.replace(str(skill_path), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    else:
        print(f"\n❌ {message}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(interactive_create())
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(1)
