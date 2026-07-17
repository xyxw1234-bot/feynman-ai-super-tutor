# 安装说明

## 方式一：给智能体发送 raw SKILL.md 链接

将以下链接发给支持 Hermes Skill 安装的智能体：

```text
https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md
```

可直接转发这一整段：

```text
请读取并安装这个 Skill，安装后启用费曼AI超级学习导师。如果你运行在 Hermes / 节点引擎环境，请自动安装主 Skill，并在支持插件时安装启用配套插件；完成后主动给我发一段简短介绍和使用建议：https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md
```

## 方式二：Hermes CLI〔命令行〕安装

```bash
hermes skills install https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md --yes --category education
hermes plugins install xyxw1234-bot/feynman-ai-super-tutor/plugins/feynman_super_tutor --force --enable
```

飞书网关智能体需要新会话或受控重启后完整生效。普通用户不需要看到命令、路径或日志。

## v1.1 插件能力

插件提供学习卡、学习档案读取、材料话题地图、复习计划，以及可视化互动增强工具：视觉必要性判断、互动 H5 需求说明、H5 生成、H5 静态质检、视觉素材列表。

生成 H5 后，正式发给学生前必须额外完成：浏览器打开、手机宽度检查、所有控件真实操作、学科正确性复核、部署后的公网 200 检查。

## 数据位置

插件数据默认保存在当前 Hermes profile〔配置档案〕的数据目录，不会写进 Skill 仓库，不会随更新覆盖用户学习档案。

## 合规边界

不要把盗版教材、盗版教辅或付费题库全文放入本项目。用户资料、学生隐私、错题数据和学习档案应留在用户自己的 Hermes profile 中。
