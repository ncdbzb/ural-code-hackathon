import requests
import os
from PyPDF2 import PdfReader


def parse_pdf(url: str) -> str:
    try:
        response = requests.get(url)
    except requests.RequestException:
        return 'Произошла ошибка парсинга'
    file_name = 'pdf_file.pdf'
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    pdf_file = open(file_name, 'rb')
    pdf_reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()

    pdf_file.close()
    os.remove(file_name)

    return text
