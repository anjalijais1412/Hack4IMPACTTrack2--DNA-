import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

PERSONAL_TOKEN = os.getenv("UIPATH_USER_KEY")
FOLDER_ID      = os.getenv("UIPATH_FOLDER_ID")
TENANT         = os.getenv("UIPATH_TENANT")
ACCOUNT        = os.getenv("UIPATH_ACCOUNT")

ORCH_URL = f"https://cloud.uipath.com/{ACCOUNT}/{TENANT}/orchestrator_"

BOTS = [
    ("Solution", {
        "in_BinDataPath": "http://localhost:5000/api/bins"
    }),
    ("Solution 1", {
        "in_AlertsFilePath": "http://localhost:5000/api/alerts"
    }),
    ("Solution 2", {
        "in_ApiBaseUrl": "http://localhost:5000/api/dashboard"
    }),
    ("Solution 3", {
        "in_EventsFilePath": "http://localhost:5000/api/reward"
    }),
]

def trigger_bot(name, args):
    headers = {
        "Authorization": f"Bearer {PERSONAL_TOKEN}",
        "Content-Type":  "application/json",
        "X-UIPATH-OrganizationUnitId": str(FOLDER_ID)
    }
    body = {
        "startInfo": {
            "ProcessKey":     name,
            "JobsCount":      1,
            "Strategy":       "ModernJobsCount",
            "InputArguments": json.dumps(args)
        }
    }
    url = (ORCH_URL +
           "/odata/Jobs/"
           "UiPath.Server.Configuration.OData.StartJobs")
    r = requests.post(url, headers=headers, json=body)
    if r.status_code in (200, 201):
        jid = r.json()["value"][0]["Id"]
        print(f"[OK] {name} started — Job ID: {jid}")
    else:
        print(f"[ERR] {name}: {r.status_code}")
        print(r.text[:300])

if __name__ == "__main__":
    if not PERSONAL_TOKEN or PERSONAL_TOKEN == "your_user_key_here":
        print("ERROR: Fill in UIPATH_USER_KEY in your .env file")
    else:
        print("Triggering all WATT_THE_WASTE! UiPath bots...")
        for name, args in BOTS:
            trigger_bot(name, args)
            time.sleep(2)
        print("Done.")



