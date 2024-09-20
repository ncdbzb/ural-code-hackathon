from typing import Callable

from langchain_core.tools import Tool


def get_url_tool(func: Callable) -> Tool:
    url_tool = Tool(
        name='extracting_data_from_url',
        description='Принимает ссылку и извлекает данные из текста',
        func=func,
    )

    return url_tool


def get_pdf_tool(func: Callable) -> Tool:
    pdf_tool = Tool(
        name='extracting_data_from_pdf',
        description='Принимает ссылку на PDF файл и извлекает данные из текста',
        func=func,
    )

    return pdf_tool
