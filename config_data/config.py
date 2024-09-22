from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
AU_DATA = os.environ.get("AU_DATA")
YC_IAM_TOKEN = os.environ.get('YC_IAM_TOKEN')
YC_FOLDER_ID = os.environ.get('YC_FOLDER_ID')
