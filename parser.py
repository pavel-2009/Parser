import requests
from bs4 import BeautifulSoup
import json
import lxml

url = 'https://www.cbr.ru/currency_base/daily/'
headers = {
    'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
}


def get_data(currency='Доллар США'):  # получаем данные о курсах валют
    try:
        # загружаем страницу с сайта НБ РФ
        response = requests.get(url, headers=headers)

        if response.status_code != 200:        # в случае ошибки - вызываем исключение
            raise Exception(
                f'Ошибка загрузки страницы: {response.status_code}')

        # создаем объект BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        table_wrapper = soup.find('div', class_='table-wrapper')
        if not table_wrapper:
            raise ValueError("Не найдено div с классом 'table-wrapper'")

        table_div = table_wrapper.find('div', class_='table')
        if not table_div:
            raise ValueError("Не найдено div с классом 'table'")

        # находим на странице таблицу с курсами валют
        table = table_div.find('table')
        if not table:
            raise ValueError("Не найдено table внутри div с классом 'table'")

        # список, в который мы будем загружать словари с данными о курсах валют
        data_list = []
        # находим все строки без первых двух столбцов (кодами валюты и буквенными обозначениями)
        rows = table.find_all('tr')[2:]
        for row in rows:
            cols = row.find_all(['td', 'th'])     # находим ячейки строк
            if len(cols) >= 3:
                quantity = cols[2].get_text().strip()
                currency_value = cols[3].get_text().strip()
                rate = cols[4].get_text().strip()
                # сохраняем данные о количестве единиц валюты, названии и курсе валюты
                data_list.append({                     # записываем эти данные в виде словаря
                    'Количество': quantity,
                    'Валюта': currency_value,
                    'Курс': rate
                })

        with open('data.json', 'w', encoding='utf-8') as file:
            # записываем все в json-файл
            json.dump(data_list, file, indent=4, ensure_ascii=False)

        with open('data.json', 'r', encoding='utf-8') as file:        # открываем json-файл с курсами
            json_data = json.load(file)
            for item in json_data:
                # проверяем, совпадает ли строка, введенная нами, с названием валюты или содержится ли она в названии
                if item['Валюта'].lower() == currency.lower() or currency.lower() in item['Валюта'].lower():
                    return (str(item['Количество']) + ' ' + item['Валюта'] + ' - ' + item['Курс'] + 'RUB')

        return 'Указанная валюта не найдена'

    except requests.RequestException as e:        # обрабатываем ошибки
        print(f"Произошла ошибка при выполнении запроса: {e}")
        return None
    except FileNotFoundError:
        print("Файл не найден!")
        return None
    except Exception as ex:
        print(f"Непредвиденная ошибка: {ex}")
        return None


def main():
    get_data()


if __name__ == '__main__':
    main()
