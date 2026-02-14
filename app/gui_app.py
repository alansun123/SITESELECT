from pathlib import Path
import sys
import tempfile
from datetime import datetime

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.siteselect.cli import load_rows, score_rows, render_report, DEFAULT_WEIGHTS

REQUIRED_FIELDS = {
    "name",
    "rent_monthly",
    "foot_traffic_index",
    "competition_count",
    "distance_to_target_m",
}
NUMERIC_FIELDS = [
    "rent_monthly",
    "foot_traffic_index",
    "competition_count",
    "distance_to_target_m",
]


st.set_page_config(page_title="SITESELECT", layout="wide")

st.title("SITESELECT · GUI-first MVP")
st.caption("餐饮选址分析（GUI 主入口，CLI 为辅助）")


if "project" not in st.session_state:
    st.session_state.project = {"name": "", "category": "", "target": ""}
if "rows" not in st.session_state:
    st.session_state.rows = []
if "weights" not in st.session_state:
    st.session_state.weights = DEFAULT_WEIGHTS.copy()
if "ranked" not in st.session_state:
    st.session_state.ranked = []
if "import_errors" not in st.session_state:
    st.session_state.import_errors = []
if "import_source" not in st.session_state:
    st.session_state.import_source = ""


def _safe_float(value):
    try:
        return float(value)
    except Exception:
        return None


def _validate_rows(rows):
    errors = []
    if not rows:
        return ["CSV 为空，至少需要 1 条候选点记录"]

    missing = REQUIRED_FIELDS - set(rows[0].keys())
    if missing:
        return [f"缺少必填字段: {', '.join(sorted(missing))}"]

    for idx, row in enumerate(rows, start=2):  # CSV header is row 1
        for field in NUMERIC_FIELDS:
            fv = _safe_float(row.get(field))
            if fv is None:
                errors.append(f"第 {idx} 行字段 {field} 不是有效数字: {row.get(field)!r}")

    return errors


def _completion_state():
    project_ok = bool(st.session_state.project["name"].strip())
    data_ok = bool(st.session_state.rows) and not st.session_state.import_errors
    weights_total = sum(st.session_state.weights.values())
    weights_ok = abs(weights_total - 1.0) < 1e-6
    return project_ok, data_ok, weights_ok, weights_total


project_ok, data_ok, weights_ok, weights_total = _completion_state()

with st.sidebar:
    st.header("流程")
    step = st.radio(
        "导航（4 步）",
        ["1) 项目定义", "2) 数据导入", "3) 权重配置", "4) 结果与导出"],
        index=0,
    )

    st.markdown("---")
    st.caption("完成状态")
    st.write(f"1) 项目定义: {'✅' if project_ok else '⬜'}")
    st.write(f"2) 数据导入: {'✅' if data_ok else '⬜'}")
    st.write(f"3) 权重配置: {'✅' if weights_ok else '⚠️'}")


if step.startswith("1"):
    st.subheader("步骤 1/4 · 项目定义")
    st.session_state.project["name"] = st.text_input("项目名称（必填）", st.session_state.project["name"])
    st.session_state.project["category"] = st.text_input("业态", st.session_state.project["category"])
    st.session_state.project["target"] = st.text_input("目标客群", st.session_state.project["target"])

    if not st.session_state.project["name"].strip():
        st.warning("请填写项目名称后继续。")
    else:
        st.success("项目基础信息已保存。")

elif step.startswith("2"):
    st.subheader("步骤 2/4 · 数据导入")
    uploaded = st.file_uploader("上传候选点 CSV", type=["csv"])

    if uploaded:
        with tempfile.NamedTemporaryFile(prefix="siteselect_", suffix=".csv", delete=False) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = Path(tmp.name)

        try:
            rows = load_rows(str(tmp_path))
            errors = _validate_rows(rows)
            if errors:
                st.session_state.rows = []
                st.session_state.import_errors = errors
                st.error("导入失败，请修复以下问题后重试：")
                for msg in errors[:8]:
                    st.write(f"- {msg}")
                if len(errors) > 8:
                    st.caption(f"其余 {len(errors) - 8} 个问题已省略")
            else:
                st.session_state.rows = rows
                st.session_state.import_errors = []
                st.session_state.import_source = uploaded.name
                st.success(f"导入成功：{len(rows)} 条（文件：{uploaded.name}）")
                st.dataframe(rows, use_container_width=True)
        finally:
            tmp_path.unlink(missing_ok=True)

    if st.session_state.rows:
        st.info(f"当前已载入 {len(st.session_state.rows)} 条候选点数据")

elif step.startswith("3"):
    st.subheader("步骤 3/4 · 权重配置")
    st.caption("建议权重总和为 1.00，以保证评分可解释性")

    w = st.session_state.weights
    w["rent_monthly"] = st.slider("租金权重", 0.0, 1.0, float(w["rent_monthly"]), 0.01)
    w["foot_traffic_index"] = st.slider("客流权重", 0.0, 1.0, float(w["foot_traffic_index"]), 0.01)
    w["competition_count"] = st.slider("竞争权重", 0.0, 1.0, float(w["competition_count"]), 0.01)
    w["distance_to_target_m"] = st.slider("距离权重", 0.0, 1.0, float(w["distance_to_target_m"]), 0.01)

    total = sum(w.values())
    if abs(total - 1.0) < 1e-6:
        st.success(f"当前权重总和: {total:.2f}（可用于分析）")
    else:
        st.warning(f"当前权重总和: {total:.2f}，建议调整至 1.00")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("恢复默认权重"):
            st.session_state.weights = DEFAULT_WEIGHTS.copy()
            st.rerun()
    with c2:
        if st.button("一键归一化为 1.00"):
            total = sum(st.session_state.weights.values())
            if total > 0:
                st.session_state.weights = {
                    k: round(v / total, 4) for k, v in st.session_state.weights.items()
                }
                st.rerun()

else:
    st.subheader("步骤 4/4 · 结果与导出")

    if not project_ok:
        st.warning("请先完成步骤 1：至少填写项目名称。")
        st.stop()
    if not data_ok:
        st.warning("请先完成步骤 2：导入并通过校验的 CSV 数据。")
        st.stop()
    if not weights_ok:
        st.warning("请先完成步骤 3：将权重总和调整为 1.00。")
        st.stop()

    ranked = score_rows(st.session_state.rows, st.session_state.weights)
    st.session_state.ranked = ranked

    top_n = st.slider("Top N", 1, min(10, len(ranked)), min(5, len(ranked)))

    st.markdown("### 推荐结论")
    st.success(f"Top1 推荐：{ranked[0]['name']}（score={ranked[0]['score']}）")

    st.markdown("### 排名明细")
    st.dataframe(ranked, use_container_width=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_out = Path("output") / f"report_{ts}.html"

    if st.button("生成 HTML 报告"):
        render_report(ranked, top_n, str(default_out))
        st.success(f"报告已生成：{default_out}")

    latest_report = sorted(Path("output").glob("report_*.html"))
    if latest_report:
        report_path = latest_report[-1]
        st.caption(f"当前可下载报告：{report_path.name}")
        st.download_button(
            "下载 HTML 报告",
            data=report_path.read_text(encoding="utf-8"),
            file_name=report_path.name,
            mime="text/html",
        )
