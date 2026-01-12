# 技能名称验证规则

## 规范要求

技能名称必须符合以下所有要求：

### 长度要求
- **最小长度**: 1 字符
- **最大长度**: 64 字符

### 字符要求
- **允许的字符**:
  - Unicode 小写字母 (a-z)
  - 数字 (0-9)
  - 连字符 (-)
- **不允许的字符**:
  - 大写字母
  - 下划线
  - 空格
  - 特殊符号

### 连字符规则
- ❌ 不能以连字符开头: `-my-skill`
- ❌ 不能以连字符结尾: `my-skill-`
- ❌ 不能包含连续连字符: `my--skill`
- ✅ 可以在中间使用单个连字符: `my-skill`

### 目录名一致性
- 技能名称必须与包含 SKILL.md 的目录名完全一致

## 有效示例

```
✅ pdf-processing
✅ data-analysis
✅ code-review
✅ api-client
✅ text-summarizer
✅ image-processing-v2
```

## 无效示例及原因

```
❌ PDF-Processing
   原因: 包含大写字母

❌ -pdf
   原因: 以连字符开头

❌ pdf-processing-
   原因: 以连字符结尾

❌ pdf--processing
   原因: 包含连续连字符

❌ pdf_processing
   原因: 包含下划线

❌ pdf processing
   原因: 包含空格

❌ pdf.processing
   原因: 包含句点

❌ this-is-a-very-long-skill-name-that-exceeds-the-maximum-allowed-length
   原因: 超过 64 字符
```

## 名称转换规则

如果用户提供的名称不符合规范，可以应用以下转换：

1. **转换为小写**: `PDF Processing` → `pdf processing`
2. **替换空格为连字符**: `pdf processing` → `pdf-processing`
3. **移除非法字符**: `pdf_processing!` → `pdfprocessing`
4. **移除首尾连字符**: `-pdf-` → `pdf`
5. **合并连续连字符**: `pdf--processing` → `pdf-processing`
6. **截断过长名称**: 保留前 64 字符

## 验证伪代码

```python
def validate_skill_name(name: str) -> tuple[bool, str]:
    """验证技能名称是否符合规范

    返回: (是否有效, 错误消息或空字符串)
    """
    # 检查长度
    if len(name) < 1:
        return False, "名称不能为空"
    if len(name) > 64:
        return False, f"名称过长 ({len(name)} 字符)，最多 64 字符"

    # 检查字符
    import re
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "名称只能包含小写字母、数字和连字符"

    # 检查连字符位置
    if name.startswith('-'):
        return False, "名称不能以连字符开头"
    if name.endswith('-'):
        return False, "名称不能以连字符结尾"
    if '--' in name:
        return False, "名称不能包含连续连字符"

    return True, ""

def suggest_valid_name(invalid_name: str) -> str:
    """为无效名称提供修正建议"""
    import re

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
```

## 常见问题

### Q: 为什么不允许大写字母？
A: 为了保持一致性和避免跨平台文件系统问题（某些系统区分大小写，某些不区分）。

### Q: 可以使用中文或其他 Unicode 字符吗？
A: 规范要求仅使用小写 ASCII 字母、数字和连字符，以确保最大兼容性。

### Q: 技能名称可以包含版本号吗？
A: 可以在名称中包含版本标识（如 `my-skill-v2`），但建议使用 metadata.version 字段来管理版本。

### Q: 如果目录名和 name 字段不一致会怎样？
A: 代理可能无法正确识别和加载技能。务必保持一致性。
