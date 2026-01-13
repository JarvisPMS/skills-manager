# ASCII 艺术字母转换器

一个用于将普通文本转换为 ASCII 艺术字的 Claude 技能。

## 文件结构

```
ascii-art-converter/
├── SKILL.md                    # 主技能文件（必需）
├── README.md                   # 本文件
└── references/                 # 参考资料
    └── FONT-EXAMPLES.md       # 字体示例和参考
```

## 快速使用

只需对 Claude 说：
```
"把 HELLO 转换成 ASCII 艺术字"
```

Claude 会自动识别并使用此技能生成相应的 ASCII 艺术字。

## 功能特点

✅ 支持英文字母 (A-Z)
✅ 支持数字 (0-9)
✅ 支持多种字体风格
✅ 自动格式化和对齐
✅ 保持完整的视觉效果

## 支持的风格

- 标准风格 (Standard) - 默认
- 简约风格 (Simple)
- 3D 风格 (3D)
- 粗体风格 (Bold)
- 花体风格 (Fancy)

## 技术规范

- **规范**: Claude Code Skills Standard
- **版本**: 1.0.0
- **许可**: MIT
- **用户可调用**: 是

## 相关文档

- [SKILL.md](./SKILL.md) - 完整的技能说明和使用指南
- [FONT-EXAMPLES.md](./references/FONT-EXAMPLES.md) - 字体示例和参考

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License - 自由使用和修改
