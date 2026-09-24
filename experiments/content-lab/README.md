# Malachi 内容实验室

帮助中文商业作者回答三个问题：读者为什么停下来，读完能带走什么，下次怎样根据真实反馈改进。

v0.1 是可运行的编辑辅助原型，包含规则检查、编辑提示词和发布后复盘。不是经过训练的爆款预测模型，不保证浏览量。没有账号连接和自动发布。

## 五分钟试用

需要 Python 3.10 或以上，仅用标准库。从当前目录运行：

```bash
python3 content_lab.py review examples/draft.json
python3 content_lab.py brief examples/draft.json --output private/editor-brief.md
python3 content_lab.py metrics examples/snapshot.json
python3 content_lab.py compare examples/snapshot.json examples/history.json
python3 -m unittest discover -s tests -v
```

brief 的输出交给你正在使用的 AI 或编辑，得到三个标题、两个首屏、修改方案与证据待办。它不会自行调用模型。演示里故意保留了一个未兑现承诺，review 应当将它拦下。

## 日常使用

1. 复制 examples/draft.json 到 private/，填入稿件和读者问题。
2. 列出关键事实与读者交付承诺。claims 的状态为 verified、author_report、assumption 或 unknown；framing 为 fact、attributed、hypothesis 或 question。已核事实要写 verification_note。
3. 运行 review，解决 blocks。查看首屏与数字片段，补齐遗漏；程序不能自动认定来源真伪。
4. 运行 brief，取得编辑任务，再由模型或人工生成候选版本。审阅当前文字后，将 review 给出的 draft_sha256 填到 annotations.reviewed_sha256，确认 claims_complete 与 promises_complete。
5. 采用 rubric.md 逐项评议。缺项保留空值，高分不能抵消缺证据。
6. 选定版本后由作者自行发布；保存发布后 24 小时、72 小时的同口径快照。使用 compare 复盘。

## 数据格式

draft.json 的 ratings 可省略，但不会生成总评均分。每项是 score 0—4 和 note。annotations 中的 SHA256 与正文标题绑定，改字后需要重审。

快照的必填对照字段：id、author、platform、format、topic、length_band、window_hours、distribution、metric_basis、measurement_method、published_at、observed_at、views。时间采用带时区的 ISO 8601。distribution 为 organic、paid 或 unknown；metric_basis 为 post_views、article_views 或 video_views。

likes、replies、reposts、bookmarks、follows、qualified_inquiries 都可为 null。只在点赞、评论、转发全部已知时计算 public_actions；不把收藏等缺项填为零。counts_approximate 用于注明页面四舍五入的数字。

同一帖子不能重复进入同一基线。目标文章不能作为自身基线；比目标更晚的文章被排除。unknown 分发来源不做同类倍数比较。每个指标有至少 5 个可用历史值时才显示相对中位数；这仍不是显著性或因果证明。

## 学习素材如何选

同时看表现好、一般和差的作品；优先同作者、同题材、同格式的对照。记录开头、具体场景、证据、交付物、转发理由与拍摄/配图，而不只抄标题。第三方全文留在有权使用的私有研究环境，公开只放链接和自己写的分析。

参见 [模型说明](MODEL_CARD.md)、[编辑任务](prompts/editor.md)、[原始工具来源](SOURCES.md)。

## 项目边界

本目录是独立实验工具，不修改雷达站案例库的审定流程。没有假装完成客户试验或传播实验。当前结果只证明程序按设计处理输入；真实写作效果需要后续文章验证。

本目录的新代码和原创方法以 MIT License 提供；不改变仓库其他目录及第三方内容的权利安排。
