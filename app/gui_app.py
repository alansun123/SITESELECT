from pathlib import Path
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.siteselect.cli import load_rows, score_rows, render_report, DEFAULT_WEIGHTS

st.set_page_config(page_title="SITESELECT", layout="wide")

st.title("SITESELECT · GUI-first MVP")
st.caption("餐饮选址分析（GUI 主入口，CLI 为辅助）")

with st.sidebar:
    st.header("流程")
    step = st.radio(
        "导航",
        ["1) 项目定义", "2) 数据导入", "3) 权重配置", "4) 结果与导出"],
        index=0,
    )

if "project" not in st.session_state:
    st.session_state.project = {"name": "", "category": "", "target": ""}
if "rows" not in st.session_state:
    st.session_state.rows = []
if "weights" not in st.session_state:
    st.session_state.weights = DEFAULT_WEIGHTS.copy()
if "ranked" not in st.session_state:
    st.session_state.ranked = []

if step.startswith("1"):
    st.subheader("项目定义")
    st.session_state.project["name"] = st.text_input("项目名称", st.session_state.project["name"])
    st.session_state.project["category"] = st.text_input("业态", st.session_state.project["category"])
    st.session_state.project["target"] = st.text_input("目标客群", st.session_state.project["target"])
    st.success("已保存项目基础信息")

elif step.startswith("2"):
    st.subheader("数据导入")
    uploaded = st.file_uploader("上传候选点 CSV", type=["csv"])
    if uploaded:
        tmp = Path("/tmp/siteselect_uploaded.csv")
        tmp.write_bytes(uploaded.read())
        rows = load_rows(str(tmp))
        required = {"name", "rent_monthly", "foot_traffic_index", "competition_count", "distance_to_target_m"}
        if not rows:
            st.error("CSV 为空")
        else:
            missing = required - set(rows[0].keys())
            if missing:
                st.error(f"缺少字段: {', '.join(sorted(missing))}")
            else:
                st.session_state.rows = rows
                st.success(f"导入成功：{len(rows)} 条")
                st.dataframe(rows, use_container_width=True)

elif step.startswith("3"):
    st.subheader("权重配置")
    w = st.session_state.weights
    w["rent_monthly"] = st.slider("租金权重", 0.0, 1.0, float(w["rent_monthly"]), 0.01)
    w["foot_traffic_index"] = st.slider("客流权重", 0.0, 1.0, float(w["foot_traffic_index"]), 0.01)
    w["competition_count"] = st.slider("竞争权重", 0.0, 1.0, float(w["competition_count"]), 0.01)
    w["distance_to_target_m"] = st.slider("距离权重", 0.0, 1.0, float(w["distance_to_target_m"]), 0.01)

    total = sum(w.values())
    st.info(f"当前权重总和: {total:.2f}")
    if st.button("恢复默认权重"):
        st.session_state.weights = DEFAULT_WEIGHTS.copy()
        st.rerun()

else:
    st.subheader("结果与导出")
    if not st.session_state.rows:
        st.warning("请先在“数据导入”步骤上传 CSV")
    else:
        ranked = score_rows(st.session_state.rows, st.session_state.weights)
        st.session_state.ranked = ranked

        top_n = st.slider("Top N", 1, min(10, len(ranked)), min(5, len(ranked)))

        st.markdown("### 推荐结论")
        st.success(f"Top1 推荐：{ranked[0]['name']}（score={ranked[0]['score']}）")

        st.markdown("### 排名明细")
        st.dataframe(ranked, use_container_width=True)

        if st.button("导出 HTML 报告"):
            out = Path("output/report.html")
            render_report(ranked, top_n, str(out))
            st.success(f"已导出：{out}")
            st.markdown(f"- 本地路径：`{out}`")
