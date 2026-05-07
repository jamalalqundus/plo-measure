#!/usr/bin/env python3
"""
Generate all figures for the PLO-MEASURE manuscript
Run: python figures/generate_figures.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import os

# Create output directory
os.makedirs('.', exist_ok=True)

print("=" * 70)
print("Generating PLO-MEASURE Figures")
print("=" * 70)

# ============================================================
# Figure 2: Results Comparison (Precision@5)
# ============================================================
print("\n1. Generating Figure 2: Results Comparison...")

methods = ['Jaccard\n(Structural)', 'BERT\n(Semantic)', 'Bloom\n(Cognitive)', 'Hybrid\n(α=0.5)']
precisions = [0.9895, 0.3095, 0.3411, 0.9895]

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#2E86AB', '#A23B72', '#F18F01', '#2E86AB']
bars = ax.bar(methods, precisions, color=colors, edgecolor='black')
ax.set_ylabel('Precision@5')
ax.set_ylim(0, 1.1)
ax.axhline(y=0.9895, color='gray', linestyle='--', alpha=0.5)
for bar, prec in zip(bars, precisions):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{prec:.4f}', ha='center', fontsize=10)
plt.title('Comparison of Similarity Methods for CLO Recommendation', fontsize=12)
plt.tight_layout()
plt.savefig('resultsComparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: resultsComparison.png")

# ============================================================
# Figure 3: Weighted vs Unweighted Comparison
# ============================================================
print("\n2. Generating Figure 3: Weighted vs Unweighted...")

scenarios = ['Strong vs Weak', 'Mixed Weights', 'All Strong', 'All Weak', 'Realistic']
weighted = [0.801, 0.767, 0.800, 0.850, 0.556]
unweighted = [0.700, 0.700, 0.800, 0.850, 0.547]

x = np.arange(len(scenarios))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, weighted, width, label='Weighted', color='#2E86AB', edgecolor='black')
bars2 = ax.bar(x + width/2, unweighted, width, label='Unweighted', color='#A23B72', edgecolor='black')
ax.set_xlabel('Scenario')
ax.set_ylabel('KPI Achievement')
ax.set_xticks(x)
ax.set_xticklabels(scenarios, rotation=15, ha='right')
ax.legend()
ax.set_ylim(0, 1.0)
plt.title('Weighted vs Unweighted KPI Achievement Calculation', fontsize=12)
plt.tight_layout()
plt.savefig('weighted_vs_unweighted.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: weighted_vs_unweighted.png")

# ============================================================
# Figure 4: Transitive Similarity Recall Improvement
# ============================================================
print("\n3. Generating Figure 4: Transitive Similarity Recall...")

methods = ['Direct\n(Shared PLOs)', 'Transitive\n(KPI+Assessment+Instructor)']
recalls = [0.123, 0.379]

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(methods, recalls, color=['#2E86AB', '#A23B72'], edgecolor='black')
ax.set_ylabel('Recall@5')
ax.set_ylim(0, 0.5)
for bar, rec in zip(bars, recalls):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{rec:.3f}', ha='center', fontsize=10)
ax.annotate(f'+{recalls[1]-recalls[0]:.0%} improvement', xy=(0.5, 0.4), xytext=(0.4, 0.45),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10)
plt.title('Recall Improvement with Transitive Similarity', fontsize=12)
plt.tight_layout()
plt.savefig('transitive_similarity_recall.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: transitive_similarity_recall.png")

# ============================================================
# Figure 5: User Study Results
# ============================================================
print("\n4. Generating Figure 5: User Study Results...")

metrics = ['Usefulness', 'Relevance', 'Clarity', 'Trust', 'Adoption']
means = [4.20, 3.90, 3.84, 3.81, 4.24]
stds = [0.46, 0.63, 0.70, 0.46, 0.46]
n = 30
ci_errors = [stats.t.interval(0.95, n-1, loc=m, scale=s/np.sqrt(n))[1] - m for m, s in zip(means, stds)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart with confidence intervals
x = np.arange(len(metrics))
bars = ax1.bar(x, means, yerr=ci_errors, capsize=5, color='#2E86AB', edgecolor='black')
ax1.set_xticks(x)
ax1.set_xticklabels(metrics)
ax1.set_ylabel('Average Rating (1-5)')
ax1.set_ylim(0, 5.5)
ax1.set_title(f'User Study Results (n={n}, GJU+MEU)')
for bar, mean in zip(bars, means):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{mean:.2f}', ha='center', fontsize=9)

# Permission match pie chart
permission_counts = [23, 7]  # 76.7% Yes, 23.3% No
labels = ['Matches Expectation (77%)', 'Does Not Match (23%)']
colors = ['#A23B72', '#F18F01']
ax2.pie(permission_counts, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
ax2.set_title('Permission Inference Expectation')

plt.tight_layout()
plt.savefig('userSurveyResults.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: userSurveyResults.png")

# ============================================================
# Figure 6: TF-IDF Baseline Comparison
# ============================================================
print("\n5. Generating Figure 6: TF-IDF Baseline Comparison...")

methods = ['TF-IDF', 'Fine-tuned\nBERT', 'Jaccard\n(Structural)']
f1_scores = [0.182, 0.810, 0.990]
precision = [0.667, 0.710, 0.990]
recall = [0.105, 0.940, 0.221]

x = np.arange(len(methods))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))
bars1 = ax.bar(x - width, f1_scores, width, label='F1 Score', color='#2E86AB', edgecolor='black')
bars2 = ax.bar(x, precision, width, label='Precision', color='#A23B72', edgecolor='black')
bars3 = ax.bar(x + width, recall, width, label='Recall', color='#F18F01', edgecolor='black')

ax.set_ylabel('Score')
ax.set_ylim(0, 1.1)
ax.set_xticks(x)
ax.set_xticklabels(methods)
ax.legend(loc='upper right')
ax.set_title('Comparison of Methods on Real CLO-PLO Dataset', fontsize=12)

for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        if height > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('tfidfComparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✓ Saved: tfidfComparison.png")

print("\n" + "=" * 70)
print("All figures generated successfully!")
print("=" * 70)
print("\nOutput files:")
print("  - resultsComparison.png")
print("  - weighted_vs_unweighted.png")
print("  - transitive_similarity_recall.png")
print("  - userSurveyResults.png")
print("  - tfidfComparison.png")