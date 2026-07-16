# 费曼AI超级学习导师

面向 Hermes / 节点引擎 / 飞书智能体的一键安装学习导师能力包。

它不是普通“AI讲题机器人”，而是让学生先讲，AI 再追问、诊断、补强、复习和沉淀学习档案的费曼式学伴。

## 直接安装入口

把下面这个 raw 链接发给支持 Hermes Skill 安装的智能体：

```text
https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md
```

也可以在命令行安装：

```bash
hermes skills install https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md --yes
```

## 核心价值

- 学生先讲，AI 后教
- 通过追问暴露理解裂缝
- 在认知边界外一步工作
- 诊断错因，而不是只给答案
- 把教材、教辅、视频、文章转成学习路线
- 支持中国中小学教材、考试和家校场景
- 强调正版资源、隐私保护和学术诚信

## 和普通 AI 学习助手的区别

| 场景 | 普通 AI | 费曼AI超级学习导师 |
|---|---|---|
| 讲解 | AI 直接讲 | 学生先讲，AI 找漏洞 |
| 诊断 | 常问“懂了吗” | 用追问暴露认知边界 |
| 错题 | 直接给答案 | 先判断错因，再最小提示 |
| 复习 | 总结知识点 | 建立错因、边界和复习路径 |
| 材料 | 摘要材料 | 转成话题地图和费曼讨论 |
| 长期 | 每次重来 | 沉淀学习档案与知识地图 |

## 使用示例

```text
带我用费曼法学初二物理浮力。
```

```text
我给你讲一遍二次函数，你找漏洞。
```

```text
这道题不要直接给答案，先问我。
```

```text
把这篇材料拆成学习路线，然后带我学第一部分。
```

```text
我是家长，帮我判断孩子到底哪里没懂。
```

```text
我是老师，帮我设计一组能暴露学生误区的课堂追问。
```

## 推荐给用户/智能体的一整段安装指令

```text
请读取并安装这个 Skill，安装后启用费曼AI超级学习导师。如果你运行在 Hermes / 节点引擎环境，请自动安装主 Skill，并在支持插件时安装启用配套插件；完成后主动给我发一段简短介绍和使用建议：https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md
```

## Hermes 命令行安装

```bash
hermes skills install https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md --yes --category education
hermes plugins install xyxw1234-bot/feynman-ai-super-tutor/plugins/feynman_super_tutor --force --enable
```

网关/飞书智能体安装后需要进入新会话或受控重启 gateway 才能完整加载新 Skill/插件。

## 可选 Hermes 插件

仓库内提供 `plugins/feynman_super_tutor/`，用于在 Hermes profile〔配置档案〕内本地保存学习档案、生成复习计划、将材料转为话题地图。插件不依赖外部服务器，不创建外部数据库，数据默认保存在当前用户自己的 Hermes profile 数据目录。

如果用户环境没有安装插件，`SKILL.md` 仍可独立运行；只是学习档案会依赖智能体自身的记忆或会话。

## 文件说明

- `SKILL.md`：主安装入口，适合直接发给智能体安装。
- `references/learning-architecture.md`：完整学习系统架构。
- `references/china-k12-resource-policy.md`：中国中小学正版资源与版权边界。
- `templates/`：学习档案和会话记录模板。
- `scripts/feynman_material_ingest.py`：轻量材料整理脚本。
- `plugins/feynman_super_tutor/`：后续 Hermes 插件化增强入口。

## 版权与合规

本项目可帮助用户学习其合法提供或公开授权的资料，但不提供盗版教材、盗版教辅、付费题库全文抓取或绕过平台限制的能力。

## 致谢

本项目吸收并产品化改造了开源项目 [koukekoukej-glitch/feynman-tutor](https://github.com/koukekoukej-glitch/feynman-tutor) 的核心理念。原项目采用 MIT 许可证。
