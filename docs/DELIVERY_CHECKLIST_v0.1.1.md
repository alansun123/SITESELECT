# DELIVERY CHECKLIST v0.1.1

## 1) 代码与文档
- [x] GUI Step1 业务字段（友商/国家/城市/行政区/行业分类）
- [x] Step1 必填校验与提示
- [x] 项目草稿导入/导出（JSON）
- [x] 项目上下文进入评分结果展示链路
- [x] HTML 报告包含项目上下文与新增业务列
- [x] `docs/DEMO_SCRIPT.md` 更新
- [x] `docs/RELEASE_NOTES_v0.1.1.md` 新增

## 2) 运行与验证
- [x] `python -m py_compile app/gui_app.py src/siteselect/cli.py scripts/ci_smoke.py`
- [x] `python scripts/ci_smoke.py`
- [x] `python src/siteselect/cli.py analyze --input examples/candidates.example.csv --weights examples/weights.example.json --top 3 --out output/report_context_check.html`
- [x] 报告内容检查（项目上下文/城市/行政区/行业分类字段）

## 3) 交付物
- [x] GUI 应用：`app/gui_app.py`
- [x] 核心逻辑：`src/siteselect/cli.py`
- [x] 报告模板：`templates/report.html.tpl`
- [x] 演示脚本：`docs/DEMO_SCRIPT.md`
- [x] 发布说明：`docs/RELEASE_NOTES_v0.1.1.md`

## 4) 发布后建议
- [ ] 推送远端并触发 GitHub Actions（Windows + Ubuntu）
- [ ] 补一轮 5 分钟真人演示录屏
- [ ] 准备 v0.1.1 tag
