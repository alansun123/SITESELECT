<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>SITESELECT 报告</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; }
    h1, h2 { margin: 8px 0; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 14px; text-align: left; }
    th { background: #f6f6f6; }
    .muted { color: #666; font-size: 13px; }
  </style>
</head>
<body>
  <h1>SITESELECT 选址分析报告（MVP）</h1>
  <p class="muted">生成时间：{{generated_at}}</p>

  <h2>Top {{top_n}} 推荐</h2>
  <ol>
  {{top_list_items}}
  </ol>

  <h2>完整排名</h2>
  <table>
    <thead>
      <tr>
        <th>排名</th>
        <th>名称</th>
        <th>总分</th>
        <th>月租</th>
        <th>客流指数</th>
        <th>竞争数</th>
        <th>距目标距离(m)</th>
        <th>数据校验提示</th>
      </tr>
    </thead>
    <tbody>
      {{table_rows}}
    </tbody>
  </table>
</body>
</html>
