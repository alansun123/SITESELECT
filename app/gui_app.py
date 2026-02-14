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

COMMON_COMPETITOR_BRANDS = [
    "蜜雪冰城",
    "霸王茶姬",
    "喜茶",
    "奈雪的茶",
    "茶百道",
    "瑞幸咖啡",
    "星巴克",
]
INDUSTRY_OPTIONS = [
    "现制茶饮",
    "咖啡",
    "快餐简餐",
    "中式正餐",
    "西式餐饮",
    "烘焙甜品",
    "小吃夜宵",
    "其他",
]


st.set_page_config(page_title="SITESELECT", layout="wide")

st.title("SITESELECT · GUI-first MVP")
st.caption("餐饮选址分析（GUI 主入口，CLI 为辅助）")


if "project" not in st.session_state:
    st.session_state.project = {
        "name": "",
        "category": "",
        "target": "",
        "competitor_brands": ["蜜雪冰城", "霸王茶姬"],
        "country": "中国",
        "city": "",
        "district": "",
        "industry_category": "现制茶饮",
    }
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
if "analysis_input" not in st.session_state:
    st.session_state.analysis_input = {}


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


def _project_validation_errors(project):
    required_text_fields = {
        "项目名称": project["name"],
        "国家": project["country"],
        "城市": project["city"],
        "行政区": project["district"],
    }
    errors = []

    for label, value in required_text_fields.items():
        if not str(value).strip():
            errors.append(f"{label}不能为空")

    if not project.get("competitor_brands"):
        errors.append("友商品牌至少选择/填写 1 个")

    if project.get("industry_category") not in INDUSTRY_OPTIONS:
        errors.append("行业分类不在支持范围内，请重新选择")

    return errors


def _build_scoring_input(rows, project):
    context = {
        "project_name": project["name"].strip(),
        "category": project["category"].strip(),
        "target": project["target"].strip(),
        "competitor_brands": project["competitor_brands"],
        "country": project["country"].strip(),
        "city": project["city"].strip(),
        "district": project["district"].strip(),
        "industry_category": project["industry_category"],
    }

    scoring_rows = []
    for row in rows:
        merged = dict(row)
        merged.update(context)
        scoring_rows.append(merged)

    return {"project_context": context, "candidates": scoring_rows}


def _completion_state():
    project_errors = _project_validation_errors(st.session_state.project)
    project_ok = len(project_errors) == 0
    data_ok = bool(st.session_state.rows) and not st.session_state.import_errors
    weights_total = sum(st.session_state.weights.values())
    weights_ok = abs(weights_total - 1.0) < 1e-6
    return project_ok, data_ok, weights_ok, weights_total, project_errors


project_ok, data_ok, weights_ok, weights_total, project_errors = _completion_state()

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
    st.caption("请先完整填写真实业务字段，后续评分与结果展示会引用这些上下文")

    p = st.session_state.project
    p["name"] = st.text_input("我方品牌/项目名称（必填）", p["name"], help="例如：XX 茶饮华东拓店项目")

    c1, c2 = st.columns(2)
    with c1:
        p["country"] = st.text_input("国家（必填）", p["country"], help="默认中国，可按出海场景修改")
        p["city"] = st.text_input("城市（必填）", p["city"], placeholder="例如：上海")
    with c2:
        p["district"] = st.text_input("行政区（必填）", p["district"], placeholder="例如：浦东新区")
        p["industry_category"] = st.selectbox(
            "行业分类（必选）",
            INDUSTRY_OPTIONS,
            index=INDUSTRY_OPTIONS.index(p["industry_category"]) if p["industry_category"] in INDUSTRY_OPTIONS else 0,
            help="用于界定竞品范围与评分解释口径",
        )

    p["competitor_brands"] = st.multiselect(
        "友商品牌（至少 1 个）",
        options=COMMON_COMPETITOR_BRANDS,
        default=p["competitor_brands"],
        help="可多选常见友商；若不在列表可在下方补充",
    )
    extra_brands = st.text_input("补充友商品牌（可选）", placeholder="多个请用逗号分隔，例如：沪上阿姨, CoCo")
    if extra_brands.strip():
        extra = [x.strip() for x in extra_brands.replace("，", ",").split(",") if x.strip()]
        p["competitor_brands"] = sorted(set(p["competitor_brands"] + extra))

    p["category"] = st.text_input("业态（可选）", p["category"], placeholder="例如：现制茶饮-外带")
    p["target"] = st.text_input("目标客群（可选）", p["target"], placeholder="例如：白领 + 社区家庭")

    if project_errors:
        st.warning("请修复以下问题后继续：")
        for err in project_errors:
            st.write(f"- {err}")
    else:
        st.success("项目业务字段已完整保存，可进入下一步。")

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
        st.warning("请先完成步骤 1：补全项目业务字段。")
        st.stop()
    if not data_ok:
        st.warning("请先完成步骤 2：导入并通过校验的 CSV 数据。")
        st.stop()
    if not weights_ok:
        st.warning("请先完成步骤 3：将权重总和调整为 1.00。")
        st.stop()

    analysis_input = _build_scoring_input(st.session_state.rows, st.session_state.project)
    st.session_state.analysis_input = analysis_input

    ranked = score_rows(analysis_input["candidates"], st.session_state.weights)
    st.session_state.ranked = ranked

    top_n = st.slider("Top N", 1, min(10, len(ranked)), min(5, len(ranked)))

    st.markdown("### 项目上下文")
    st.json(analysis_input["project_context"], expanded=False)

    st.markdown("### 推荐结论")
    st.success(f"Top1 推荐：{ranked[0]['name']}（score={ranked[0]['score']}）")

    st.markdown("### 排名明细")
    visible_cols = [
        "name",
        "score",
        "country",
        "city",
        "district",
        "industry_category",
        "competitor_brands",
        "rent_monthly",
        "foot_traffic_index",
        "competition_count",
        "distance_to_target_m",
    ]
    st.dataframe([{k: r.get(k) for k in visible_cols} for r in ranked], use_container_width=True)

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
