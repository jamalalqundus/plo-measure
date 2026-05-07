#!/usr/bin/env python3
"""
TF-IDF Baseline for CLO Similarity
Evaluates TF-IDF + cosine similarity on the CLO-PLO dataset
"""

import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_clo_plo_data(data_path="/content/CLO-PLO-main"):
    """
    Load CLO descriptions and PLO mappings from the Zaki et al. dataset
    """
    try:
        cs_courses = pd.read_excel(f"{data_path}/Course-Mappings-CompScience.xlsx")
        infosec_courses = pd.read_excel(f"{data_path}/Course-Mappings-InfoSecurity.xlsx")
    except FileNotFoundError:
        print("Error: CLO-PLO dataset not found. Please download from https://github.com/nzaki02/CLO-PLO")
        return []
    
    clos_data = []
    
    # Extract from CS courses
    for _, row in cs_courses.iterrows():
        clo_text = row.get('Outcome')
        if pd.notna(clo_text) and isinstance(clo_text, str) and len(clo_text) > 20:
            plos = []
            for plo_col in ['POL1', 'PLO2', 'POL3', 'POL4', 'PLO5', 'POL6']:
                if plo_col in cs_courses.columns and pd.notna(row[plo_col]):
                    val = str(row[plo_col]).strip().lower()
                    if val == 'x' or val == '1':
                        plo_num = plo_col.replace('POL', '').replace('PLO', '').replace('2', '2')
                        plos.append(f"PLO_{plo_num}")
            if plos:
                clos_data.append({
                    'text': str(clo_text),
                    'plos': plos,
                    'source': 'CS'
                })
    
    # Extract from InfoSec courses
    for _, row in infosec_courses.iterrows():
        clo_text = row.get('CLOs')
        if pd.notna(clo_text) and isinstance(clo_text, str) and len(clo_text) > 20:
            plos = []
            for plo_col in ['SO1', 'SO2', 'SO3', 'SO4', 'SO5', 'SO6']:
                if plo_col in infosec_courses.columns and pd.notna(row[plo_col]):
                    val = str(row[plo_col]).strip().lower()
                    if val == 'x' or val == '1':
                        plo_num = plo_col.replace('SO', '')
                        plos.append(f"PLO_{plo_num}")
            if plos:
                clos_data.append({
                    'text': str(clo_text),
                    'plos': plos,
                    'source': 'InfoSec'
                })
    
    return clos_data

def create_pairs(clos_data, random_seed=42):
    """
    Create positive and negative pairs for similarity evaluation
    """
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    positive_pairs = []
    for i in range(len(clos_data)):
        for j in range(i+1, len(clos_data)):
            plos_i = set(clos_data[i]['plos'])
            plos_j = set(clos_data[j]['plos'])
            if len(plos_i.intersection(plos_j)) > 0:
                positive_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 1.0))
    
    negative_pairs = []
    for i in range(len(clos_data)):
        for _ in range(2):
            j = random.randint(0, len(clos_data)-1)
            while j == i:
                j = random.randint(0, len(clos_data)-1)
            plos_i = set(clos_data[i]['plos'])
            plos_j = set(clos_data[j]['plos'])
            if len(plos_i.intersection(plos_j)) == 0:
                negative_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 0.0))
            if len(negative_pairs) >= len(positive_pairs):
                break
    
    min_len = min(len(positive_pairs), len(negative_pairs))
    positive_pairs = positive_pairs[:min_len]
    negative_pairs = negative_pairs[:min_len]
    
    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)
    
    train_pairs, test_pairs = train_test_split(all_pairs, test_size=0.2, random_state=random_seed)
    
    return train_pairs, test_pairs

def evaluate_tfidf(test_pairs):
    """
    Compute TF-IDF vectors and evaluate performance
    """
    all_texts = list(set([p[0] for p in test_pairs] + [p[1] for p in test_pairs]))
    
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000, ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(all_texts)
    
    text_to_idx = {text: i for i, text in enumerate(all_texts)}
    
    predictions = []
    true_labels = []
    
    for text1, text2, label in test_pairs:
        idx1 = text_to_idx.get(text1)
        idx2 = text_to_idx.get(text2)
        if idx1 is not None and idx2 is not None:
            sim = cosine_similarity(tfidf_matrix[idx1:idx1+1], tfidf_matrix[idx2:idx2+1])[0][0]
            predictions.append(sim)
            true_labels.append(label)
    
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    best_f1 = 0
    best_threshold = 0
    best_precision = 0
    best_recall = 0
    
    for t in thresholds:
        pred_binary = [1 if p >= t else 0 for p in predictions]
        precision = precision_score(true_labels, pred_binary, zero_division=0)
        recall = recall_score(true_labels, pred_binary, zero_division=0)
        f1 = f1_score(true_labels, pred_binary, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = t
            best_precision = precision
            best_recall = recall
    
    return {
        'precision': best_precision,
        'recall': best_recall,
        'f1': best_f1,
        'threshold': best_threshold,
        'test_size': len(test_pairs)
    }

def main():
    print("=" * 70)
    print("TF-IDF Baseline Evaluation on CLO-PLO Dataset")
    print("=" * 70)
    
    clos_data = load_clo_plo_data()
    if not clos_data:
        return
    
    print(f"\nLoaded {len(clos_data)} CLOs with PLO mappings")
    
    train_pairs, test_pairs = create_pairs(clos_data)
    print(f"Training pairs: {len(train_pairs)}")
    print(f"Test pairs: {len(test_pairs)}")
    
    results = evaluate_tfidf(test_pairs)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Test set size: {results['test_size']} pairs")
    print(f"Best threshold: {results['threshold']}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall: {results['recall']:.4f}")
    print(f"F1 Score: {results['f1']:.4f}")
    
    # Save results
    os.makedirs('../output/evaluation', exist_ok=True)
    with open('../output/evaluation/tfidf_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✓ Results saved to ../output/evaluation/tfidf_results.json")

if __name__ == "__main__":
    main()