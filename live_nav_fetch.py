import os
import requests
import pandas as pd

# Target AMFI Scheme Codes
SCHEMES = {
    "125497": "hdfc_125497",
    "119551": "sbi_119551",
    "120503": "icici_120503",
    "118632": "nippon_118632",
    "119092": "axis_119092",
    "120841": "kotak_120841"
}

def fetch_and_save_individual_navs():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("--- FETCHING INDIVIDUAL LIVE NAV DATA FROM MFAPI.IN ---")
    for code, file_prefix in SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url)
        
        if response.status_code == 200:
            json_data = response.json()
            meta = json_data.get("meta", {})
            data = json_data.get("data", [])
            
            # Extract metadata values (keys are strictly lowercase)
            scheme_name = meta.get("scheme_name", "")
            fund_house = meta.get("fund_house", "")
            
            # Parse daily NAV entries into DataFrame
            df = pd.DataFrame(data)
            df["scheme_code"] = code
            df["scheme_name"] = scheme_name
            df["fund_house"] = fund_house
            
            # Save individually without combining
            file_name = f"{file_prefix}_raw.csv"
            file_path = os.path.join(raw_dir, file_name)
            df.to_csv(file_path, index=False)
            
            print(f"[✓] Saved {scheme_name} ({code}) -> '{file_path}' ({len(df)} records)")
            print(f"    Fund House: {fund_house}")
        else:
            print(f"[X] Failed to fetch scheme code {code}: Status {response.status_code}")

if __name__ == "__main__":
    fetch_and_save_individual_navs()