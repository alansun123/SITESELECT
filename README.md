# SITESELECT

餐饮细分行业智能选址工具（Local-first + 高德地图开放平台）。

本项目面向连锁餐饮企业选址团队，支持茶饮、冰激凌、甜点、烘焙、肉饼、高端面馆等业态的候选点位评估、竞品分析、可达性分析与选址报告输出。

---

## 1. 项目目标

- 用数据替代经验驱动选址决策
- 缩短选址评估周期
- 降低误选址风险
- 建立可复盘、可解释的标准化流程

详见：
- `docs/PRD_餐饮选址工具_高德API_本地部署_V1.md`
- `docs/附件A_研发任务拆解与排期_附件B_数据库表结构草案.md`

---

## 2. 当前仓库内容

```text
.
├── docs/
│   ├── PRD_餐饮选址工具_高德API_本地部署_V1.md
│   └── 附件A_研发任务拆解与排期_附件B_数据库表结构草案.md
├── sql/
│   ├── init/
│   │   ├── 000_create_extensions.sql
│   │   └── 001_schema.sql
│   └── 附件B_数据库表结构_PostgreSQL_PostGIS_SQL_V1.sql
└── docker-compose.sitepilot.yml
```

---

## 3. 技术方案（MVP）

- **部署方式**：本地笔记本（Local-first）
- **数据库**：PostgreSQL 16 + PostGIS 3.4
- **地图数据**：高德地图开放平台 API（POI、地理编码、路径规划）
- **接口服务（建议）**：FastAPI
- **前端（建议）**：React / Next.js

> 当前仓库已提供数据库与初始化脚本，可直接启动。

---

## 4. 快速启动（数据库）

### 4.1 环境要求

- Docker
- Docker Compose（或 `docker compose`）

### 4.2 启动

```bash
docker compose -f docker-compose.sitepilot.yml up -d
```

### 4.3 连接信息

- PostgreSQL
  - Host: `localhost`
  - Port: `5432`
  - DB: `sitepilot`
  - User: `sitepilot`
  - Password: `sitepilot123`

- Adminer（可视化）
  - URL: `http://localhost:8080`

### 4.4 停止

```bash
docker compose -f docker-compose.sitepilot.yml down
```

如需清空数据卷：

```bash
docker compose -f docker-compose.sitepilot.yml down -v
```

---

## 5. 数据库说明

初始化顺序（容器首次启动时自动执行）：

1. `sql/init/000_create_extensions.sql`
2. `sql/init/001_schema.sql`

主要数据实体：

- 项目：`projects`
- 候选点位：`site_candidates`
- 竞品：`competitors`
- 评分模板：`score_templates`
- 评分结果：`site_scores`
- 报告：`reports`
- 流程日志：`workflow_logs`
- 审计日志：`audit_logs`
- 高德缓存：`amap_poi_cache`, `amap_route_cache`

---

## 6. 业态支持（V1）

- 茶饮（`tea`）
- 冰激凌（`icecream`）
- 甜点（`dessert`）
- 烘焙（`bakery`）
- 肉饼（`meatpie`）
- 高端面馆（`noodle_premium`）

---

## 7. 开发建议（下一步）

1. 增加 `backend/`（FastAPI）与 `frontend/`（Next.js）目录
2. 增加 `.env.example`（高德 Key、数据库连接）
3. 增加 `Makefile`：`up/down/logs/reset`
4. 增加最小接口：
   - 候选点位 CRUD
   - 单点评分 / 批量评分
   - 报告生成

---

## 8. 注意事项

- 生产环境请更换默认数据库密码
- 高德 API Key 不要提交到仓库
- 缓存表建议设置 TTL 清理任务

---

## 9. License

暂未指定（默认保留所有权利）。
