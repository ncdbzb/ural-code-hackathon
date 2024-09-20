from config_data.config import AU_DATA
from gigachat.exceptions import ResponseError
from langchain.agents import AgentExecutor, create_gigachat_functions_agent
from langchain_community.chat_models.gigachat import GigaChat
from llm_agent.utils.web_parser import parse_web
from llm_agent.utils.pfd_parser import parse_pdf
from llm_agent.agent_tools.agent_tools import get_url_tool, get_pdf_tool
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)


class Bibliography:
    """
    Класс, создающий агента чат-бота, возвращающего библиографические описания источников
    """
    def __init__(self, user_query: str):
        self.giga = GigaChat(credentials=AU_DATA, verify_ssl_certs=False, scope="GIGACHAT_API_CORP",
                             model='GigaChat-Pro-preview', profanity_check=False, temperature=0)
        self.user_query = user_query

    def _parse_pdf(self):
        """
        Функция, которая загружает pdf документ по ссылке и парсит текст
        :return: (str) Текст из pdf документа
        """

        return parse_pdf(self.user_query)

    def _parse_url(self):
        """
        Функция парсит текст с url, полученного от пользователя
        :return: (str) Часть текста страницы
        """

        return parse_web(self.user_query)

    def _get_answer_from_url(self, input_data):
        prompt_tool = f"""
            Тебе предоставлен текст с веб-страницы, который послужил основой для написания научной статьи.
            Твоя задача состоит в определении типа веб-страницы, по содержащейся информации в данном тексте и в извлечении названия статьи,авторов статьи,года написания статьи из данного текста. Текст:{self._parse_url()}
            Максимальная длина ответа: 5 слов.
            Думай пошагово.
            Ответ дай строго в виде: Название статьи : тип -- автор, год написания -- URL : {self.user_query}, (дата обращения: 24.04.2024) — Текст : электронный.
            """

        try:
            response = self.giga.invoke(prompt_tool).content
        except ResponseError:
            response = 'Произошла ошибка, вероятно, отправленный вами источник слишком большой'
        return response

    def _get_answer_from_pdf(self, input_data):
        prompt_tool = f"""
            Тебе предоставлен текст с веб-страницы, который послужил основой для написания научной статьи.
            Твоя задача состоит в определении типа веб-страницы, по содержащейся информации в данном тексте и в извлечении названия статьи,авторов статьи,года написания статьи из данного текста. Текст:{self._parse_pdf()}
            Максимальная длина ответа: 5 слов.
            Думай пошагово.
            Ответ дай строго в виде: Название статьи : тип -- автор, год написания -- URL : {self.user_query}, (дата обращения: 24.04.2024) — Текст : электронный.
            """
        try:
            response = self.giga.invoke(prompt_tool).content
        except ResponseError:
            response = 'Произошла ошибка, вероятно, отправленный вами источник слишком большой'
        return response

    def _get_tools(self):
        """
        Функция создает инструменты агента
        :return: list[Tool]
        """

        tools = [
            get_url_tool(self._get_answer_from_url),
            get_pdf_tool(self._get_answer_from_pdf)
        ]

        return tools

    def execute_agent(self):
        """
        Функция, которая создает агента и вызывает его, используя запрос пользователя в качестве входных данных
        :return:
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Используй extracting_data_from_pdf, если на вход поступает ссылка .pdf, и extracting_data_from_url, если поступает НЕ .pdf. Возвращай слово в слово результат выполнения инструментов, ничего не меняй"),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        agent = create_gigachat_functions_agent(self.giga, self._get_tools(), prompt)

        agent_executor = AgentExecutor(agent=agent, tools=self._get_tools(),
                                       verbose=True, return_intermediate_steps=True)
        result = agent_executor.invoke({"input": self.user_query})

        return result['output']
