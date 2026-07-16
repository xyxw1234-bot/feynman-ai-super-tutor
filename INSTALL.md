# 安装说明

## 方式一：给智能体发送 raw SKILL.md 链接

将以下链接发给支持 Hermes Skill 安装的智能体：

```text
https://raw.githubusercontent.com/OWNER/feynman-ai-super-tutor/main/SKILL.md
```

告诉它：请读取并安装这个 Skill，安装后作为我的费曼AI超级学习导师工作。

## 方式二：Hermes CLI〔命令行〕安装

```bash
hermes skills install https://raw.githubusercontent.com/OWNER/feynman-ai-super-tutor/main/SKILL.md --yes
```

## 可选：安装插件

如果需要本地学习档案、材料话题地图和复习计划工具，可把 `plugins/feynman_super_tutor` 安装到 Hermes 插件目录并启用：

```bash
mkdir -p ~/.hermes/plugins/feynman_super_tutor
cp -R plugins/feynman_super_tutor/* ~/.hermes/plugins/feynman_super_tutor/
hermes plugins enable feynman_super_tutor
```

重启 Hermes 或飞书 Gateway〔网关〕后生效。

## 数据位置

插件数据默认保存在当前 Hermes profile〔配置档案〕的数据目录，不会写进 Skill 仓库，不会随更新覆盖用户学习档案。

## 合规边界

不要把盗版教材、盗版教辅或付费题库全文放入本项目。用户资料、学生隐私、错题数据和学习档案应留在用户自己的 Hermes profile 中。
