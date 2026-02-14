# SITESELECT (GUI-first MVP)

餐饮选址工具，**GUI 是主入口**，CLI 是能力层与自动化入口。

> 目标：在 5 天内交付一个可用、可演示、可收费的 GUI 应用（并保留 CLI 能力）。

---

## 产品定位

- **主体验**：图形界面（Best Practice 交互流程）
- **辅入口**：CLI（批处理/调试/自动化）
- **交付物**：交互式评分流程 + 可读报告页面 + 可导出 HTML 报告

---

## MVP 范围（GUI-first）

### ✅ 包含
- GUI 四步流程：
  1. 项目信息（我方品牌、友商品牌、国家/城市/行政区、行业分类）
  2. 候选点导入
  3. 权重调整
  4. 结果与报告
- 候选点表格预览与校验提示
- 基础评分模型（可解释）
- 报告预览 + HTML 导出
- CLI 分析命令（保留）

### ❌ 暂不包含
- 多账号系统
- 在线支付
- 复杂 GIS 引擎
- 大规模多租户平台

---

## 仓库结构

```text
.
├── PRD.md
├── app/
│   └── gui_app.py              # GUI 主应用（Streamlit）
├── src/
│   └── siteselect/
│       ├── __init__.py
│       └── cli.py              # CLI 能力层
├── templates/
│   └── report.html.tpl
├── examples/
│   ├── candidates.example.csv
│   └── weights.example.json
└── output/
```

---

## 快速开始

## 1) 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

## 2) 启动 GUI

```bash
streamlit run app/gui_app.py
```

打开浏览器后按向导完成：导入 CSV → 调权重 → 查看排名 → 导出报告。

## 3) 使用 CLI（可选）

```bash
python3 src/siteselect/cli.py analyze \
  --input examples/candidates.example.csv \
  --weights examples/weights.example.json \
  --top 5 \
  --out output/report.html
```

---

## Best Practice 交互原则（本项目已落地）

- 明确流程导航（步骤化）
- 每一步有状态反馈与错误提示
- 关键参数可调且有默认值
- 结果页先给结论，再给细节
- 导出操作“一键可得”

---

## 下一步（Phase 2）

- 高德 API 接入（POI/通达性）
- 地图可视化页
- FastAPI 服务化
- 报告模板升级（行业版）

