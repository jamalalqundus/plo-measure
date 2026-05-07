#!/usr/bin/env python3
"""
Achievement Calculation
Implements Equations 1-3 from the paper: CLO → KPI → PLO weighted aggregation
"""

import pandas as pd
import numpy as np
import json
import os
from collections import defaultdict
from scipy import stats

# Weight values for contributions
WEIGHT_VALUES = {
    'weak': 0.33,
    'middle': 0.66,
    'strong': 1.0
}

def calculate_clo_achievement(grades_df):
    """
    Calculate CLO achievement using Equation (1).
    
    Equation (1): CLO Achievement = (1/n) * Σ(score_i / maxScore_i)
    
    Args:
        grades_df: DataFrame with columns 'clo_id', 'score', 'max_score', 'student_id'
    
    Returns:
        dict: CLO achievement per CLO
    """
    # Group by CLO and student, then average
    per_student = grades_df.groupby(['clo_id', 'student_id']).apply(
        lambda x: (x['score'] / x['max_score']).mean()
    ).reset_index(name='normalized_score')
    
    # Average across students
    clo_achievement = per_student.groupby('clo_id')['normalized_score'].mean().to_dict()
    
    return clo_achievement

def calculate_kpi_achievement(clo_achievement, clo_to_kpi, clo_weights):
    """
    Calculate KPI achievement using Equation (2).
    
    Equation (2): KPI Achievement = Σ(CLO_Achievement_j × w_j) / Σ(w_j)
    
    Args:
        clo_achievement: dict mapping clo_id → achievement
        clo_to_kpi: dict mapping clo_id → kpi_id
        clo_weights: dict mapping clo_id → weight category ('weak', 'middle', 'strong')
    
    Returns:
        dict: KPI achievement per KPI
    """
    kpi_to_clos = defaultdict(list)
    for clo, kpi in clo_to_kpi.items():
        kpi_to_clos[kpi].append(clo)
    
    kpi_achievement = {}
    for kpi, clos in kpi_to_clos.items():
        total_weight = 0
        weighted_sum = 0
        for clo in clos:
            if clo in clo_achievement and clo in clo_weights:
                weight = WEIGHT_VALUES.get(clo_weights[clo], 0.66)
                weighted_sum += clo_achievement[clo] * weight
                total_weight += weight
        if total_weight > 0:
            kpi_achievement[kpi] = weighted_sum / total_weight
        else:
            kpi_achievement[kpi] = 0.0
    
    return kpi_achievement

def calculate_plo_achievement(kpi_achievement, kpi_to_plo, kpi_weights=None):
    """
    Calculate PLO achievement using Equation (3).
    
    Equation (3): PLO Achievement = Σ(KPI_Achievement_k × w_k) / Σ(w_k)
    
    Args:
        kpi_achievement: dict mapping kpi_id → achievement
        kpi_to_plo: dict mapping kpi_id → plo_id
        kpi_weights: optional dict mapping kpi_id → weight (default: equal weights)
    
    Returns:
        dict: PLO achievement per PLO
    """
    plo_to_kpis = defaultdict(list)
    for kpi, plo in kpi_to_plo.items():
        plo_to_kpis[plo].append(kpi)
    
    plo_achievement = {}
    for plo, kpis in plo_to_kpis.items():
        achievements = [kpi_achievement.get(kpi, 0.0) for kpi in kpis]
        if kpi_weights:
            weights = [kpi_weights.get(kpi, 1.0) for kpi in kpis]
            plo_achievement[plo] = np.average(achievements, weights=weights)
        else:
            plo_achievement[plo] = np.mean(achievements) if achievements else 0.0
    
    return plo_achievement

def generate_synthetic_grade_data(num_students=50, num_courses=5, num_clos_per_course=5):
    """
    Generate synthetic grade data for testing achievement calculation.
    
    Args:
        num_students: Number of students
        num_courses: Number of courses
        num_clos_per_course: Number of CLOs per course
    
    Returns:
        DataFrame: Synthetic grade data
    """
    np.random.seed(42)
    
    data = []
    for student_id in range(1, num_students + 1):
        for course_id in range(1, num_courses + 1):
            for clo_idx in range(1, num_clos_per_course + 1):
                clo_id = f"CLO_{course_id}_{clo_idx}"
                # Generate score between 0 and 1 with some variation
                ability = np.random.beta(2, 2)  # Mean ~0.5
                score = ability * 100
                max_score = 100
                data.append({
                    'student_id': f"S{student_id:03d}",
                    'course_id': f"C{course_id:03d}",
                    'clo_id': clo_id,
                    'score': score,
                    'max_score': max_score
                })
    
    return pd.DataFrame(data)

def generate_synthetic_mappings(num_clos=25, num_kpis=10, num_plos=5):
    """
    Generate synthetic mappings for testing.
    
    Args:
        num_clos: Number of CLOs
        num_kpis: Number of KPIs
        num_plos: Number of PLOs
    
    Returns:
        tuple: (clo_to_kpi, clo_weights, kpi_to_plo)
    """
    np.random.seed(42)
    
    # Create IDs
    clos = [f"CLO_{i}" for i in range(1, num_clos + 1)]
    kpis = [f"KPI_{i}" for i in range(1, num_kpis + 1)]
    plos = [f"PLO_{i}" for i in range(1, num_plos + 1)]
    
    # Assign each CLO to a KPI
    clo_to_kpi = {}
    clo_weights = {}
    for clo in clos:
        kpi = np.random.choice(kpis)
        clo_to_kpi[clo] = kpi
        clo_weights[clo] = np.random.choice(['weak', 'middle', 'strong'], p=[0.3, 0.3, 0.4])
    
    # Assign each KPI to a PLO
    kpi_to_plo = {}
    for kpi in kpis:
        plo = np.random.choice(plos)
        kpi_to_plo[kpi] = plo
    
    return clo_to_kpi, clo_weights, kpi_to_plo

def compare_weighted_vs_unweighted():
    """
    Compare weighted vs unweighted achievement calculation.
    This produces the results for Table 5 in the manuscript.
    """
    scenarios = []
    
    # Scenario 1: Strong vs Weak
    clos_sw = [
        {'achievement': 0.90, 'weight': 'strong', 'label': 'Strong'},
        {'achievement': 0.50, 'weight': 'weak', 'label': 'Weak'}
    ]
    scenarios.append(('Strong vs Weak', clos_sw))
    
    # Scenario 2: Mixed Weights
    clos_mixed = [
        {'achievement': 0.90, 'weight': 'strong', 'label': 'Strong'},
        {'achievement': 0.70, 'weight': 'middle', 'label': 'Middle'},
        {'achievement': 0.50, 'weight': 'weak', 'label': 'Weak'}
    ]
    scenarios.append(('Mixed Weights', clos_mixed))
    
    # Scenario 3: All Strong
    clos_all_strong = [
        {'achievement': 0.90, 'weight': 'strong', 'label': 'Strong 1'},
        {'achievement': 0.80, 'weight': 'strong', 'label': 'Strong 2'},
        {'achievement': 0.70, 'weight': 'strong', 'label': 'Strong 3'}
    ]
    scenarios.append(('All Strong', clos_all_strong))
    
    # Scenario 4: All Weak
    clos_all_weak = [
        {'achievement': 0.90, 'weight': 'weak', 'label': 'Weak 1'},
        {'achievement': 0.80, 'weight': 'weak', 'label': 'Weak 2'}
    ]
    scenarios.append(('All Weak', clos_all_weak))
    
    # Scenario 5: Realistic Program (10 CLOs)
    np.random.seed(42)
    realistic_clos = []
    weights = ['strong', 'strong', 'middle', 'middle', 'middle', 'weak', 'weak', 'weak', 'strong', 'middle']
    achievements = np.random.beta(2, 2, 10)
    for i, (w, a) in enumerate(zip(weights, achievements)):
        realistic_clos.append({'achievement': a, 'weight': w, 'label': f'CLO_{i}'})
    scenarios.append(('Realistic Program', realistic_clos))
    
    results = []
    for name, clos in scenarios:
        # Weighted calculation
        total_weight = sum(WEIGHT_VALUES[c['weight']] for c in clos)
        weighted_sum = sum(c['achievement'] * WEIGHT_VALUES[c['weight']] for c in clos)
        weighted = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Unweighted calculation
        unweighted = np.mean([c['achievement'] for c in clos])
        
        results.append({
            'scenario': name,
            'weighted': weighted,
            'unweighted': unweighted,
            'difference': abs(weighted - unweighted),
            'percent_diff': abs(weighted - unweighted) / max(weighted, unweighted) * 100
        })
    
    return results

def main():
    """Main entry point for testing achievement calculation"""
    print("=" * 70)
    print("Achievement Calculation Demo")
    print("=" * 70)
    
    # Generate synthetic data
    print("\n1. Generating synthetic grade data...")
    grades_df = generate_synthetic_grade_data()
    print(f"   Generated {len(grades_df)} grade records")
    
    # Generate synthetic mappings
    print("\n2. Generating synthetic mappings...")
    clo_to_kpi, clo_weights, kpi_to_plo = generate_synthetic_mappings()
    print(f"   {len(clo_to_kpi)} CLOs → {len(set(clo_to_kpi.values()))} KPIs → {len(set(kpi_to_plo.values()))} PLOs")
    
    # Calculate achievements
    print("\n3. Calculating achievements...")
    clo_ach = calculate_clo_achievement(grades_df)
    kpi_ach = calculate_kpi_achievement(clo_ach, clo_to_kpi, clo_weights)
    plo_ach = calculate_plo_achievement(kpi_ach, kpi_to_plo)
    
    print(f"   CLO achievements: {len(clo_ach)}")
    print(f"   KPI achievements: {len(kpi_ach)}")
    print(f"   PLO achievements: {len(plo_ach)}")
    
    # Compare weighted vs unweighted
    print("\n4. Weighted vs Unweighted Comparison")
    print("-" * 50)
    comparison = compare_weighted_vs_unweighted()
    for r in comparison:
        print(f"\n  {r['scenario']}:")
        print(f"    Weighted: {r['weighted']:.3f}")
        print(f"    Unweighted: {r['unweighted']:.3f}")
        print(f"    Difference: {r['difference']:.3f} ({r['percent_diff']:.1f}%)")
    
    # Save results
    os.makedirs('../output/evaluation', exist_ok=True)
    
    results = {
        'clo_achievement': clo_ach,
        'kpi_achievement': kpi_ach,
        'plo_achievement': plo_ach,
        'weighted_comparison': comparison
    }
    
    with open('../output/evaluation/achievement_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✓ Results saved to ../output/evaluation/achievement_results.json")

if __name__ == "__main__":
    main()