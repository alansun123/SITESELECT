# DEMO SCRIPT (v0.1.1)

## 目标
5 分钟演示 SITESELECT 的 GUI-first 业务工作流：项目定义（含市场上下文）→ 导入数据 → 调权重 → 出结论 → 导出报告。

## 演示前准备
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/gui_app.py
```

## 演示流程（建议话术）
1. **项目定义（业务必填）**
   - 输入：我方品牌/项目名称、友商品牌（可多选）、国家、城市、行政区、行业分类。
   - 推荐补充：子分类、门店模型、目标客群。
   - 强调：这一步用于固定真实业务上下文，后续会进入结果页与报告。

2. **数据导入**
   - 上传 `examples/candidates.example.csv`。
   - 强调：系统会做字段与数值校验，不合规会给明确提示。

3. **权重配置**
   - 调整“客流/租金/竞争/距离”权重。
   - 强调：可一键归一化为 1.00，保证解释一致性。

4. **结果与导出**
   - 展示 Top1 推荐与完整排名。
   - 展示“项目上下文”（项目/友商/国家/城市/行政区/行业分类）。
   - 点击“生成 HTML 报告”并下载。
   - 强调：报告已包含业务上下文，可直接用于客户沟通与初判。

## 备用演示（CLI）
```bash
python3 src/siteselect/cli.py analyze \
  --input examples/candidates.example.csv \
  --weights examples/weights.example.json \
  --top 5 \
  --out output/report.html
```
