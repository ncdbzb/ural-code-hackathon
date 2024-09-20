from bs4 import BeautifulSoup
import requests


def parse_web(url: str) -> str:
    try:
        response = requests.get(url)
    except requests.RequestException:
        return 'Произошла ошибка парсинга'
    body_text = ''
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        body_tag = soup.find('body')

        if body_tag:
            body_text = body_tag.get_text()[:5000]

    return body_text
