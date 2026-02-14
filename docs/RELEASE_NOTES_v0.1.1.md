# RELEASE NOTES v0.1.1

## 发布定位
v0.1.1 是对 v0.1.0 的**业务工作流收口版**：补齐真实业务录入字段、强化跨平台 CI 稳定性、增强报告可交付性。

## 本版亮点
- Step 1 业务字段落地：友商品牌、国家、城市、行政区、行业分类（含必填校验）
- GUI 支持项目草稿导入/导出（JSON）
- 评分输入链路接入项目上下文，结果页可见业务信息
- HTML 报告新增“项目上下文”模块
- 排名表新增城市/行政区/行业分类列
- 跨平台 CI 稳定化：统一 `requirements.txt + scripts/ci_smoke.py`

## 关键改进
- 降低跨平台回归风险：去除 workflow 中 POSIX/Windows 分叉命令
- 文档与执行命令对齐：安装方式统一为 `pip install -r requirements.txt`
- 报告可读性提升：Top 推荐附解释摘要，便于客户沟通

## 兼容性与验证
- 本地验证：
  - `python -m py_compile app/gui_app.py src/siteselect/cli.py scripts/ci_smoke.py`
  - `python scripts/ci_smoke.py`
  - `streamlit run app/gui_app.py`（短启停验证）
- 目标运行环境：macOS + Windows（通过 GitHub Actions 进行跨平台校验）

## 已知限制
- 项目上下文目前主要用于报告与展示，不参与独立业务规则引擎（后续可扩展）
- 报告导出仍以 HTML 为主，PDF/Excel 待后续版本

## 升级建议
从 v0.1.0 升级到 v0.1.1：
```bash
git pull
python3 -m pip install -r requirements.txt
```
