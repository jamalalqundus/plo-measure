#!/usr/bin/env python3
"""
Generate synthetic data for achievement calculation and permission evaluation
"""

import pandas as pd
import numpy as np
import random
from collections import defaultdict
import json
import os

def generate_synthetic_grades(num_students=50, num_courses=10, num_questions_per_course=10):
    """Generate synthetic student grade data"""
    np.random.seed(42)
    
    courses = [f"CS_{i+1:03d}" for i in range(num_courses)]
    grades_data = []
    
    for student_id in range(num_students):
        for course in courses:
            for question_id in range(num_questions_per_course):
                max_score = random.randint(5, 50)
                ability = np.random.beta(2, 2)
                score = ability * max_score
                score = min(max_score, max(0, score + np.random.normal(0, max_score * 0.1)))
                grades_data.append({
                    'student_id': f"S{student_id:03d}",
                    'course': course,
                    'question_id': f"Q_{course}_{question_id}",
                    'max_score': max_score,
                    'score': score
                })
    
    return pd.DataFrame(grades_data)

def generate_kpi_plo_hierarchy(num_plos=6, num_kpis_per_plo=2):
    """Generate KPI-PLO hierarchy with weights"""
    kpi_categories = ['Knowledge', 'Skill', 'Competency']
    weight_values = {'weak': 0.33, 'middle': 0.66, 'strong': 1.0}
    
    hierarchy = {
        'plos': [],
        'kpis': [],
        'clo_to_kpi': {},
        'clo_weights': {}
    }
    
    for plo_id in range(1, num_plos + 1):
        plo = f"PLO_{plo_id}"
        hierarchy['plos'].append(plo)
        
        for kpi_idx in range(1, num_kpis_per_plo + 1):
            kpi = f"KPI_{plo}_{kpi_idx}"
            category = random.choice(kpi_categories)
            hierarchy['kpis'].append({
                'id': kpi,
                'plo': plo,
                'category': category
            })
    
    return hierarchy

def calculate_achievement(grades_df):
    """Calculate CLO, KPI, and PLO achievements"""
    # Simplified calculation for demonstration
    clo_achievement = grades_df.groupby('student_id')['score'].mean() / grades_df.groupby('student_id')['max_score'].mean()
    
    return {
        'clo_avg': clo_achievement.mean(),
        'kpi_avg': 0.0,
        'plo_avg': 0.0
    }

def main():
    print("=" * 70)
    print("Generating Synthetic Data for PLO-MEASURE")
    print("=" * 70)
    
    grades_df = generate_synthetic_grades()
    print(f"\nGenerated {len(grades_df)} grade records")
    print(f"  Students: {grades_df['student_id'].nunique()}")
    print(f"  Courses: {grades_df['course'].nunique()}")
    
    hierarchy = generate_kpi_plo_hierarchy()
    print(f"\nGenerated hierarchy:")
    print(f"  PLOs: {len(hierarchy['plos'])}")
    print(f"  KPIs: {len(hierarchy['kpis'])}")
    
    achievement = calculate_achievement(grades_df)
    print(f"\nAchievement results:")
    print(f"  Average CLO achievement: {achievement['clo_avg']:.3f}")
    
    os.makedirs('../output/data', exist_ok=True)
    grades_df.to_csv('../output/data/synthetic_grades.csv', index=False)
    
    with open('../output/data/hierarchy.json', 'w') as f:
        json.dump(hierarchy, f, indent=2)
    
    print("\n✓ Data saved to ../output/data/")

if __name__ == "__main__":
    main()