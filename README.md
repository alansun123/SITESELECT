# SITESELECT (MVP-first)

5天可落地的餐饮选址工具：**先交付结果、先验证付费**。

> 方向：本地优先（Local-first）、CLI 优先、报告优先。  
> 现阶段不追求“全栈平台”，先把“可收费的选址分析服务”跑通。

## 核心原则

- **先赚钱，再工程化**：优先支持“99元/次人工咨询交付”
- **先本地跑通**：不依赖复杂服务编排
- **先稳定输出**：一键生成 HTML 报告
- **API 可选增强**：高德作为增强数据源，不是硬依赖

---

## MVP 范围（5天）

### ✅ 包含
- CLI 命令行分析
- 本地 CSV/JSON 数据输入
- 基础评分模型（可配置权重）
- HTML 报告生成

### ❌ 暂不包含
- Web 前端
- 用户系统/支付系统
- PostgreSQL / Redis / Serverless
- PDF/Excel 自动导出（可后续加）

---

## 仓库结构

```text
.
├── PRD.md
├── src/
│   └── siteselect/
│       ├── __init__.py
│       └── cli.py
├── templates/
│   └── report.html.tpl
├── examples/
│   ├── candidates.example.csv
│   └── weights.example.json
└── output/
    └── (生成的报告)
```

---

## 快速开始

### 1) 准备数据

复制示例数据：

```bash
cp examples/candidates.example.csv ./candidates.csv
cp examples/weights.example.json ./weights.json
```

### 2) 运行分析

```bash
python3 src/siteselect/cli.py analyze \
  --input ./candidates.csv \
  --weights ./weights.json \
  --top 5 \
  --out ./output/report.html
```

### 3) 打开报告

```bash
open ./output/report.html
```

---

## 数据字段（MVP）

输入 CSV 最少包含以下列：

- `name`：候选点名称
- `rent_monthly`：月租（元）
- `foot_traffic_index`：客流指数（0-100）
- `competition_count`：周边同类店数量
- `distance_to_target_m`：距目标客群中心点距离（米）

---

## 评分逻辑（当前版本）

- 租金越低越好
- 客流越高越好
- 竞争越少越好
- 距离越近越好

最终输出 `score`（0-100）与排序。

---

## 商业化建议（与MVP配套）

- 开源工具免费发布
- 付费交付：人工复核 + 选址建议（99元/次）
- 客户拿到的是“报告 + 推荐理由”，不是让客户自己学工具

---

## 未来迭代（Phase 2）

- 高德 API 接入（POI、路径、通达性）
- FastAPI 服务化
- Web 界面
- PostGIS 空间分析

---

## License

暂未指定（默认保留所有权利）。
