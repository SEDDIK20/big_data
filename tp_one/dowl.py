import os
import requests
import time
import random

folder_path = r"C:\Users\ounz\Desktop\TP_scrping"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

base_url = "https://www.amazon.com/s?k=Nintendo+Switch+Games&rh=n%3A16227133011&_encoding=UTF8&pf_rd_p=39fc32bd-755e-448d-add5-8e4518ce2470&pf_rd_r=PTK891CPHKHF1ERXKW06&ref=cct_cg_purimil_3b1"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.251"
]

session = requests.Session()

for i in range(1, 400):
    url = f"{base_url}&page={i}"
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        file_path = os.path.join(folder_path, f"page_{i}.html")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"تم حفظ الصفحة {i} في {file_path}")
    else:
        print(f"فشل تنزيل الصفحة {i} من {url}، رمز الحالة: {response.status_code}")
        

    
    time.sleep(1)
