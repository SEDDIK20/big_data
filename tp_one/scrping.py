import os
import csv
from bs4 import BeautifulSoup

folder_path = r"C:\Users\ounz\Desktop\TP_scrping"

with open(os.path.join(folder_path, "games_data.csv"), mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["اسم اللعبة", "السعر", "التقييم", "رابط المنتج"])

    for i in range(1, 400):
        file_path = os.path.join(folder_path, f"page_{i}.html")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
                
                game_items = soup.find_all('div', {'class': 's-result-item'})

                for game in game_items:
                    try:
                        name = game.find('h2').text.strip()
                        price = game.find('span', {'class': 'a-price-whole'}).text.strip() if game.find('span', {'class': 'a-price-whole'}) else "غير موجود"
                        rating = game.find('span', {'class': 'a-icon-alt'}).text.strip() if game.find('span', {'class': 'a-icon-alt'}) else "لا يوجد تقييم"
                        link = "https://www.amazon.com" + game.find('a')['href'] if game.find('a') else "لا يوجد رابط"
                        
                        writer.writerow([name, price, rating, link])
                    except AttributeError:
                        continue

            print(f"تم استخراج البيانات من {file_path}")
        else:
            print(f"الملف {file_path} غير موجود.")
