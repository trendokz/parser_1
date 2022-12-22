import requests
from bs4 import BeautifulSoup

import schedule


url = 'https://zeta.kz/'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 RuxitSynthetic/1.0 v3975717906 t6703941201591042144 athfa3c3975 altpub cvcv=2 smf=0"
}


def get_data():
    req = requests.get(url=url, headers=headers)
    req.encoding = 'UTF8'
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    # Сбор всех ссылок на каталоги
    categories_li = soup.find('ul', class_='i_v_menu j_v_menu').find_all('li', class_='i_vm_li_2 j_vm_li_2')
    dict_categ = []
    for li_2 in categories_li:
        if len(li_2.find_all('li', class_='i_vm_li_3 j_vm_li_3')) > 0:
            li_3_all = li_2.find_all('li', class_='i_vm_li_3 j_vm_li_3')
            for li_3 in li_3_all:
                if len(li_3.find_all('li', class_='i_vm_li_4 j_vm_li_4')) > 0:
                    li_4_all = li_3.find_all('li', class_='i_vm_li_4 j_vm_li_4')
                    for li_4 in li_4_all:
                        a_li_4 = li_4.find('a').get('href')
                        dict_categ.append(f'https://zeta.kz{a_li_4}?SHOWALL_1=1')
                else:
                    a_li_3 = li_3.find('a').get('href')
                    dict_categ.append(f'https://zeta.kz{a_li_3}?SHOWALL_1=1')
        else:
            a_li_2 = li_2.find('a').get('href')
            dict_categ.append(f'https://zeta.kz{a_li_2}?SHOWALL_1=1')

    # сбор карточек в каталогах
    dict_cards = [["Название", "Артикул", "Цена"]]
    sum_count = []
    k = 0
    for url1 in dict_categ:
        k += 1
        try:
            req1 = requests.get(url=url1, headers=headers)
            req1.encoding = 'UTF8'
            src1 = req1.text
            soup1 = BeautifulSoup(src1, 'lxml')

            all_cards = soup1.find('div', class_='i_catalog_border').find('div', class_='i_cs j_cs i_cs_tile')\
                .find_all('div', class_='i_item jq_item')

            count = 0
            for cards in all_cards:
                count += 1
                if len(cards.find('div', class_='i_ebuy').find_all('span', class_='i_price')) > 0:
                    price = f"{cards.find('div', class_='i_ebuy').find('span', class_='i_price').text}"
                    name_product = cards.find('a', class_='i_item_name').find('span').text
                    article_num = cards.find('a', class_='i_item_name').find('span', class_='i_article_item').text[9:]

                    dict_cards.append(
                        [
                            name_product,
                            article_num,
                            price
                        ]
                    )

            sum_count.append(count)

        except Exception as ex:
            print(ex)
            print(url1)

        print(k)

    print(sum(sum_count))
    google_table(dict_cards=dict_cards)


def google_table(dict_cards):
    import os.path

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # mail bot 'parsers@parsers-372008.iam.gserviceaccount.com'
    SAMPLE_SPREADSHEET_ID = '107SdHe8_dV6npe_dKE-7xA2QJgxz6ZOywOy-GZyrZX0'
    SAMPLE_RANGE_NAME = 'Zeta.kz'

    try:
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        # Чистим(удаляет) весь лист
        array_clear = {}
        clear_table = service.clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,
                                    body=array_clear).execute()

        # добавляет информации
        array = {'values': dict_cards}
        response = service.append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range=SAMPLE_RANGE_NAME,
                                  valueInputOption='USER_ENTERED',
                                  insertDataOption='OVERWRITE',
                                  body=array).execute()

    except HttpError as err:
        print(err)


def main():
    # start_time = datetime.datetime.now()

    schedule.every(55).minutes.do(get_data)

    while True:
        schedule.run_pending()

    # finish_time = datetime.datetime.now()
    # spent_time = finish_time - start_time
    # print(spent_time)


if __name__ == '__main__':
    main()
