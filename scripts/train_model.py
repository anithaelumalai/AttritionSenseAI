import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from utils.ml_pipeline import train_and_evaluate_model

def main():
    csv_path = os.path.join(PROJECT_ROOT, "data", "employees.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}. Run setup_data.py first.")
        sys.exit(1)
        
    print(f"Loading employee dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records.")
    
    print("Training Random Forest Classifier with balanced class weights...")
    pipeline, metadata = train_and_evaluate_model(df)
    
    print("\n" + "="*50)
    print("MODEL EVALUATION RESULTS")
    print("="*50)
    for metric, val in metadata["metrics"].items():
        if metric != "confusion_matrix":
            print(f"{metric.upper():<15}: {val:.4f}")
    print("\nTop 10 Most Influential Risk Predictors:")
    for rank, feat in enumerate(metadata["feature_ranking"][:10], 1):
        print(f"  {rank:>2}. {feat['feature']:<30}: {feat['importance']:.4f}")
    print("="*50)
    print("Training complete!")

if __name__ == "__main__":
    main()
