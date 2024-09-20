# HDS DEEP HACK BOT
___
## Инструкция по развертыванию
### 1. Убедитесь, что Docker и Docker Compose установлены

   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

### 2. Клонируйте репозиторий


   ```bash
   git clone https://github.com/ncdbzb/hds-deep-hack.git
   ```

### 3. Переменные окружения
Создайте файл `.env` в корневой директории и добавьте в него следующую информацию:

```plaintext
BOT_TOKEN=токен_телеграм_бота
AU_DATA=авторизационные_данные
```    
    

### 4. Запуск

   ```bash
   docker compose up
   ```
Теперь вы можете написать нашему боту в telegram!
https://t.me/DeepHack_HDS_bot

### 5. Использование
После команды /start отправьте боту ссылку на статью или ссылку на pdf файл, например:<br>
- https://www.influenza.spb.ru/files/File/metodptichgripp.pdf<br>
В ответ получите библиографическое описание источника