# INSTALL

项目的技能符合AgentSkill规范，可以支持Claude Code和Codex等Agents。

下面以Claude Code为例，演示如何安装。你可以手动安装，也可以把这个页面给Claude Code让它帮你完成。

## 需要准备

- Python 3
- 安装依赖：`pip install pyyaml`

## 安装

只要把本仓库里的 3 个技能目录（skill-creator、skill-installer、skill-lister）复制到`~/.claude/skills/`，就可以直接使用了。
注意是否有重名技能，如果有重名技能，建议先备份，再复制。

## 验证

Claude Code 支持热加载，安装之后使用 `/skill` 技能看到技能。如果不行就重启一下！









