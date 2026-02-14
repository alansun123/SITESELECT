# SITESELECT MVP Test Cases (GUI-first)

## TC-HP-01 CLI Happy Path
- **目标**: 验证核心分析链路可用。
- **前置**: 使用 `examples/candidates.example.csv` + `examples/weights.example.json`。
- **步骤**:
  1. 执行 CLI analyze。
  2. 检查 stdout 与输出 HTML。
- **期望**:
  - 返回码 0。
  - 输出 `分析完成` 和 Top1。
  - 目标 HTML 文件存在。

## TC-HP-02 GUI Happy Path（手工）
- **目标**: 验证 GUI 四步流程闭环。
- **步骤**:
  1. 启动 `streamlit run app/gui_app.py`。
  2. Step1 填写项目。
  3. Step2 上传合法 CSV。
  4. Step3 调整权重。
  5. Step4 查看推荐并导出报告。
- **期望**:
  - 导入成功、排名正常、可导出 HTML。

## TC-EC-01 Empty CSV
- **输入**: 仅表头，无数据行。
- **步骤**: CLI analyze。
- **期望**:
  - 失败退出（非0）。
  - 明确提示“输入数据为空”。

## TC-EC-02 Missing Required Field
- **输入**: 缺少 `distance_to_target_m` 列。
- **步骤**: CLI analyze。
- **期望（产品）**:
  - 友好报错指出缺失字段。
- **当前实际**:
  - 抛 `KeyError` traceback（需修复）。

## TC-EC-03 Invalid Numerics
- **输入**: 数值列包含 `abc` / `N/A` / `xyz`。
- **步骤**: CLI analyze。
- **期望（产品）**:
  - 至少有告警或拒绝非法值。
- **当前实际**:
  - 成功执行，非法值按 `0.0` 参与计算（静默降级）。

## TC-EC-04 Extreme Weights (Very Large)
- **输入**: 全部权重设为 `10`。
- **步骤**: CLI analyze。
- **期望（产品）**:
  - 限制权重范围或归一化后计算。
- **当前实际**:
  - 正常输出，但分数异常放大（>100）。

## TC-EC-05 Extreme Weights (Negative)
- **输入**: `rent_monthly=-1`，其余0。
- **步骤**: CLI analyze。
- **期望（产品）**:
  - 拒绝负权重。
- **当前实际**:
  - 正常执行并产生非直觉结果。

## TC-EC-06 GUI Dependency Readiness
- **目标**: GUI 可执行前置依赖检查。
- **步骤**: `python3 -c "import streamlit"`
- **期望**:
  - 可导入。
- **当前实际**:
  - 环境缺少 streamlit（阻断 GUI 本地验证）。