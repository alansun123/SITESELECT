# SITESELECT 全 AI Agent 开发蓝图（OpenClaw Best Practice）

## 0. 目标

把 SITESELECT 做成 **GUI-first MVP**，并通过多 Agent 协作实现：
- 快速迭代（并行开发）
- 可控质量（统一验收门禁）
- 可回滚（每步可恢复）
- 可持续（错误沉淀 + 记忆复盘）

---

## 1. 组织结构：主 Agent + 专家子 Agent

### 1.1 主 Agent（Orchestrator）
职责：
1. 维护产品范围（防 scope creep）
2. 拆任务并分派给子 Agent
3. 汇总交付、执行最终验收
4. 统一提交与发布

### 1.2 子 Agent 角色

1) **PM Agent**
- 维护 PRD、里程碑、DoD
- 将模糊需求转成可验收任务

2) **UX Agent**
- 负责 GUI 信息架构、交互流程、文案可理解性
- 保证“先结论后细节”的报告体验

3) **GUI Agent**
- 实现 Streamlit 页面与交互状态管理
- 落地四步流程（项目定义/数据导入/权重配置/结果导出）

4) **Scoring Agent**
- 维护评分引擎（归一化、加权、解释）
- 输出可解释性说明（为什么这个点排第一）

5) **Data Agent**
- 负责 CSV 字段校验、清洗、映射
- 预留高德增强接口（可插拔）

6) **QA Agent**
- 设计回归用例与边界数据
- 判定“可发布/不可发布”

7) **Release Agent**
- 更新 README/CHANGELOG
- 生成版本发布说明与回滚指令

---

## 2. 开发节奏（5天冲刺）

### Day 1：框架与底座
- PM Agent：冻结 MVP 范围与 DoD
- UX Agent：输出 GUI 流程稿
- GUI Agent：搭页面框架
- Scoring/Data Agent：稳定输入输出契约

### Day 2：核心能力
- GUI Agent：上传、校验、配置、结果页
- Scoring Agent：评分与解释
- QA Agent：首轮 smoke test

### Day 3：报告与可交付
- Report 模板定稿（HTML）
- GUI 一键导出报告
- QA 回归测试 + 缺陷清单

### Day 4：真实样本试跑
- Data Agent 导入真实样本
- UX Agent 修正文案与交互阻塞点
- 主 Agent 冻结发布候选版本

### Day 5：发布与获客素材
- Release Agent：发布说明、演示脚本
- 生成“99元咨询交付模板”

---

## 3. 任务模板（每个子 Agent必须遵守）

每个任务回传必须包含：

1. **变更内容**（改了哪些文件）
2. **验收结果**（怎么验证，结果是什么）
3. **风险说明**（可能影响哪些模块）
4. **回滚方案**（如何一键撤销）

建议格式：

```text
[任务名]
- Files:
- Verification:
- Risks:
- Rollback:
```

---

## 4. 质量门禁（DoD）

发布前必须全部通过：

1) 代码门禁
- `python3 -m py_compile app/gui_app.py src/siteselect/cli.py`

2) 功能门禁
- GUI：四步流程可完整走通
- CLI：`analyze` 命令可生成报告

3) 体验门禁
- 错误提示可读（字段缺失/空文件/无结果）
- 结果页先展示 Top1 结论

4) 交付门禁
- `output/report.html` 可打开
- README 与实际命令一致

---

## 5. Git 策略（Agent 协作专用）

- 小步提交：每个任务一个 commit
- commit 前缀建议：
  - `feat:` 新功能
  - `fix:` 缺陷修复
  - `docs:` 文档
  - `refactor:` 重构
- 关键改动必须带回滚描述

推荐分支策略：
- `main`: 可发布主干
- `agent/<role>/<task>`: 子 Agent 临时分支（合并后删除）

---

## 6. 风险与防线

### 6.1 范围膨胀风险
防线：PM Agent 每日核对 “是否仍在 MVP 范围内”。

### 6.2 交互复杂化风险
防线：UX Agent 只保留“最短可交付路径”，每步最多 1 个主动作。

### 6.3 数据质量风险
防线：Data Agent 强制字段校验 + 默认值策略 + 错误可读提示。

### 6.4 宣称成功过早
防线：主 Agent 只有在 QA 通过后才可对外宣布“完成”。

---

## 7. 记忆与复盘机制（OpenClaw）

- 每次失败/纠正/踩坑，立即写入 `memory/error-log.md`
- 每日复盘：提炼可长期复用经验进 `MEMORY.md`
- 心跳时检查是否有“已知错误重复发生”

---

## 8. 立即可执行的下一步

1. 由 PM Agent 生成当前 Sprint 任务清单（GUI/Scoring/Data/QA）
2. 并行启动 3 个子 Agent：GUI Agent、Scoring Agent、QA Agent
3. 今日完成一个“可演示版本”：上传样例CSV → 输出报告
4. 准备 1 份“99元咨询交付模板”作为商业闭环

---

## 9. 成功标准（AI Agent 视角）

- 不是“写了很多代码”，而是：
  - 用户能通过 GUI 在 5 分钟内完成一次分析
  - 报告可直接发给客户
  - 整个流程可以重复、可解释、可回滚

