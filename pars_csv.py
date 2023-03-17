import requests
from bs4 import BeautifulSoup

from multiprocessing import Pool
from datetime import datetime
import csv
from config import CSV_FILE_NAME


def get_html(URL): 
    # Делать запрос по ссылке и возвращать html код этой страницы
    response = requests.get(URL)
    return response.text


def get_posts_links(html):
    links = []
    soup = BeautifulSoup(html, "html.parser")
    table_data = soup.find("div", {"class":"search-results-table"})
    data = table_data.find("div", {"class":"table-view-list"})
    posts = data.find_all("div", {"class":"list-item"})
    for p in posts:
        href=p.find("a").get("href")
        full_url = "https://www.mashina.kg"+href
        links.append(full_url)
    return links # возвращает ссылки на детальную страницу постов

def get_detail_post(html, post_url):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", {"class":"details-wrapper"})
    detail = content.find("div",{"class":"details-content"})
    title = detail.find("div", {"head-left"}).find("h1").text
    som = detail.find("div", {"class":"sep main"}).find("div",{"class":"price-som"}).text
    dollar = detail.find("div", {"class":"sep main"}).find("div",{"class":"price-dollar"}).text
    add_price = detail.find("div",{"class":"sep addit"}).find_all("div")
    tenge = add_price[1].text
    ruble = add_price[0].text
    mobile = detail.find("div",{"class":"details-phone-wrap"})
    mobile = mobile.find("div",{"class":"number"}).text
    description = detail.find("h2", {"class":"comment"}).text
    som = int(som.replace("сом", "").strip().replace(" ", ""))
    dollar = int(dollar.replace("$", "").strip().replace(" ", ""))
    data = {
        "title":title,
        "som":som,
        "dollar":dollar,
        "mobile":mobile,
        "description":description,
        "link":post_url
    }
    return data

def get_lp_number(html):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", {"class":"search-results-table"})
    ul = content.find("ul", {"class":"pagination"})
    lp = ul.find_all("a", {"class":"page-link"})[-1]
    n=lp.get("data-page")
    return int(n)

def write_data(data): 
    with open(CSV_FILE_NAME, "a", encoding="utf-8") as file:
        headers = ["title", "mobile", "dollar", "som", "link", "description"]
        writer = csv.DictWriter(file , fieldnames=headers)
        writer.writerow(data)




def write_header_csv():
    with open(CSV_FILE_NAME, "w", encoding="utf-8") as file:
        headers = ["title", "mobile", "dollar", "som", "link", "description"]
        writer = csv.DictWriter(file , fieldnames=headers)
        writer.writeheader()


def get_parse_page(page):
    URL_MAIN = "https://www.mashina.kg/search/all/all/"
    filter = "?currency=2&price_to=10000&region=1&sort_by=upped_at+desc&steering_wheel=1&town=2"
    FULL_URL = URL_MAIN + filter
    print(f"Парсинг страницы:{page}")
    FULL_URL += f"&page={page}"
    html = get_html(FULL_URL)
    post_links = get_posts_links(html)
    for link in post_links:
        post_html = get_html(link)
        post_data = get_detail_post(post_html, post_url=link)
        write_data(data=post_data)

def main():
    write_header_csv()
    start = datetime.now()
    passed_posts=0
    URL_MAIN = "https://www.mashina.kg/search/all/all/"
    filter = "?currency=2&price_to=10000&region=1&sort_by=upped_at+desc&steering_wheel=1&town=2"
    FULL_URL = URL_MAIN + filter
    last_page = get_lp_number(get_html(FULL_URL))
    with Pool(40) as p:
        p.map(get_parse_page, range(1, last_page+1))
    
    end = datetime.now()
    print("Время выполнения: ", end-start)
    print("Количество постов , которые были пропущены: ", passed_posts)

if __name__=="__main__":
    main()