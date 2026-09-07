import io
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse
from ..utils.storage import storage
from ..services.duplicates import deduplicate_dataframe
from ..services.profiler import profile_dataset
from ..services.missing import analyze_missingness
from ..services.duplicates import analyze_duplicates
from ..services.distributions import analyze_distributions
from ..services.outliers import analyze_outliers
from ..services.correlations import analyze_correlations
from ..services.categorical import analyze_categorical
from ..services.insights import generate_insights_and_quality

router = APIRouter(tags=["Export"])

@router.get("/download-deduplicated/{dataset_id}")
async def download_deduplicated_csv(dataset_id: str):
    df = storage.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found."
        )

    deduped_df = deduplicate_dataframe(df)
    
    stream = io.StringIO()
    deduped_df.to_csv(stream, index=False)
    stream.seek(0)

    meta = storage.get_metadata(dataset_id) or {}
    base_name = meta.get("filename", "dataset.csv").replace(".csv", "")
    download_filename = f"{base_name}_cleaned_deduplicated.csv"

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
    )

@router.get("/export-report/{dataset_id}", response_class=HTMLResponse)
async def export_html_report(dataset_id: str):
    df = storage.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found."
        )

    meta = storage.get_metadata(dataset_id) or {}
    filename = meta.get("filename", "Dataset")

    # Run complete analysis
    profile = profile_dataset(df)
    missing = analyze_missingness(df)
    duplicates = analyze_duplicates(df)
    distributions = analyze_distributions(df, numeric_columns=profile["numeric_columns"])
    outliers = analyze_outliers(df, numeric_columns=profile["numeric_columns"])
    correlations = analyze_correlations(df, numeric_columns=profile["numeric_columns"])
    categorical = analyze_categorical(df, categorical_columns=profile["categorical_columns"])
    insights = generate_insights_and_quality(profile, missing, duplicates, distributions, outliers, correlations, categorical)

    q_score = insights["quality_score"]
    
    # Generate standalone, beautiful modern HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDAflow Report — {filename}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: #111827;
            --card-border: #1f2937;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #3b82f6;
            --primary-glow: rgba(59, 130, 246, 0.15);
            --accent: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 32px;
        }}
        .logo-title {{ display: flex; align-items: center; gap: 12px; }}
        .logo-badge {{
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: white;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 1.1rem;
            letter-spacing: -0.5px;
        }}
        .title-text {{ font-size: 1.5rem; font-weight: 700; color: #fff; }}
        .meta-pill {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .grid-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
        }}
        .stat-label {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .stat-value {{ font-size: 1.8rem; font-weight: 800; color: #fff; margin-top: 4px; }}
        
        .score-hero {{
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.7), var(--card-bg));
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
        }}
        .score-badge {{
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #10b981, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .section-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #fff;
            margin: 36px 0 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left; }}
        th {{
            background: #1e293b;
            color: #94a3b8;
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--card-border);
        }}
        td {{ padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #e2e8f0; }}
        tr:hover td {{ background: rgba(255,255,255,0.02); }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}
        .badge-high {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .badge-med {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-low {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
        .badge-type {{ background: #1e293b; color: #93c5fd; border: 1px solid #334155; }}
        .insight-card {{
            background: #161e2e;
            border-left: 4px solid var(--primary);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }}
        .insight-card.high {{ border-left-color: var(--danger); }}
        .insight-card.medium {{ border-left-color: var(--warning); }}
        .insight-title {{ font-weight: 700; font-size: 1rem; color: #fff; margin-bottom: 4px; }}
        .insight-desc {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 8px; }}
        .insight-rec {{ color: #93c5fd; font-size: 0.85rem; font-weight: 500; }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 24px;
            border-top: 1px solid var(--card-border);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        @media print {{
            body {{ background: #fff; color: #000; }}
            .card, .stat-card, .score-hero {{ border-color: #e2e8f0; background: #fff; color: #000; }}
            .title-text, .stat-value, td, .insight-title {{ color: #000 !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo-title">
                <div class="logo-badge">EDAflow</div>
                <div>
                    <h1 class="title-text">{filename}</h1>
                    <p style="color: var(--text-muted); font-size: 0.85rem;">Automated Dataset Intelligence Report</p>
                </div>
            </div>
            <div class="meta-pill">Generated by EDAflow Engine • {len(df):,} Rows • {len(df.columns)} Columns</div>
        </header>

        <section class="score-hero">
            <div>
                <h2 style="font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 6px;">Data Quality Score (Grade {q_score['grade']})</h2>
                <p style="color: var(--text-muted); max-width: 600px; font-size: 0.95rem;">{q_score['summary']}</p>
                <div style="margin-top: 12px; display: flex; gap: 16px; font-size: 0.85rem; color: #94a3b8;">
                    <span>Missing Penalty: -{q_score['missingness_penalty']}</span>
                    <span>Duplicate Penalty: -{q_score['duplicate_penalty']}</span>
                    <span>Outlier Penalty: -{q_score['outlier_penalty']}</span>
                    <span>Type Penalty: -{q_score['invalid_type_penalty']}</span>
                </div>
            </div>
            <div class="score-badge">{q_score['final_score']}<span style="font-size: 1.5rem; color: var(--text-muted);">/100</span></div>
        </section>

        <div class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Total Rows</div>
                <div class="stat-value">{profile['rows_count']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Columns</div>
                <div class="stat-value">{profile['columns_count']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Missing Cells</div>
                <div class="stat-value">{missing['overall_missing_percentage']}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duplicate Rows</div>
                <div class="stat-value">{duplicates['duplicate_rows_count']:,} ({duplicates['duplicate_percentage']}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Memory Footprint</div>
                <div class="stat-value">{profile['total_memory_formatted']}</div>
            </div>
        </div>

        <h2 class="section-title">💡 Prioritized Intelligence & Recommendations</h2>
        <div>
            {"".join([f'''
            <div class="insight-card {i['severity']}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div class="insight-title">{i['title']}</div>
                    <span class="badge badge-{i['severity']}">{i['severity'].upper()}</span>
                </div>
                <div class="insight-desc">{i['description']}</div>
                <div class="insight-rec"><strong>Recommendation:</strong> {i['recommendation']}</div>
            </div>
            ''' for i in insights['insights'][:10]])}
        </div>

        <h2 class="section-title">📋 Schema & Feature Typing</h2>
        <div class="card" style="overflow-x: auto; padding: 0;">
            <table>
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Dtype</th>
                        <th>Inferred Type</th>
                        <th>Unique Count</th>
                        <th>Missing Count (%)</th>
                        <th>Sample Values</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{c['name']}</strong></td>
                        <td><span class="badge badge-type">{c['dtype']}</span></td>
                        <td><span class="badge badge-type">{c['inferred_type']}</span></td>
                        <td>{c['unique_count']:,} ({c['unique_ratio']*100:.1f}%)</td>
                        <td>{c['null_count']:,} ({c['null_ratio']*100:.1f}%)</td>
                        <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #94a3b8;">{", ".join([str(v) for v in c['sample_values'][:3]])}</td>
                    </tr>
                    ''' for c in profile['columns']])}
                </tbody>
            </table>
        </div>

        <h2 class="section-title">📊 Numerical Statistics & Distributions</h2>
        <div class="card" style="overflow-x: auto; padding: 0;">
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Mean</th>
                        <th>Median</th>
                        <th>Std Dev</th>
                        <th>Min - Max</th>
                        <th>IQR</th>
                        <th>Skewness</th>
                        <th>Kurtosis</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{s['column']}</strong></td>
                        <td>{s['mean']}</td>
                        <td>{s['median']}</td>
                        <td>{s['std']}</td>
                        <td>{s['min']} to {s['max']}</td>
                        <td>{s['iqr']}</td>
                        <td><span class="badge {'badge-high' if s['is_skewed'] else 'badge-low'}">{s['skewness']} ({s['skew_direction']})</span></td>
                        <td>{s['kurtosis']}</td>
                    </tr>
                    ''' for s in distributions['columns'].values()])}
                </tbody>
            </table>
        </div>

        <h2 class="section-title">🔍 Multi-Method Outlier Detection</h2>
        <div class="card" style="overflow-x: auto; padding: 0;">
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>IQR Method (1.5x)</th>
                        <th>Z-Score (|z|>3)</th>
                        <th>Isolation Forest</th>
                        <th>Consensus (2+ Methods)</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><strong>{o['column']}</strong></td>
                        <td>{o['iqr_outliers_count']:,} ({o['iqr_percentage']}%)</td>
                        <td>{o['zscore_outliers_count']:,} ({o['zscore_percentage']}%)</td>
                        <td>{o['isolation_forest_count']:,} ({o['isolation_forest_percentage']}%)</td>
                        <td><span class="badge {'badge-high' if o['consensus_percentage'] > 3.0 else 'badge-low'}">{o['consensus_count']:,} ({o['consensus_percentage']}%)</span></td>
                    </tr>
                    ''' for o in outliers['columns'][:15]])}
                </tbody>
            </table>
        </div>

        <footer class="footer">
            <p>EDAflow Automated Dataset Intelligence Platform • Built for high-velocity data exploration and ML preparation.</p>
        </footer>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

@router.get("/export-notebook/{dataset_id}")
async def export_jupyter_notebook(dataset_id: str):
    df = storage.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found."
        )

    from ..services.notebook_generator import generate_eda_notebook
    meta = storage.get_metadata(dataset_id) or {}
    filename = meta.get("filename", "dataset.csv")
    profile = profile_dataset(df)

    notebook_content = generate_eda_notebook(filename, profile)
    base_name = Path(filename).stem
    download_filename = f"{base_name}_edaflow_analysis.ipynb"

    return StreamingResponse(
        io.StringIO(notebook_content),
        media_type="application/x-ipynb+json",
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
    )

@router.get("/export-markdown/{dataset_id}")
async def export_markdown_report(dataset_id: str):
    df = storage.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found."
        )

    meta = storage.get_metadata(dataset_id) or {}
    filename = meta.get("filename", "dataset.csv")

    profile = profile_dataset(df)
    missing = analyze_missingness(df)
    duplicates = analyze_duplicates(df)
    distributions = analyze_distributions(df, numeric_columns=profile["numeric_columns"])
    outliers = analyze_outliers(df, numeric_columns=profile["numeric_columns"])
    correlations = analyze_correlations(df, numeric_columns=profile["numeric_columns"])
    categorical = analyze_categorical(df, categorical_columns=profile["categorical_columns"])
    insights = generate_insights_and_quality(profile, missing, duplicates, distributions, outliers, correlations, categorical)

    q = insights["quality_score"]

    md_lines = [
        f"# EDAflow Intelligence Report: `{filename}`",
        f"\n**Data Quality Score:** `{q['final_score']}/100` (Grade {q['grade']})",
        f"> {q['summary']}\n",
        "## Summary Metrics",
        f"- **Total Rows:** {profile['rows_count']:,}",
        f"- **Total Columns:** {profile['columns_count']}",
        f"- **Missing Values:** {missing['overall_missing_percentage']}%",
        f"- **Duplicate Rows:** {duplicates['duplicate_rows_count']:,} ({duplicates['duplicate_percentage']}%)",
        f"- **Memory Footprint:** {profile['total_memory_formatted']}\n",
        "## Top Actionable Insights & Recommendations",
    ]

    for idx, ins in enumerate(insights.get("insights", [])[:8], 1):
        md_lines.append(f"{idx}. **[{ins['severity'].upper()}] {ins['title']}**")
        md_lines.append(f"   - {ins['description']}")
        md_lines.append(f"   - *Action:* {ins['recommendation']}\n")

    md_lines.append("## Column Schema")
    md_lines.append("| Feature | Type | Inferred | Null Count (%) | Unique Count |")
    md_lines.append("|---|---|---|---|---|")
    for col in profile.get("columns", []):
        md_lines.append(f"| `{col['name']}` | `{col['dtype']}` | `{col['inferred_type']}` | {col['null_count']} ({col['null_ratio']*100:.1f}%) | {col['unique_count']} |")

    md_content = "\n".join(md_lines)
    base_name = Path(filename).stem
    download_filename = f"{base_name}_edaflow_summary.md"

    return StreamingResponse(
        io.StringIO(md_content),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
    )

