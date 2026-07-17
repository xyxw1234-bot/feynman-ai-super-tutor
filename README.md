# 费曼AI超级学习导师

当前版本：v1.3.3「官方课程教材定位增强版」。

面向 Hermes / 节点引擎 / 飞书智能体的一键安装学习导师能力包。

它不是普通“AI讲题机器人”，而是让学生先讲，AI 再追问、诊断、补强、复习和沉淀学习档案的费曼式学伴。v1.1 增加“可视化互动学习增强版”：当数理化等问题只靠文字不够直观时，智能体会判断是否需要简图、配图或经过检查的互动 H5〔网页互动课件〕。

## 直接安装入口

把下面这个 raw 链接发给支持 Hermes Skill 安装的智能体：

```text
https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md
```

也可以在命令行安装：

```bash
hermes skills install https://raw.githubusercontent.com/xyxw1234-bot/feynman-ai-super-tutor/main/SKILL.md --yes --category education
hermes plugins install xyxw1234-bot/feynman-ai-super-tutor/plugins/feynman_super_tutor --force --enable
```

## 核心价值

- 学生先讲，AI 后教
- 通过追问暴露理解裂缝
- 在认知边界外一步工作
- 诊断错因，而不是只给答案
- 把教材、教辅、视频、文章转成学习路线
- 支持中国中小学教材、考试和家校场景
- 针对函数图像、受力、浮力、电路、化学粒子等内容，判断是否需要视觉或互动脚手架
- 强调正版资源、隐私保护和学术诚信
- 自动识别小初高学段、学科、知识点、题型和考试关联
- 支持官方公开资源索引建议、原创变式题、错因卡和复习闭环

## 可视化互动学习增强

新增插件工具集 `feynman_super_tutor`：

- `feynman_assess_visual_need`：判断是否需要图示或互动 H5。
- `feynman_generate_interactive_h5_brief`：生成聚焦一个知识点的互动素材需求说明。
- `feynman_create_interactive_h5`：生成本地独立 H5 小实验，内置一次函数、二次函数、浮力、受力分析、电路、化学粒子等模板。
- `feynman_check_visual_asset`：检查页面是否具备移动端、交互、反馈、回讲任务和安全红线。
- `feynman_list_visual_assets`：查看已生成的本地视觉学习素材记录。

重要边界：H5 生成后仍必须先做浏览器预览、移动端宽度检查、学科正确性复核和公网 200 验证，才能把链接发给学生。视觉素材不是最终答案，而是帮助学生重新讲清楚的脚手架。

## 使用示例

```text
带我用费曼法学初二物理浮力，必要时给我一个能操作的小实验。
```

```text
我给你讲一遍二次函数，你找漏洞；如果我卡在图像变化上，请做一个互动页让我拖动参数。
```

```text
这道题不要直接给答案，先问我。
```

```text
把这篇材料拆成学习路线，然后带我学第一部分。
```

```text
我是老师，帮我设计一组能暴露学生误区的课堂追问。
```

## 文件说明

- `SKILL.md`：主安装入口，适合直接发给智能体安装。
- `plugins/feynman_super_tutor/`：学习档案、材料话题地图、视觉判断、互动 H5 生成和静态质检工具。
- `references/learning-framework.md`：学习系统框架。
- `references/visual-interactive-learning.md`：可视化互动增强设计与质量标准。
- `references/china-k12-resource-policy.md`：中国中小学正版资源与版权边界。
- `templates/`：学习卡、错因卡与 H5 需求模板。
- `scripts/acceptance.py`：发布前验收脚本。

## 版权与合规

本项目可帮助用户学习其合法提供或公开授权的资料，但不提供盗版教材、盗版教辅、付费题库全文抓取或绕过平台限制的能力。

## 致谢

本项目吸收并产品化改造了开源项目 [koukekoukej-glitch/feynman-tutor](https://github.com/koukekoukej-glitch/feynman-tutor) 的核心理念。原项目采用 MIT 许可证。


## 使用边界

本工具的核心卖点就是面向中国小初高学生的学科提分训练与 AI 私教陪伴：围绕教材、考试、错因、变式、复习节奏和费曼回讲，帮助学生提升理解质量、做题能力和应试表达。官方真题/样题必须保留可核验来源；无法核验时生成原创模拟题或考试风格变式。
