from bs4 import BeautifulSoup
import requests
import logging
import pandas as pd


namnyamURL = "https://www.nam-nyam.ru/catering/"

class foodItem:

    def __init__(self, title, weight, calories, price, link):
        self.title = title
        self.weight = weight
        self.calories = calories
        self.price = price
        self.link = link

    def __str__(self):
        return f"""
{self.title}
{self.weight}
{self.calories}
{self.price}
{self.link}\n
        """


def getDailyMenu(url: str):

    dailyMenu = {}
    dailyMenuSoup = BeautifulSoup(url, 'lxml')
    dailyMealTypes = dailyMenuSoup.find_all('div', class_='catering_item included_item')

    for mealType in dailyMealTypes:

        typeLabel = mealType.find('div', class_='catering_item_name catering_item_name_complex').text.strip()
        if not typeLabel:
            continue
        typeLabel+= f". {' '.join(mealType.find('div', class_='catering_item_price').text.split(' ')[1:])}"

        dailyMenu[typeLabel] = []

        foods = mealType.find('ul', class_='list_included_item').find_all('li')

        for item in foods:

            weight = '? гр.'
            calories = '? ккал'
            price = '? руб.'
            link = f"https://www.nam-nyam.ru{item.a['href']}"

            foodPage = requests.get(link).text
            foodPageSoup = BeautifulSoup(foodPage, 'lxml')

            match = foodPageSoup.find('div', class_='right_pos')

            title = match.find('h1').text.strip()

            if title == 'Страница не найдена':
                title = item.find('span', class_='complex_tooltip').text.strip()
                weight = ' '.join(item.find('span', class_='catering_item_weight').text.split(' ')[1:])
                dailyMenu[typeLabel].append(foodItem(title, weight, calories, price, link))
                continue

            item_desc = foodPageSoup.find('td', itemprop="offers")

            for line in item_desc.find_all('p'):
                if line.text.startswith("Вес: "):
                    weight = ' '.join(line.text.split(' ')[1:])
                elif line.text.startswith("Калорийность: "):
                    calories = f"{' '.join(line.text.split(' ')[1:])} ккал"

            price = ' '.join(item_desc.find('div', id="item_price_block").text.split(' ')[1:])

            dailyMenu[typeLabel].append(foodItem(title, weight, calories, price, link))

    return dailyMenu

try:
    dailyMenu = getDailyMenu(requests.get(namnyamURL).text)
    dailyMenu = {k: [f'{x.title}, {x.weight}, {x.calories}, {x.price}' for x in v] for k, v in dailyMenu.items()}

    columns = [pd.Series(foods, name=mealType) for mealType, foods in dailyMenu.items()]

    writer = pd.ExcelWriter("result.xlsx", engine='xlsxwriter') # pylint: disable=abstract-class-instantiated

    result = pd.concat(columns, axis=1)
    result.to_excel(writer, sheet_name='Main', index=False)

    worksheet = writer.sheets['Main']
    worksheet.set_column('A:D', 50, None)

    writer.save()

    print('.xlsx created')
except Exception:
    logging.exception('e')
