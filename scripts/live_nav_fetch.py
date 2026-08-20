"""
live_nav_fetch.py - Live NAV Fetcher & Cron Scheduler for Mutual Fund Analytics

Fetches current NAV data for specified AMFI scheme codes via the mfapi.in API,
saves individual CSV files to data/raw/ directory, and provides cron schedule helpers.

Bonus Challenge B1:
- Schedule ETL as a cron job auto-fetching NAV from mfapi.in every weekday at 8 PM:
  Crontab entry: 0 20 * * 1-5 python /path/to/scripts/live_nav_fetch.py >> /path/to/cron.log 2>&1

Usage:
    python scripts/live_nav_fetch.py
"""

import sys
import logging
from pathlib import Path
import requests
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

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
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("--- FETCHING INDIVIDUAL LIVE NAV DATA FROM MFAPI.IN ---")
    
    success_count = 0
    for code, file_prefix in SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                json_data = response.json()
                meta = json_data.get("meta", {})
                data = json_data.get("data", [])
                
                scheme_name = meta.get("scheme_name", "")
                fund_house = meta.get("fund_house", "")
                
                df = pd.DataFrame(data)
                df["scheme_code"] = code
                df["scheme_name"] = scheme_name
                df["fund_house"] = fund_house
                
                file_path = DATA_RAW_DIR / f"{file_prefix}_raw.csv"
                df.to_csv(file_path, index=False)
                
                logging.info(f"[OK] Saved {scheme_name} ({code}) -> '{file_path.name}' ({len(df)} records)")
                success_count += 1
            else:
                logging.warning(f"[FAIL] HTTP {response.status_code} for scheme {code}")
        except Exception as e:
            logging.error(f"[ERROR] Failed fetching scheme {code}: {e}")
            
    logging.info(f"Completed Live NAV Fetch: {success_count}/{len(SCHEMES)} successful.")


if __name__ == "__main__":
    fetch_and_save_individual_navs()
