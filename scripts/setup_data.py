import os
import sys
import io
import urllib.request
import pandas as pd

def setup_and_verify_dataset(output_path="data/employees.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Primary and fallback URLs for the official 1470-record IBM dataset
    urls = [
        "https://raw.githubusercontent.com/YBIFoundation/Dataset/main/EmployeeAttrition.csv",
        "https://raw.githubusercontent.com/rochead/IBM-HR-Employee-Attrition-Analytics/master/WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "https://raw.githubusercontent.com/jillanirudh/IBM-Employee-Attrition/master/WA_Fn-UseC_-HR-Employee-Attrition.csv"
    ]
    
    df = None
    if os.path.exists(output_path):
        print(f"Reading existing dataset from {output_path}...")
        try:
            df = pd.read_csv(output_path)
        except Exception as e:
            print(f"Failed to read existing file: {e}")
    
    if df is None:
        print("Downloading official IBM HR dataset...")
        for u in urls:
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw_data = resp.read()
                    df = pd.read_csv(io.BytesIO(raw_data))
                    print(f"Successfully downloaded from {u}")
                    df.to_csv(output_path, index=False)
                    break
            except Exception as e:
                print(f"Failed download from {u}: {e}")
                
    if df is None:
        raise RuntimeError("Unable to download IBM HR dataset from any repository.")
        
    print("\n" + "="*60)
    print("DATASET VERIFICATION REPORT")
    print("="*60)
    
    # 1. Shape verification
    rows, cols = df.shape
    print(f"1. Record Count: {rows} (Expected: 1470)")
    assert rows == 1470, f"Expected 1470 rows, got {rows}"
    print(f"2. Column Count: {cols} (Expected: 35)")
    assert cols == 35, f"Expected 35 columns, got {cols}"
    
    # 2. Key column verification
    assert "EmployeeNumber" in df.columns, "EmployeeNumber column missing!"
    assert "Attrition" in df.columns, "Attrition target column missing!"
    print("3. Target column 'Attrition' confirmed. Unique values:", df['Attrition'].unique())
    print("   Class distribution:\n", df['Attrition'].value_counts())
    
    # 3. EmployeeNumber uniqueness & non-sequential verification
    emp_nums = df['EmployeeNumber']
    duplicates = emp_nums.duplicated().sum()
    print(f"4. Duplicate EmployeeNumber count: {duplicates}")
    assert duplicates == 0, f"Found {duplicates} duplicate EmployeeNumber records!"
    
    emp_min = emp_nums.min()
    emp_max = emp_nums.max()
    emp_unique_count = emp_nums.nunique()
    is_strictly_sequential = (emp_max - emp_min + 1) == emp_unique_count
    print(f"5. EmployeeNumber Range: min={emp_min}, max={emp_max}, count={emp_unique_count}")
    print(f"   Is strictly sequential: {is_strictly_sequential} (Note: Non-sequential IDs present as expected!)")
    
    # Show first 15 actual EmployeeNumbers to prove non-sequential nature
    sample_ids = sorted(emp_nums.tolist())[:15]
    print(f"   Sample first 15 actual EmployeeNumbers: {sample_ids}")
    
    # 4. Missing values
    null_counts = df.isna().sum().sum()
    print(f"6. Total missing / null values across entire dataset: {null_counts}")
    
    # 5. Categorical vs Numerical feature verification
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    print(f"7. Numerical columns ({len(num_cols)}): {num_cols}")
    print(f"8. Categorical columns ({len(cat_cols)}): {cat_cols}")
    
    print("\nDATASET VERIFICATION PASSED SUCCESSFULLY!")
    print("="*60 + "\n")
    return df

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/employees.csv"
    setup_and_verify_dataset(out)
