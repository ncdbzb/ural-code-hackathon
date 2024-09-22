import time

from langchain.chains import LLMChain
import asyncio
from langchain_community.llms import YandexGPT
from langchain_core.prompts import PromptTemplate
from config_data.config import YC_FOLDER_ID, YC_IAM_TOKEN
import os
import re



# Настраиваем аутентификацию через переменные окружения (если еще не настроены)
os.environ["YC_IAM_TOKEN"] = YC_IAM_TOKEN
os.environ["YC_FOLDER_ID"] = YC_FOLDER_ID

# Настраиваем YandexGPT
llm = YandexGPT(model_uri='gpt://b1g67dbhtsk2c1ke5k9b/yandexgpt/latest', temperature=0)

template = """ 
Представь, что ты находишься на экзамене в вузе. 
Ты - профессиональный преподаватель в профильном институте. Тебе будет дан текст отчета студента и Вопрос к этому тексту. Ты должен ОТВЕТИТЬ на ВОПРОС ЧЁТКО и ЯСНО. 
Формат ответа СТРОГО: да/нет 
Вопрос: {question} 
Контекст: {context} 
Ответ: 
"""
# Инициализация шаблонов
prompt_template_intro = PromptTemplate(input_variables=["context", "question"], template=template)
prompt_template_concl = PromptTemplate(input_variables=["context", "question"], template=template)
prompt_template_que_int_con = PromptTemplate(input_variables=["context", "question"], template=template)

# Создаем цепочки для Введения, Заключения и анализа их соотношения
qa_chain_intro = LLMChain(llm=llm, prompt=prompt_template_intro)
qa_chain_concl = LLMChain(llm=llm, prompt=prompt_template_concl)
qa_chain_que_int_con = LLMChain(llm=llm, prompt=prompt_template_que_int_con)

questions_introduction = [
    "Современное состояние проблемы оценено? Да/Нет",
    "Имеются основания для разработки темы? Да/Нет",
    "Необходимость проведения НИР обоснована? Да/Нет",
    "Планируемый уровень разработки определен? Да/Нет",
    "Актуальность темы подтверждена? Да/Нет",
    "Новизна темы установлена? Да/Нет",
    "Связь с другими работами выявлена? Да/Нет",
    "Цель исследования определена? Да/Нет",
    "Объект и предмет исследования определены? Да/Нет"
]

questions_conclusion = [
    "Содержат ли работа или её этапы краткие выводы? Да/Нет",
    "Оценена ли полнота решений поставленных задач? Да/Нет",
    "Разработаны ли рекомендации и указаны ли исходные данные для конкретного использования результатов НИР? Да/Нет",
    "Представлены ли результаты оценки технико-экономической эффективности внедрения? Да/Нет",
    "Содержит ли работа оценку научно-технического уровня выполненной НИР в сравнении с лучшими достижениями в этой области? Да/Нет"
]

que_int_con = [
    "Заключение базируется на цели и задачах, выдвинутых во введении? Да/Нет"
]


# Функция для очистки ответа от пунктуации
def clean_answer(answer):
    return re.sub(r'[^\w\s]', '', answer).strip().lower()


# Функция для генерации исправления, если ответ "Нет"
def get_corrected_answer(question, context, qa_chain):
    prompt = f"""
    Тебе будет дан текст отчета студента, в котором обнаружена ошибка по вопросу "{question[:-6]}".
    Контекст: {context}
    Твоя задача: Написать исправленный вариант текста. Данный контекст ТОЧНО СОДЕРЖИТ ОШИБКУ. Текст нужно исправить так, чтобы он более ярко отражал вопрос.

    НАПИШИ ТОЛЬКО ИСПРАВЛЕНЫЙ ТЕКСТ И ВСЁ!! БОЛЬШЕ НИЧЕГО НЕ ПИШИ!!
    """
    return qa_chain.run({"context": context, "question": prompt})


# Функция анализа введения
async def analyze_introduction(introduction):
    answers = []
    for question in questions_introduction:
        answer_intro = qa_chain_intro.run({"context": introduction, "question": question})
        await asyncio.sleep(2)
        # Очистка ответа от лишней пунктуации
        cleaned_answer = clean_answer(answer_intro)
        if cleaned_answer == "нет":
            # Если ответ "Нет", получить исправление, используя qa_chain_intro
            text_help = get_corrected_answer(question, introduction, qa_chain_intro)
        else:
            text_help = ""  # Пустая строка, если исправление не нужно
        answers.append((cleaned_answer, text_help))
    return answers


# Функция анализа заключения
async def analyze_conclusion(concl):
    answers = []
    for question in questions_conclusion:
        answer_concl = qa_chain_concl.run({"context": concl, "question": question})
        await asyncio.sleep(2)
        # Очистка ответа от лишней пунктуации
        cleaned_answer = clean_answer(answer_concl)
        if cleaned_answer == "нет":
            # Получение исправления, используя qa_chain_concl
            text_help = get_corrected_answer(question, concl, qa_chain_concl)
        else:
            text_help = ""  # Пустая строка
        answers.append((cleaned_answer, text_help))
    return answers


# Функция анализа связи между введением и заключением
async def analyze_relationship(introduction, concl):
    answers = []
    combined_context = f"{introduction}\n\n{concl}"
    for question in que_int_con:
        answer_que_int_con = qa_chain_que_int_con.run({"context": combined_context, "question": question})
        await asyncio.sleep(2)
        # Очистка ответа от лишней пунктуации
        cleaned_answer = clean_answer(answer_que_int_con)
        if cleaned_answer == "нет":
            # Получить исправление, используя qa_chain_que_int_con
            text_help = get_corrected_answer(question, combined_context, qa_chain_que_int_con)
        else:
            text_help = ""  # Пустая строка
        answers.append((cleaned_answer, text_help))
    return answers


