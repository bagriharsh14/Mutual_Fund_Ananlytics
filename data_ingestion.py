# data_ingestion.py
import os
import glob
import pandas as pd

def ingest_and_inspect_data():
    raw_path = os.path.join("data", "raw")
    csv_files = glob.glob(os.path.join(raw_path, "*.csv"))
    
    print(f"\n==========================================")
    print(f"LOADING & INSPECTING {len(csv_files)} CSV DATASETS")
    print(f"==========================================\n")
    
    datasets = {}

    for file_path in sorted(csv_files):
        file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path)
        datasets[file_name] = df
        
        print(f"Dataset Name: {file_name}")
        print(f"• Shape (rows, cols) : {df.shape}")
        print(f"• Data Types:\n{df.dtypes.to_string()}")
        print(f"• Head (First 3 Rows):\n{df.head(3).to_string(index=False)}")
        
        # Anomaly Detection
        nulls = df.isnull().sum()
        missing_cols = nulls[nulls > 0]
        duplicates = df.duplicated().sum()
        
        if len(missing_cols) > 0 or duplicates > 0:
            print(f"• Anomalies Noted:")
            if len(missing_cols) > 0:
                print(f"  - Missing values: {missing_cols.to_dict()}")
            if duplicates > 0:
                print(f"  - Duplicate rows: {duplicates}")
        else:
            print(f"• Anomalies Noted: None (Clean)")
            
        print("-" * 60 + "\n")

    return datasets

def explore_fund_master(datasets):
    print("==========================================")
    print("EXPLORING FUND MASTER")
    print("==========================================")
    
    fm = datasets.get("01_fund_master.csv")
    if fm is not None:
        print(f"• Unique Fund Houses ({fm['fund_house'].nunique()}): {fm['fund_house'].unique().tolist()}")
        print(f"• Unique Categories ({fm['category'].nunique()}): {fm['category'].unique().tolist()}")
        print(f"• Unique Sub-Categories ({fm['sub_category'].nunique()}): {fm['sub_category'].unique().tolist()}")
        print(f"• Unique Risk Grades ({fm['risk_category'].nunique()}): {fm['risk_category'].unique().tolist()}")
    else:
        print("fund_master.csv not found.")
    print("-" * 60 + "\n")

def validate_amfi_codes(datasets):
    print("==========================================")
    print("AMFI CODE REFERENTIAL INTEGRITY VALIDATION")
    print("==========================================")
    
    fm = datasets.get("01_fund_master.csv")
    nav = datasets.get("02_nav_history.csv")

    if fm is not None and nav is not None:
        master_codes = set(fm["amfi_code"].unique())
        nav_codes = set(nav["amfi_code"].unique())
        
        missing_in_nav = master_codes - nav_codes
        
        print(f"• Total AMFI Codes in Fund Master : {len(master_codes)}")
        print(f"• Total AMFI Codes in NAV History  : {len(nav_codes)}")
        
        print("\n--- DATA QUALITY SUMMARY ---")
        if len(missing_in_nav) == 0:
            print("STATUS: PASSED")
            print("SUMMARY: Every scheme code present in fund_master exists in nav_history.")
        else:
            print("STATUS: FAILED / ANOMALY DETECTED")
            print(f"SUMMARY: Found {len(missing_in_nav)} scheme codes in fund_master missing from nav_history.")
            print(f"Missing Codes: {missing_in_nav}")
    print("==========================================\n")

if __name__ == "__main__":
    loaded_data = ingest_and_inspect_data()
    explore_fund_master(loaded_data)
    validate_amfi_codes(loaded_data)