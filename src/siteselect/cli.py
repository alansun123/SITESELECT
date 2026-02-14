#!/usr/bin/env python3
import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path

DEFAULT_WEIGHTS = {
    "rent_monthly": 0.30,
    "foot_traffic_index": 0.35,
    "competition_count": 0.20,
    "distance_to_target_m": 0.15,
}

LOWER_BETTER = {"rent_monthly", "competition_count", "distance_to_target_m"}
HIGHER_BETTER = {"foot_traffic_index"}


def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def minmax(values):
    mn, mx = min(values), max(values)
    if mn == mx:
        return [1.0 for _ in values]
    return [(v - mn) / (mx - mn) for v in values]


def normalize(rows, field):
    values = [to_float(r[field]) for r in rows]
    norm = minmax(values)
    if field in LOWER_BETTER:
        norm = [1 - x for x in norm]
    return norm


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_weights(path):
    if not path:
        return DEFAULT_WEIGHTS
    with open(path, "r", encoding="utf-8") as f:
        w = json.load(f)
    return {**DEFAULT_WEIGHTS, **w}


def score_rows(rows, weights):
    fields = list(DEFAULT_WEIGHTS.keys())
    normalized = {field: normalize(rows, field) for field in fields}

    for i, row in enumerate(rows):
        s = 0.0
        for field in fields:
            s += normalized[field][i] * float(weights[field])
        row["score"] = round(s * 100, 2)

    return sorted(rows, key=lambda r: r["score"], reverse=True)


def render_report(rows, top_n, output):
    template_path = Path(__file__).resolve().parents[2] / "templates" / "report.html.tpl"
    tpl = template_path.read_text(encoding="utf-8")

    top_items = []
    for r in rows[:top_n]:
        top_items.append(f"<li><b>{r['name']}</b>（总分 {r['score']}）</li>")

    table_rows = []
    for i, r in enumerate(rows, start=1):
        table_rows.append(
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{r['name']}</td>"
            f"<td>{r['score']}</td>"
            f"<td>{r['rent_monthly']}</td>"
            f"<td>{r['foot_traffic_index']}</td>"
            f"<td>{r['competition_count']}</td>"
            f"<td>{r['distance_to_target_m']}</td>"
            "</tr>"
        )

    html = (
        tpl.replace("{{generated_at}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        .replace("{{top_n}}", str(top_n))
        .replace("{{top_list_items}}", "\n".join(top_items))
        .replace("{{table_rows}}", "\n".join(table_rows))
    )

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def cmd_analyze(args):
    rows = load_rows(args.input)
    if not rows:
        raise SystemExit("输入数据为空")

    weights = load_weights(args.weights)
    ranked = score_rows(rows, weights)
    render_report(ranked, args.top, args.out)

    print(f"分析完成：{args.out}")
    print(f"Top1: {ranked[0]['name']} (score={ranked[0]['score']})")


def build_parser():
    p = argparse.ArgumentParser(description="SITESELECT MVP CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="运行选址分析并输出HTML报告")
    a.add_argument("--input", required=True, help="候选点 CSV 文件路径")
    a.add_argument("--weights", help="权重 JSON 文件路径（可选）")
    a.add_argument("--top", type=int, default=5, help="报告展示 Top N")
    a.add_argument("--out", default="output/report.html", help="输出 HTML 报告路径")
    a.set_defaults(func=cmd_analyze)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
