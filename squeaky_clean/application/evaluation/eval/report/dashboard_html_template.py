"""Static HTML template for the meta-evaluation dashboard."""

DASHBOARD_TEMPLATE: str = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><title>Squeaky Clean — meta-eval dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
 body{{font-family:ui-monospace,monospace;max-width:1100px;margin:2em auto;}}
 .summary{{background:#f3f3f3;padding:8px 12px;border:1px solid #ddd;}}
 .chart{{margin:2em 0;border:1px solid #eee;padding:10px;}}
 .reg{{background:#fff5f5;border-left:4px solid #c00;padding:6px 10px;margin:1em 0;}}
 canvas{{max-height:240px;}} h2{{margin-top:1.5em;}} h3{{margin:0 0 .3em;}}
 ul{{margin:.3em 0 .6em 1em;}} code{{background:#eef;padding:1px 4px;}}
</style></head><body>
<h1>Squeaky Clean — meta-evaluation dashboard</h1>
<section class="summary">
<p><b>Total runs:</b> {total_runs}</p>
<p><b>Date range:</b> {date_range}</p>
<p><b>Per-problem run counts:</b></p>
<ul>{problem_counts}</ul>
</section>
<h2>Flagged regressions (≥2σ drop in last 10 runs)</h2>
<div id="regressions">{regressions}</div>
<h2>Time series</h2>
<div id="charts">{charts}</div>
<script>
const SERIES = {series_json};
for (const s of SERIES) {{
  const ctx = document.getElementById('chart-' + s.name);
  if (!ctx) continue;
  new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: s.labels,
      datasets: [
        {{label: s.name, data: s.values, borderColor: '#37c',
          backgroundColor: '#37c2', tension: 0.1}},
        {{label: '5-run mean', data: s.rolling_mean, borderColor: '#c73',
          borderDash: [4, 4], pointRadius: 0, tension: 0.1}},
      ]
    }},
    options: {{responsive: true, plugins: {{legend: {{position: 'bottom'}}}}}}
  }});
}}
</script>
</body></html>
"""

EMPTY_TEMPLATE: str = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Squeaky Clean — no runs yet</title></head>
<body><h1>Squeaky Clean — meta-evaluation dashboard</h1>
<p>No meta-evaluation runs found yet.</p></body></html>
"""
