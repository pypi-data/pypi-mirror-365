import os
import json
import time
import requests
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

session = None

def login(env_path):
    global session
    
    login_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://support.ferma.ai/main/login"
    }
    
    load_dotenv(dotenv_path=env_path)
    session = requests.Session()
    session.get("https://support.ferma.ai/main/login")

    login_data = {
        "username": os.getenv("FERMA_USERNAME"),
        "password": os.getenv("FERMA_PASSWORD")
    }
    response = session.post("https://support.ferma.ai/main/validate", data=login_data, headers=login_headers)
    
    if response.status_code == 200:
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_now}]: Ferma Support Portal Login successful")
        return session
    else:
        raise Exception(f"[{time_now}]: Login failed - Invalid credentials or server error")
    
def annotate(input_path, custom_needles_path=None, needles=[1, 1], entities=None, long_table=True, poll_interval=10, max_wait=300):
    global session
    time_now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if session is None:
        raise Exception("Session not initialized. Call login() first")
        
    if len(needles) != 2:
        raise ValueError("`NEEDLES` must be a list of two integers: [kb_status, nct_status]")

    kb_status, nct_status = needles
    ordered_needles = []
    if kb_status == 1:
        ordered_needles.append("kb")
    if nct_status == 1:
        ordered_needles.append("nct")

    use_custom = custom_needles_path and os.path.exists(custom_needles_path)
    if use_custom:
        ordered_needles.append("custom")

    files = {"input_csv": open(input_path, "rb")}
    
    input_df = pd.read_csv(input_path)
    if 'id' not in input_df.columns:
        raise ValueError("Error!! Input CSV file must contain `id` as one of the columns")
    
    if use_custom:
        files["custom_needles"] = open(custom_needles_path, "rb")

    form_data = {
        "ann_name": "Annt",
        "output_db": "annotations",
        "output_table_name": "Annt",
        "entities": json.dumps(entities) if entities else "",
        "needles": ordered_needles
    }

    resp = session.post("https://support.ferma.ai/annotation/csv-input", data=form_data, files=files)
    if resp.status_code != 200:
        raise Exception(f"[{time_now}]: Failed to initiate annotation")

    soup = BeautifulSoup(resp.text, "html.parser")
    trans_id = soup.find("input", {"name": "trans_id"})["value"]
    print(f"\n[{time_now}]: Annotation started, transaction ID: {trans_id}")

    tracker_url = f"https://support.ferma.ai/annotation/progress-tracker?trans_id={trans_id}"
    waited = 0

    while waited < max_wait:
        progress_html = session.get(tracker_url).text
        soup = BeautifulSoup(progress_html, "html.parser")

        try:
            total = int(soup.find("td", string="total").find_next_sibling("td").text.strip())
            completed = int(soup.find("td", string="completed").find_next_sibling("td").text.strip())
            print(f"⏳ {waited}s -> {completed}/{total} Completed")
            if total > 0 and completed >= total:
                break
        except Exception as e:
            print("Error parsing progress:", e)

        time.sleep(poll_interval)
        waited += poll_interval

    download_format = "long_table_format" if long_table else "pivot_table_format"
    payload = {"trans_id": trans_id, "format_type": download_format}
    download_resp = session.post("https://support.ferma.ai/annotation/progress-tracker", data=payload)

    if download_resp.headers.get("Content-Type", "").startswith("text/csv"):
        return pd.read_csv(BytesIO(download_resp.content), encoding='utf-8')
    else:
        raise Exception(f"[{time_now}]: Download failed or invalid format received")