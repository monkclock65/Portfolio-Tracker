import os
from dotenv import load_dotenv
import finnhub

load_dotenv()
key = os.getenv('API_KEY')
print("KEY:", repr(key))

client = finnhub.Client(api_key=key)
print(client.quote('AAPL'))