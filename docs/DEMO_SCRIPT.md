# DEMO SCRIPT (v0.1.0)

## 目标
5 分钟演示 SITESELECT 的 GUI-first MVP：导入数据 → 调权重 → 出结论 → 导出报告。

## 演示前准备
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/gui_app.py
```

## 演示流程（建议话术）
1. **项目定义**
   - 输入项目名称、业态、目标客群。
   - 强调：这一步用于把分析上下文固定下来。

2. **数据导入**
   - 上传 `examples/candidates.example.csv`。
   - 强调：系统会做字段与数值校验，不合规会给明确提示。

3. **权重配置**
   - 调整“客流/租金/竞争/距离”权重。
   - 强调：可一键归一化为 1.00，保证解释一致性。

4. **结果与导出**
   - 展示 Top1 推荐与完整排名。
   - 点击“生成 HTML 报告”并下载。
   - 强调：可直接发给客户做初步决策依据。

## 备用演示（CLI）
```bash
python3 src/siteselect/cli.py analyze \
  --input examples/candidates.example.csv \
  --weights examples/weights.example.json \
  --top 5 \
  --out output/report.html
```
