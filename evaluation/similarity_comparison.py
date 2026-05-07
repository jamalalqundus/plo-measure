#!/usr/bin/env python3
"""
Similarity Method Comparison
Compares Jaccard, TF-IDF, and BERT-based similarity methods
"""

import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
import json
import os

def load_clo_plo_data(data_path="/content/CLO-PLO-main"):
    """Load CLO descriptions and PLO mappings"""
    cs_courses = pd.read_excel(f"{data_path}/Course-Mappings-CompScience.xlsx")
    infosec_courses = pd.read_excel(f"{data_path}/Course-Mappings-InfoSecurity.xlsx")
    
    clos_data = []
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
                clos_data.append({'text': str(clo_text), 'plos': plos})
    
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
                clos_data.append({'text': str(clo_text), 'plos': plos})
    
    return clos_data

def jaccard_similarity(clo_a, clo_b):
    """Compute Jaccard similarity based on shared PLOs"""
    plos_a = set(clo_a['plos'])
    plos_b = set(clo_b['plos'])
    if len(plos_a.union(plos_b)) == 0:
        return 0.0
    return len(plos_a.intersection(plos_b)) / len(plos_a.union(plos_b))

def tfidf_similarity(texts, model):
    """Compute TF-IDF similarity matrix"""
    tfidf_matrix = model.transform(texts)
    return cosine_similarity(tfidf_matrix)

def bert_similarity(texts, model):
    """Compute BERT embedding similarity matrix"""
    embeddings = model.encode(texts)
    return cosine_similarity(embeddings)

def main():
    print("=" * 70)
    print("Similarity Method Comparison")
    print("=" * 70)
    
    clos_data = load_clo_plo_data()
    print(f"Loaded {len(clos_data)} CLOs")
    
    texts = [c['text'] for c in clos_data]
    
    # Compute ground truth
    ground_truth = {}
    for i, clo_a in enumerate(clos_data):
        similar = []
        for j, clo_b in enumerate(clos_data):
            if i != j and len(set(clo_a['plos']).intersection(set(clo_b['plos']))) > 0:
                similar.append(j)
        ground_truth[i] = similar
    
    # Jaccard similarity
    print("\nComputing Jaccard similarity...")
    jaccard_sim = np.zeros((len(clos_data), len(clos_data)))
    for i in range(len(clos_data)):
        for j in range(len(clos_data)):
            jaccard_sim[i, j] = jaccard_similarity(clos_data[i], clos_data[j])
    
    # TF-IDF similarity
    print("Computing TF-IDF similarity...")
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = tfidf.fit_transform(texts)
    tfidf_sim_matrix = cosine_similarity(tfidf_matrix)
    
    # BERT similarity
    print("Computing BERT similarity...")
    bert_model = SentenceTransformer('all-MiniLM-L6-v2')
    bert_embeddings = bert_model.encode(texts)
    bert_sim_matrix = cosine_similarity(bert_embeddings)
    
    # Evaluate at k=5
    k = 5
    results = {}
    
    for name, sim_matrix in [('Jaccard', jaccard_sim), ('TF-IDF', tfidf_sim_matrix), ('BERT', bert_sim_matrix)]:
        precisions = []
        recalls = []
        for i in range(len(clos_data)):
            if len(ground_truth[i]) == 0:
                continue
            scores = [(j, sim_matrix[i, j]) for j in range(len(clos_data)) if j != i]
            scores.sort(key=lambda x: x[1], reverse=True)
            top_k = [j for j, _ in scores[:k]]
            hits = len([j for j in top_k if j in ground_truth[i]])
            precisions.append(hits / k)
            recalls.append(hits / len(ground_truth[i]))
        
        results[name] = {
            'precision@5': np.mean(precisions),
            'recall@5': np.mean(recalls)
        }
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    for name, metrics in results.items():
        print(f"\n{name}:")
        print(f"  Precision@5: {metrics['precision@5']:.4f}")
        print(f"  Recall@5: {metrics['recall@5']:.4f}")
    
    os.makedirs('../output/evaluation', exist_ok=True)
    with open('../output/evaluation/similarity_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✓ Results saved to ../output/evaluation/similarity_results.json")

if __name__ == "__main__":
    main()