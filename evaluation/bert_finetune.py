#!/usr/bin/env python3
"""
BERT Fine-tuning for CLO Similarity
Fine-tunes Sentence-BERT on the CLO-PLO similarity task
"""

import pandas as pd
import numpy as np
import random
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_clo_plo_data(data_path="/content/CLO-PLO-main"):
    """Load CLO descriptions and PLO mappings"""
    try:
        cs_courses = pd.read_excel(f"{data_path}/Course-Mappings-CompScience.xlsx")
        infosec_courses = pd.read_excel(f"{data_path}/Course-Mappings-InfoSecurity.xlsx")
    except FileNotFoundError:
        print("Error: CLO-PLO dataset not found.")
        return []
    
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

def create_pairs(clos_data, random_seed=42):
    """Create positive and negative pairs"""
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    positive_pairs = []
    for i in range(len(clos_data)):
        for j in range(i+1, len(clos_data)):
            if len(set(clos_data[i]['plos']).intersection(set(clos_data[j]['plos']))) > 0:
                positive_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 1.0))
    
    negative_pairs = []
    for i in range(len(clos_data)):
        for _ in range(2):
            j = random.randint(0, len(clos_data)-1)
            while j == i:
                j = random.randint(0, len(clos_data)-1)
            if len(set(clos_data[i]['plos']).intersection(set(clos_data[j]['plos']))) == 0:
                negative_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 0.0))
            if len(negative_pairs) >= len(positive_pairs):
                break
    
    min_len = min(len(positive_pairs), len(negative_pairs))
    positive_pairs = positive_pairs[:min_len]
    negative_pairs = negative_pairs[:min_len]
    
    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)
    
    return train_test_split(all_pairs, test_size=0.2, random_state=random_seed)

def main():
    print("=" * 70)
    print("BERT Fine-tuning for CLO Similarity")
    print("=" * 70)
    
    clos_data = load_clo_plo_data()
    if not clos_data:
        return
    
    print(f"\nLoaded {len(clos_data)} CLOs with PLO mappings")
    
    train_pairs, test_pairs = create_pairs(clos_data)
    print(f"Training pairs: {len(train_pairs)}")
    print(f"Test pairs: {len(test_pairs)}")
    
    train_examples = [InputExample(texts=[p[0], p[1]], label=p[2]) for p in train_pairs]
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    train_loss = losses.CosineSimilarityLoss(model)
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    
    print("\nStarting training (5-10 minutes)...")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=5,
        warmup_steps=100,
        show_progress_bar=True,
        output_path='./fine_tuned_clo_bert'
    )
    
    fine_tuned_model = SentenceTransformer('./fine_tuned_clo_bert')
    
    predictions = []
    true_labels = []
    for text1, text2, label in test_pairs:
        emb1 = fine_tuned_model.encode([text1])[0]
        emb2 = fine_tuned_model.encode([text2])[0]
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        predictions.append(sim)
        true_labels.append(label)
    
    thresholds = [0.5, 0.6, 0.7, 0.8]
    best_f1 = 0
    for t in thresholds:
        pred_binary = [1 if p >= t else 0 for p in predictions]
        precision = precision_score(true_labels, pred_binary, zero_division=0)
        recall = recall_score(true_labels, pred_binary, zero_division=0)
        f1 = f1_score(true_labels, pred_binary, zero_division=0)
        print(f"Threshold {t}: P={precision:.4f}, R={recall:.4f}, F1={f1:.4f}")
        if f1 > best_f1:
            best_f1 = f1
    
    print(f"\nBest F1: {best_f1:.4f}")
    
    os.makedirs('../output/evaluation', exist_ok=True)
    fine_tuned_model.save('../output/evaluation/fine_tuned_model')
    print("\n✓ Model saved to ../output/evaluation/fine_tuned_model")

if __name__ == "__main__":
    main()