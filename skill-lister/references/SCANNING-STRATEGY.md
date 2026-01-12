# 技能扫描策略详解

本文档详细说明 skill-lister 如何扫描、识别和解析 Agent Skills。

## 扫描流程

### 1. 路径发现

skill-lister 按以下优先级顺序扫描技能目录：

```
1. 自定义路径（如果用户指定）
2. 项目级路径（优先级最高）
3. 工作区级路径
4. 用户级路径
5. 系统级路径（优先级最低）
6. 环境变量额外路径
```

### 2. 路径解析算法

#### 用户级路径

```python
def get_user_skills_dir() -> Path:
    # 1. 检查环境变量
    if 'AGENT_SKILLS_USER_DIR' in os.environ:
        return Path(os.environ['AGENT_SKILLS_USER_DIR'])

    # 2. 根据操作系统确定默认路径
    if os.name == 'nt':  # Windows
        return Path.home() / '.agent-skills'
    else:  # macOS/Linux
        # 遵循 XDG 规范
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            return Path(xdg_data_home) / 'agent-skills'
        return Path.home() / '.agent-skills'
```

#### 项目级路径

```python
def find_project_root(start_path: Path = None) -> Optional[Path]:
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # 项目标识文件
    project_markers = [
        '.git',           # Git 仓库
        'package.json',   # Node.js 项目
        'pyproject.toml', # Python 项目 (PEP 518)
        'setup.py',       # Python 项目 (传统)
        'Cargo.toml',     # Rust 项目
        'pom.xml',        # Java Maven 项目
        'build.gradle',   # Java Gradle 项目
        'go.mod',         # Go 项目
        'composer.json',  # PHP 项目
        'Gemfile',        # Ruby 项目
    ]

    # 向上遍历直到找到项目标识
    while current != current.parent:
        if any((current / marker).exists() for marker in project_markers):
            return current
        current = current.parent

    return None

def get_project_skills_dir() -> Optional[Path]:
    project_root = find_project_root()
    if project_root:
        skills_dir = project_root / '.agent-skills'
        if skills_dir.exists():
            return skills_dir
    return None
```

#### 系统级路径

```python
def get_system_skills_dir() -> Path:
    # 1. 检查环境变量
    if 'AGENT_SKILLS_SYSTEM_DIR' in os.environ:
        return Path(os.environ['AGENT_SKILLS_SYSTEM_DIR'])

    # 2. 根据操作系统确定默认路径
    if os.name == 'nt':  # Windows
        return Path('C:/ProgramData/agent-skills')
    elif platform.system() == 'Darwin':  # macOS
        return Path('/usr/local/share/agent-skills')
    else:  # Linux
        return Path('/usr/local/share/agent-skills')
```

### 3. 技能识别

对于找到的每个目录，执行以下步骤判断是否为有效技能：

```python
def is_valid_skill_dir(path: Path) -> bool:
    """判断目录是否为有效的技能目录"""

    # 1. 必须是目录
    if not path.is_dir():
        return False

    # 2. 不是隐藏目录（以 . 开头）
    if path.name.startswith('.'):
        return False

    # 3. 必须包含 SKILL.md 文件
    skill_md = path / 'SKILL.md'
    if not skill_md.exists() or not skill_md.is_file():
        return False

    return True
```

### 4. 元数据解析

对于识别的每个技能，解析其元数据：

```python
def parse_skill_metadata(skill_path: Path) -> Dict:
    """解析技能元数据"""

    skill_md = skill_path / 'SKILL.md'
    content = skill_md.read_text(encoding='utf-8')

    # 1. 检查是否以 YAML frontmatter 开头
    if not content.startswith('---'):
        raise ValueError("Missing YAML frontmatter")

    # 2. 分割 frontmatter 和 body
    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError("Invalid frontmatter format")

    # 3. 解析 YAML
    frontmatter = yaml.safe_load(parts[1])

    # 4. 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            raise ValueError(f"Missing required field: {field}")

    # 5. 验证字段格式
    validate_skill_name(frontmatter['name'])
    validate_description(frontmatter['description'])

    return frontmatter
```

## 性能优化

### 1. 懒加载策略

仅在需要时加载完整的技能信息：

```python
class SkillInfo:
    def __init__(self, path: Path):
        self.path = path
        self._metadata = None  # 延迟加载

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self):
        # 实际加载逻辑
        pass
```

### 2. 缓存机制

使用缓存避免重复解析：

```python
import time
import pickle

class SkillCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / 'skills-cache.pkl'

    def get(self, skill_path: Path) -> Optional[Dict]:
        """获取缓存的技能信息"""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'rb') as f:
                cache = pickle.load(f)

            # 检查文件是否被修改
            skill_md = skill_path / 'SKILL.md'
            cached_mtime = cache.get(str(skill_path), {}).get('mtime', 0)
            current_mtime = skill_md.stat().st_mtime

            if current_mtime <= cached_mtime:
                return cache[str(skill_path)]['data']

        except Exception:
            pass

        return None

    def set(self, skill_path: Path, data: Dict):
        """缓存技能信息"""
        cache = {}

        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
            except Exception:
                pass

        skill_md = skill_path / 'SKILL.md'
        cache[str(skill_path)] = {
            'mtime': skill_md.stat().st_mtime,
            'data': data
        }

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache, f)
```

### 3. 并行扫描

对于大量技能，使用并行处理：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_skills_parallel(skill_dirs: List[Path], max_workers: int = 4) -> List[SkillInfo]:
    """并行扫描技能"""
    skills = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_path = {
            executor.submit(parse_skill, path): path
            for path in skill_dirs
        }

        # 收集结果
        for future in as_completed(future_to_path):
            try:
                skill = future.result()
                if skill:
                    skills.append(skill)
            except Exception as e:
                path = future_to_path[future]
                print(f"Error parsing {path}: {e}")

    return skills
```

## 错误处理

### 1. 权限错误

```python
def scan_directory_safe(directory: Path) -> List[Path]:
    """安全地扫描目录，处理权限错误"""
    try:
        return [item for item in directory.iterdir() if item.is_dir()]
    except PermissionError:
        print(f"⚠️  警告: 无法读取 {directory} (权限被拒绝)")
        return []
    except OSError as e:
        print(f"⚠️  警告: 读取 {directory} 时出错: {e}")
        return []
```

### 2. 格式错误

```python
def parse_skill_safe(skill_path: Path) -> Optional[SkillInfo]:
    """安全地解析技能，捕获格式错误"""
    try:
        return SkillInfo(skill_path)
    except yaml.YAMLError as e:
        print(f"❌ YAML 解析错误 ({skill_path.name}): {e}")
        return None
    except ValueError as e:
        print(f"❌ 验证错误 ({skill_path.name}): {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误 ({skill_path.name}): {e}")
        return None
```

### 3. 编码错误

```python
def read_file_safe(file_path: Path) -> Optional[str]:
    """安全地读取文件，处理编码问题"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️  警告: 读取 {file_path} 失败: {e}")
            return None

    print(f"❌ 错误: 无法解码 {file_path}（尝试了 {encodings}）")
    return None
```

## 验证规则

### 1. 名称验证

```python
def validate_skill_name(name: str) -> Tuple[bool, Optional[str]]:
    """验证技能名称"""
    # 长度检查
    if len(name) < 1 or len(name) > 64:
        return False, f"名称长度必须在 1-64 字符之间（当前: {len(name)}）"

    # 字符检查
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "名称只能包含小写字母、数字和连字符"

    # 连字符位置检查
    if name.startswith('-'):
        return False, "名称不能以连字符开头"
    if name.endswith('-'):
        return False, "名称不能以连字符结尾"
    if '--' in name:
        return False, "名称不能包含连续连字符"

    return True, None
```

### 2. 描述验证

```python
def validate_description(description: str) -> Tuple[bool, Optional[str]]:
    """验证技能描述"""
    if not description or not description.strip():
        return False, "描述不能为空"

    if len(description) > 1024:
        return False, f"描述过长（{len(description)} 字符，最多 1024）"

    return True, None
```

### 3. 目录名一致性检查

```python
def check_name_consistency(skill_path: Path, skill_name: str) -> Optional[str]:
    """检查目录名与技能名称是否一致"""
    if skill_path.name != skill_name:
        return f"目录名 ({skill_path.name}) 与技能名称 ({skill_name}) 不一致"
    return None
```

## 搜索和过滤

### 1. 关键词搜索

```python
def search_skills(skills: List[SkillInfo], keyword: str) -> List[SkillInfo]:
    """按关键词搜索技能"""
    keyword_lower = keyword.lower()

    def matches(skill: SkillInfo) -> bool:
        # 在名称中搜索
        if keyword_lower in skill.name.lower():
            return True

        # 在描述中搜索
        if keyword_lower in skill.description.lower():
            return True

        # 在作者中搜索
        if skill.author and keyword_lower in skill.author.lower():
            return True

        # 在元数据中搜索
        for key, value in skill.metadata.items():
            if isinstance(value, str) and keyword_lower in value.lower():
                return True

        return False

    return [s for s in skills if matches(s)]
```

### 2. 级别过滤

```python
def filter_by_level(skills: List[SkillInfo], level: str) -> List[SkillInfo]:
    """按级别过滤技能"""
    return [s for s in skills if s.level == level]
```

### 3. 标签过滤

```python
def filter_by_tags(skills: List[SkillInfo], tags: List[str]) -> List[SkillInfo]:
    """按标签过滤技能"""
    def has_tags(skill: SkillInfo) -> bool:
        skill_tags = skill.metadata.get('tags', [])
        if isinstance(skill_tags, str):
            skill_tags = [skill_tags]
        return any(tag in skill_tags for tag in tags)

    return [s for s in skills if has_tags(s)]
```

## 排序策略

### 1. 按名称排序

```python
def sort_by_name(skills: List[SkillInfo], reverse: bool = False) -> List[SkillInfo]:
    return sorted(skills, key=lambda s: s.name.lower(), reverse=reverse)
```

### 2. 按级别排序

```python
def sort_by_level(skills: List[SkillInfo]) -> List[SkillInfo]:
    level_order = {'project': 0, 'workspace': 1, 'user': 2, 'system': 3, 'custom': 4}
    return sorted(skills, key=lambda s: (level_order.get(s.level, 99), s.name))
```

### 3. 按最近修改时间排序

```python
def sort_by_mtime(skills: List[SkillInfo], reverse: bool = True) -> List[SkillInfo]:
    def get_mtime(skill: SkillInfo) -> float:
        skill_md = skill.path / 'SKILL.md'
        return skill_md.stat().st_mtime if skill_md.exists() else 0

    return sorted(skills, key=get_mtime, reverse=reverse)
```

## 输出格式化

### 1. 颜色支持检测

```python
def supports_color() -> bool:
    """检测终端是否支持颜色"""
    # 检查环境变量
    if os.environ.get('NO_COLOR'):
        return False

    # 检查是否为 TTY
    if not sys.stdout.isatty():
        return False

    # Windows 特殊处理
    if os.name == 'nt':
        try:
            import colorama
            colorama.init()
            return True
        except ImportError:
            return False

    return True
```

### 2. 文本截断

```python
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """智能截断文本"""
    if len(text) <= max_length:
        return text

    # 在单词边界处截断
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.8:  # 如果空格位置合理
        truncated = truncated[:last_space]

    return truncated + suffix
```

## 统计信息

### 1. 基本统计

```python
def get_statistics(skills: List[SkillInfo]) -> Dict:
    """获取技能统计信息"""
    stats = {
        'total': len(skills),
        'by_level': {},
        'valid': 0,
        'invalid': 0,
        'with_scripts': 0,
        'with_references': 0,
        'with_assets': 0,
    }

    for skill in skills:
        # 按级别统计
        level = skill.level
        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1

        # 有效性统计
        if skill.is_valid:
            stats['valid'] += 1
        else:
            stats['invalid'] += 1

        # 附加目录统计
        if skill.has_scripts:
            stats['with_scripts'] += 1
        if skill.has_references:
            stats['with_references'] += 1
        if skill.has_assets:
            stats['with_assets'] += 1

    return stats
```

### 2. 显示统计

```python
def format_statistics(stats: Dict) -> str:
    """格式化统计信息"""
    lines = []
    lines.append(f"\n📊 统计信息")
    lines.append(f"总技能数: {stats['total']}")

    lines.append(f"\n按级别:")
    for level, count in sorted(stats['by_level'].items()):
        lines.append(f"  {level}: {count}")

    lines.append(f"\n状态:")
    lines.append(f"  有效: {stats['valid']}")
    lines.append(f"  无效: {stats['invalid']}")

    lines.append(f"\n附加资源:")
    lines.append(f"  包含脚本: {stats['with_scripts']}")
    lines.append(f"  包含参考文档: {stats['with_references']}")
    lines.append(f"  包含资源文件: {stats['with_assets']}")

    return '\n'.join(lines)
```

## 最佳实践

1. **始终验证输入**: 检查路径存在性和权限
2. **优雅处理错误**: 继续扫描其他技能而不是中断
3. **提供有用的错误信息**: 明确指出问题所在
4. **使用缓存**: 避免重复解析相同的技能
5. **支持并行**: 对于大量技能，提高扫描速度
6. **遵循标准**: 严格按照 Agent Skills 规范验证
