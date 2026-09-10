"""
Generate performance analysis charts from benchmark results.
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

project_root = os.path.dirname(os.path.abspath(__file__))
artifacts_dir = r"C:\Users\ashis\.gemini\antigravity\brain\8cbb48d2-1585-4c83-81b0-ff32e3c0bafe"

with open(os.path.join(project_root, "benchmark_results.json"), "r") as f:
    data = json.load(f)

results = data["results"]
agg = data["aggregate"]

# ── Style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f172a',
    'axes.facecolor': '#1e293b',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#e2e8f0',
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.grid': True,
    'grid.color': '#334155',
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'text.color': '#e2e8f0',
    'font.family': 'sans-serif',
    'font.size': 10,
    'legend.facecolor': '#1e293b',
    'legend.edgecolor': '#475569',
    'legend.fontsize': 9,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
})

categories = [r["category"] for r in results]
precisions = [r["precision"] for r in results]
recalls = [r["recall"] for r in results]
f1_scores = [r["f1"] for r in results]
coverages = [r["coverage"] for r in results]
times_ms = [r["time_ms"] for r in results]
num_matched = [r["num_matched"] for r in results]
num_partial = [r["num_partial"] for r in results]
num_facts = [r["num_facts"] for r in results]

# ===========================================================================
# CHART 1: Precision / Recall / F1 per category (grouped bar)
# ===========================================================================
fig, ax = plt.subplots(figsize=(16, 7))
x = np.arange(len(categories))
w = 0.25

bars1 = ax.bar(x - w, precisions, w, label='Precision', color='#38bdf8', alpha=0.9, edgecolor='#0284c7', linewidth=0.5)
bars2 = ax.bar(x,     recalls,    w, label='Recall',    color='#818cf8', alpha=0.9, edgecolor='#6366f1', linewidth=0.5)
bars3 = ax.bar(x + w, f1_scores,  w, label='F1 Score',  color='#e879f9', alpha=0.9, edgecolor='#c026d3', linewidth=0.5)

ax.set_xlabel('Crime Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Score (0.0 - 1.0)', fontsize=12, fontweight='bold')
ax.set_title('Rule-Based Expert System: Precision, Recall & F1 Score per Crime Category', fontsize=15, pad=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
ax.set_ylim(0, 1.15)
ax.legend(loc='upper right')

# Add value labels on bars
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width() / 2, h),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=7, color='#cbd5e1')

plt.tight_layout()
fig.savefig(os.path.join(artifacts_dir, "chart_precision_recall_f1.png"))
print("Saved chart 1: Precision / Recall / F1")
plt.close()


# ===========================================================================
# CHART 2: Coverage + Match Distribution (stacked bar with coverage line)
# ===========================================================================
fig, ax1 = plt.subplots(figsize=(16, 7))

ax1.bar(x, num_matched, 0.5, label='Full Matches', color='#34d399', alpha=0.9, edgecolor='#059669', linewidth=0.5)
ax1.bar(x, num_partial, 0.5, bottom=num_matched, label='Partial Matches', color='#fbbf24', alpha=0.7, edgecolor='#d97706', linewidth=0.5)
ax1.set_xlabel('Crime Category', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Rules', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)
ax1.set_title('Rule Firing Distribution & Coverage per Crime Category', fontsize=15, pad=15)

ax2 = ax1.twinx()
ax2.plot(x, coverages, 'o-', color='#f87171', linewidth=2.5, markersize=8, label='Coverage', zorder=5)
ax2.set_ylabel('Coverage (0.0 - 1.0)', fontsize=12, fontweight='bold', color='#f87171')
ax2.set_ylim(0, 1.15)
ax2.tick_params(axis='y', labelcolor='#f87171')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
fig.savefig(os.path.join(artifacts_dir, "chart_coverage_distribution.png"))
print("Saved chart 2: Coverage & Distribution")
plt.close()


# ===========================================================================
# CHART 3: Inference Time per Category
# ===========================================================================
fig, ax = plt.subplots(figsize=(14, 6))

colors = ['#38bdf8' if t < 50 else '#818cf8' if t < 100 else '#e879f9' if t < 200 else '#f87171' for t in times_ms]
bars = ax.bar(categories, times_ms, color=colors, alpha=0.9, edgecolor='#334155', linewidth=0.5)

ax.set_xlabel('Crime Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Inference Time (ms)', fontsize=12, fontweight='bold')
ax.set_title('Rule-Based Inference Time per Crime Category', fontsize=15, pad=15)
ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=9)

# Add time labels
for bar, t in zip(bars, times_ms):
    ax.annotate(f'{t:.0f}ms', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
               xytext=(0, 4), textcoords="offset points",
               ha='center', va='bottom', fontsize=8, color='#cbd5e1')

# Legend for color coding
legend_patches = [
    mpatches.Patch(color='#38bdf8', label='< 50ms (Fast)'),
    mpatches.Patch(color='#818cf8', label='50-100ms (Normal)'),
    mpatches.Patch(color='#e879f9', label='100-200ms (Moderate)'),
    mpatches.Patch(color='#f87171', label='> 200ms (Slow)'),
]
ax.legend(handles=legend_patches, loc='upper right')

avg_line = ax.axhline(y=agg["avg_time_ms"], color='#fbbf24', linestyle='--', linewidth=1.5, alpha=0.8)
ax.annotate(f'Avg: {agg["avg_time_ms"]:.0f}ms', xy=(len(categories)-1, agg["avg_time_ms"]),
           xytext=(10, 5), textcoords="offset points",
           color='#fbbf24', fontsize=10, fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(artifacts_dir, "chart_inference_time.png"))
print("Saved chart 3: Inference Time")
plt.close()


# ===========================================================================
# CHART 4: Radar / Spider chart for aggregate metrics
# ===========================================================================
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
fig.patch.set_facecolor('#0f172a')
ax.set_facecolor('#1e293b')

metrics = ['Precision', 'Recall', 'F1 Score', 'Coverage', 'Speed\n(normalized)']
values = [
    agg["avg_precision"],
    agg["avg_recall"],
    agg["avg_f1"],
    agg["avg_coverage"],
    max(0, 1.0 - agg["avg_time_ms"] / 500)  # normalize: lower time = higher score
]
values += values[:1]  # close the polygon

angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
angles += angles[:1]

ax.plot(angles, values, 'o-', color='#818cf8', linewidth=2, markersize=8)
ax.fill(angles, values, alpha=0.25, color='#818cf8')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(metrics, fontsize=11, fontweight='bold', color='#e2e8f0')
ax.set_ylim(0, 1.0)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8, color='#94a3b8')
ax.set_title('System Performance Overview (Aggregate)', fontsize=14, fontweight='bold', pad=25, color='#e2e8f0')
ax.grid(color='#475569', linestyle='--', alpha=0.5)
ax.spines['polar'].set_color('#475569')

# Annotate values
for angle, val, label in zip(angles[:-1], values[:-1], metrics):
    ax.annotate(f'{val:.2f}', xy=(angle, val), xytext=(5, 5),
               textcoords="offset points", fontsize=9, color='#38bdf8', fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(artifacts_dir, "chart_radar_overview.png"))
print("Saved chart 4: Radar overview")
plt.close()


# ===========================================================================
# CHART 5: Facts Extracted per Category (horizontal bar)
# ===========================================================================
fig, ax = plt.subplots(figsize=(12, 8))

sorted_indices = np.argsort(num_facts)
sorted_cats = [categories[i] for i in sorted_indices]
sorted_facts = [num_facts[i] for i in sorted_indices]

gradient_colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(sorted_facts)))
bars = ax.barh(sorted_cats, sorted_facts, color=gradient_colors, edgecolor='#334155', linewidth=0.5, height=0.7)

for bar, v in zip(bars, sorted_facts):
    ax.text(v + 0.2, bar.get_y() + bar.get_height()/2, str(v),
           va='center', ha='left', fontsize=10, color='#e2e8f0', fontweight='bold')

ax.set_xlabel('Number of Facts Extracted', fontsize=12, fontweight='bold')
ax.set_title('Fact Extraction Count per Crime Category', fontsize=15, pad=15)
ax.set_xlim(0, max(sorted_facts) + 3)

plt.tight_layout()
fig.savefig(os.path.join(artifacts_dir, "chart_facts_extracted.png"))
print("Saved chart 5: Facts extracted")
plt.close()

print("\nAll charts generated successfully!")
