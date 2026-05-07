#!/usr/bin/env python3
"""
Load CLO-PLO Dataset
Loads and processes the CLO-PLO dataset from Zaki et al.
"""

import pandas as pd
import numpy as np
import json
import os
import sys

def load_clo_plo_dataset(data_path="/content/CLO-PLO-main"):
    """
    Load the complete CLO-PLO dataset.
    
    Args:
        data_path: Path to the CLO-PLO-main directory
    
    Returns:
        dict: Dictionary containing CLOs, PLOs, and mappings
    """
    try:
        cs_courses = pd.read_excel(f"{data_path}/Course-Mappings-CompScience.xlsx")
        infosec_courses = pd.read_excel(f"{data_path}/Course-Mappings-InfoSecurity.xlsx")
        cs_mapping = pd.read_csv(f"{data_path}/Original-Mapping-ComputerScience.csv")
        infosec_mapping = pd.read_csv(f"{data_path}/Original-Mapping-InfoSecurity.csv")
    except FileNotFoundError as e:
        print(f"Error: Could not load dataset from {data_path}")
        print("Please download from https://github.com/nzaki02/CLO-PLO")
        raise e
    
    result = {
        'cs_courses': cs_courses,
        'infosec_courses': infosec_courses,
        'cs_mapping': cs_mapping,
        'infosec_mapping': infosec_mapping,
        'clos': [],
        'plos': [],
        'clo_to_plo': {}
    }
    
    # Extract PLOs from mapping columns
    plo_set = set()
    for col in cs_mapping.columns:
        if col.startswith('P') and col[1:].isdigit():
            plo_set.add(f"PLO_{col}")
    for col in infosec_mapping.columns:
        if col.startswith('P') and col[1:].isdigit():
            plo_set.add(f"PLO_{col}")
    result['plos'] = sorted(list(plo_set))
    
    # Extract CLOs from CS courses
    cs_clo_index = 0
    for idx, row in cs_courses.iterrows():
        clo_text = row.get('Outcome')
        if pd.notna(clo_text) and isinstance(clo_text, str) and len(clo_text) > 20:
            # Extract PLO mappings from this row
            mapped_plos = []
            for plo_col in ['POL1', 'PLO2', 'POL3', 'POL4', 'PLO5', 'POL6']:
                if plo_col in cs_courses.columns and pd.notna(row[plo_col]):
                    val = str(row[plo_col]).strip().lower()
                    if val == 'x' or val == '1':
                        plo_name = f"PLO_{plo_col.replace('POL', '').replace('PLO', '').replace('2', '2')}"
                        mapped_plos.append(plo_name)
            
            clo_id = f"CS_CLO_{cs_clo_index}"
            result['clos'].append({
                'id': clo_id,
                'text': str(clo_text),
                'plos': mapped_plos,
                'source': 'CS',
                'course': row.get('Course Code and Title', 'Unknown')
            })
            result['clo_to_plo'][clo_id] = mapped_plos
            cs_clo_index += 1
    
    # Extract CLOs from InfoSec courses
    infosec_clo_index = 0
    for idx, row in infosec_courses.iterrows():
        clo_text = row.get('CLOs')
        if pd.notna(clo_text) and isinstance(clo_text, str) and len(clo_text) > 20:
            mapped_plos = []
            for plo_col in ['SO1', 'SO2', 'SO3', 'SO4', 'SO5', 'SO6']:
                if plo_col in infosec_courses.columns and pd.notna(row[plo_col]):
                    val = str(row[plo_col]).strip().lower()
                    if val == 'x' or val == '1':
                        plo_name = f"PLO_{plo_col.replace('SO', '')}"
                        mapped_plos.append(plo_name)
            
            if mapped_plos:  # Only keep if has PLO mappings
                clo_id = f"IS_CLO_{infosec_clo_index}"
                result['clos'].append({
                    'id': clo_id,
                    'text': str(clo_text),
                    'plos': mapped_plos,
                    'source': 'InfoSec',
                    'course': row.get('Course Code', 'Unknown')
                })
                result['clo_to_plo'][clo_id] = mapped_plos
                infosec_clo_index += 1
    
    return result

def extract_clo_with_plos(data, min_length=20):
    """
    Extract only CLOs that have PLO mappings.
    
    Args:
        data: Output from load_clo_plo_dataset()
        min_length: Minimum text length to keep
    
    Returns:
        list: CLOs with PLO mappings
    """
    clos_with_plos = []
    for clo in data['clos']:
        if len(clo['plos']) > 0 and len(clo['text']) >= min_length:
            clos_with_plos.append(clo)
    return clos_with_plos

def create_similarity_pairs(clos_data, random_seed=42):
    """
    Create positive and negative pairs for similarity training/evaluation.
    
    Args:
        clos_data: List of CLO dictionaries with 'text' and 'plos' keys
        random_seed: Random seed for reproducibility
    
    Returns:
        tuple: (positive_pairs, negative_pairs)
    """
    import random
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    positive_pairs = []
    negative_pairs = []
    
    # Create positive pairs (CLOs that share PLOs)
    for i in range(len(clos_data)):
        for j in range(i+1, len(clos_data)):
            plos_i = set(clos_data[i]['plos'])
            plos_j = set(clos_data[j]['plos'])
            if len(plos_i.intersection(plos_j)) > 0:
                positive_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 1.0))
    
    # Create negative pairs (CLOs that share no PLOs)
    for i in range(len(clos_data)):
        attempts = 0
        while len([p for p in negative_pairs if p[0] == clos_data[i]['text'] or p[1] == clos_data[i]['text']]) < 2:
            j = random.randint(0, len(clos_data)-1)
            while j == i:
                j = random.randint(0, len(clos_data)-1)
            plos_i = set(clos_data[i]['plos'])
            plos_j = set(clos_data[j]['plos'])
            if len(plos_i.intersection(plos_j)) == 0:
                negative_pairs.append((clos_data[i]['text'], clos_data[j]['text'], 0.0))
            attempts += 1
            if attempts > 100:
                break
    
    # Balance the dataset
    min_len = min(len(positive_pairs), len(negative_pairs))
    positive_pairs = positive_pairs[:min_len]
    negative_pairs = negative_pairs[:min_len]
    
    return positive_pairs, negative_pairs

def save_processed_data(data, output_dir="../output/data"):
    """
    Save processed data to CSV files.
    
    Args:
        data: Output from load_clo_plo_dataset()
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save CLOs
    clos_df = pd.DataFrame(data['clos'])
    clos_df.to_csv(f"{output_dir}/clos.csv", index=False)
    
    # Save PLOs
    plos_df = pd.DataFrame({'plo_id': data['plos']})
    plos_df.to_csv(f"{output_dir}/plos.csv", index=False)
    
    # Save mapping
    mapping_df = pd.DataFrame([
        {'clo_id': clo_id, 'plo_id': plo}
        for clo_id, plos in data['clo_to_plo'].items()
        for plo in plos
    ])
    mapping_df.to_csv(f"{output_dir}/clo_plo_mapping.csv", index=False)
    
    print(f"Saved processed data to {output_dir}")
    print(f"  - clos.csv: {len(data['clos'])} CLOs")
    print(f"  - plos.csv: {len(data['plos'])} PLOs")
    print(f"  - clo_plo_mapping.csv: {len(mapping_df)} mappings")

def main():
    """Main entry point for testing"""
    print("=" * 70)
    print("CLO-PLO Data Loader")
    print("=" * 70)
    
    # Load dataset
    data = load_clo_plo_dataset()
    print(f"\nLoaded {len(data['clos'])} CLOs")
    print(f"Loaded {len(data['plos'])} PLOs")
    
    # Extract CLOs with PLO mappings
    clos_with_plos = extract_clo_with_plos(data)
    print(f"CLOs with PLO mappings: {len(clos_with_plos)}")
    
    # Create similarity pairs
    pos_pairs, neg_pairs = create_similarity_pairs(clos_with_plos)
    print(f"Positive pairs: {len(pos_pairs)}")
    print(f"Negative pairs: {len(neg_pairs)}")
    
    # Save processed data
    save_processed_data(data)
    
    # Print sample
    print("\nSample CLOs:")
    for clo in clos_with_plos[:3]:
        print(f"  {clo['id']}: {clo['text'][:80]}...")
        print(f"    PLOs: {clo['plos']}")

if __name__ == "__main__":
    main()