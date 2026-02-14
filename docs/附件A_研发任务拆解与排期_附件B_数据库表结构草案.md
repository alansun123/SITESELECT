# 附件A：研发任务拆解与排期（12周）

## 1. 角色分工
- **产品经理（1）**：需求澄清、验收、业务规则定义
- **前端工程师（1）**：地图工作台、评分页、报告页
- **后端工程师（1）**：API编排、任务调度、权限、报表服务
- **数据/算法工程师（1）**：评分模型、数据清洗、指标校准
- **测试工程师（0.5~1）**：功能/性能/回归测试

---

## 2. 里程碑拆解（按周）

### W1-W2：基础设施与数据底座
**目标**：系统可启动，能调用高德API并落库存储

- 后端
  - [ ] 初始化项目骨架（FastAPI + SQLAlchemy/Alembic）
  - [ ] 接入高德API网关（POI/地理编码/路径规划）
  - [ ] 配置中心（.env、多Key、限流）
- 数据
  - [ ] 设计基础表（点位、POI缓存、任务日志）
  - [ ] 地址标准化与坐标系统一（GCJ-02）
- 前端
  - [ ] 地图容器与底图接入
  - [ ] 城市/关键词搜索UI
- 测试
  - [ ] API连通性用例
  - [ ] Key异常、超时、429限流场景用例

**交付物**：可检索POI并在地图展示；可入库缓存

---

### W3-W4：评分引擎与业态模板
**目标**：支持6业态基础评分

- 算法/数据
  - [ ] 评分维度实现（客群、流量、可达性、竞品、成本、场景、风险）
  - [ ] 6业态权重模板配置化
  - [ ] 风险惩罚逻辑实现
- 后端
  - [ ] 单点评分API
  - [ ] 批量评分任务API（异步）
- 前端
  - [ ] 点位评分详情页（雷达图+维度解释）
  - [ ] 业态切换与分数对比UI
- 测试
  - [ ] 评分可解释性与边界值测试

**交付物**：单点可评估，支持业态切换对比

---

### W5-W6：批量评估与候选池管理
**目标**：选址专员可批量筛点并管理流程

- 后端
  - [ ] 批量导入（Excel/CSV）
  - [ ] 点位状态流转（待评估/实勘中/通过/淘汰）
  - [ ] 筛选与排序API
- 前端
  - [ ] 批量评估页（Top N、筛选器、导出）
  - [ ] 点位状态看板
- 测试
  - [ ] 1000点批量任务稳定性测试
  - [ ] 并发任务测试

**交付物**：可批量评估、形成推荐候选池

---

### W7-W8：报告系统与审批场景
**目标**：一键导出可审批报告

- 后端
  - [ ] 报告生成服务（PDF）
  - [ ] 报告模板（审批版/简版）
- 前端
  - [ ] 报告预览页
  - [ ] 分享链接与下载
- 产品
  - [ ] 结论模板标准化（推荐/谨慎/不建议）
- 测试
  - [ ] 报告一致性测试（同输入同输出）

**交付物**：完整选址报告产出

---

### W9-W10：试点城市上线与复盘闭环
**目标**：真实业务跑通

- 业务
  - [ ] 选择1个试点城市
  - [ ] 完成≥20个点位评估
- 系统
  - [ ] 实勘回填模块（简版）
  - [ ] 模型参数手动调优入口
- 测试
  - [ ] 线上问题回归与热修复机制

**交付物**：试点数据与复盘报告

---

### W11-W12：性能优化与验收
**目标**：达到MVP验收指标

- 性能
  - [ ] 单点评分<3秒
  - [ ] 1000点批量<10分钟
- 安全
  - [ ] 权限校验、审计日志
  - [ ] 敏感信息脱敏
- 验收
  - [ ] UAT
  - [ ] 上线SOP与运维手册

**交付物**：MVP验收通过

---

## 3. 研发任务清单（按模块）

### 3.1 地图与数据采集
- [ ] POI检索服务
- [ ] 地理编码/逆编码服务
- [ ] 路径规划与等时圈计算
- [ ] API缓存层（TTL、去重）

### 3.2 评分引擎
- [ ] 维度计算器
- [ ] 权重模板服务
- [ ] 风险规则引擎
- [ ] 可解释输出生成器

### 3.3 业务流程
- [ ] 候选点位生命周期管理
- [ ] 批量任务调度与进度追踪
- [ ] 报告生成与归档

### 3.4 平台能力
- [ ] RBAC权限
- [ ] 操作审计
- [ ] 系统配置管理

---

## 4. 验收门槛（研发）
- [ ] API失败降级可用
- [ ] 核心页面无阻塞级Bug
- [ ] 核心链路端到端可跑通
- [ ] 关键指标达到PRD要求


---

# 附件B：数据库表结构草案（V1）

> 说明：以下为逻辑模型，具体字段类型可按 PostgreSQL + PostGIS 落地。

## 1. 基础实体

### 1.1 `projects`（选址项目）
- `id` (PK)
- `name` 项目名称
- `city_code` 城市编码
- `business_type` 业态（tea/icecream/dessert/bakery/meatpie/noodle_premium）
- `status` 状态（active/archived）
- `owner_user_id`
- `created_at` / `updated_at`

### 1.2 `site_candidates`（候选点位）
- `id` (PK)
- `project_id` (FK)
- `name` 点位名
- `address` 地址
- `location_gcj` 地理坐标（POINT）
- `source_type` 来源（manual/import/amap_poi）
- `area_sqm` 面积（可空）
- `rent_monthly` 月租（可空）
- `status`（pending/evaluating/field_check/approved/rejected）
- `remarks`
- `created_at` / `updated_at`

### 1.3 `competitors`（竞品门店库）
- `id` (PK)
- `brand_name`
- `store_name`
- `category` 竞品分类
- `price_band` 价格带
- `address`
- `location_gcj`（POINT）
- `source`（amap/manual/import）
- `updated_at`

---

## 2. 地图与API缓存

### 2.1 `amap_poi_cache`
- `id` (PK)
- `query_hash` 查询参数哈希（唯一）
- `query_json` 查询原文
- `response_json` 响应原文
- `expires_at`
- `created_at`

### 2.2 `amap_route_cache`
- `id` (PK)
- `origin`
- `destination`
- `mode`（walk/drive）
- `distance_m`
- `duration_s`
- `response_json`
- `expires_at`
- `created_at`

---

## 3. 评分与模型

### 3.1 `score_templates`（业态模板）
- `id` (PK)
- `business_type`
- `version`
- `weights_json`（各维度权重）
- `is_active`
- `created_at`

### 3.2 `site_scores`（评分结果）
- `id` (PK)
- `site_candidate_id` (FK)
- `template_id` (FK)
- `total_score`
- `dimension_scores_json`
- `risk_penalty`
- `recommendation`（recommend/caution/reject）
- `explanation_text`
- `scored_at`

### 3.3 `field_checks`（实勘回填）
- `id` (PK)
- `site_candidate_id` (FK)
- `traffic_observation`
- `visibility_observation`
- `rival_observation`
- `risk_notes`
- `photos_json`
- `checker_user_id`
- `checked_at`

---

## 4. 报告与流程

### 4.1 `reports`
- `id` (PK)
- `project_id` (FK)
- `site_candidate_id` (FK)
- `report_type`（full/brief）
- `report_url`
- `snapshot_json`
- `generated_by`
- `generated_at`

### 4.2 `workflow_logs`
- `id` (PK)
- `entity_type`（site/report/project）
- `entity_id`
- `action`
- `from_status`
- `to_status`
- `operator_user_id`
- `note`
- `created_at`

---

## 5. 用户与权限

### 5.1 `users`
- `id` (PK)
- `name`
- `email`
- `role`（admin/manager/analyst/viewer）
- `status`
- `created_at`

### 5.2 `audit_logs`
- `id` (PK)
- `user_id`
- `module`
- `action`
- `request_meta_json`
- `created_at`

---

## 6. 索引建议
- `site_candidates(project_id, status)`
- `site_scores(site_candidate_id, scored_at DESC)`
- `competitors(category)`
- 空间索引：`location_gcj`（GIST）
- 缓存唯一索引：`amap_poi_cache(query_hash)`

---

## 7. 数据保留策略（建议）
- API缓存：7~30天（按配额成本调）
- 评分结果：长期保留（用于复盘）
- 审计日志：至少180天
