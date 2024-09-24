import redis
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

host = os.getenv('REDIS_HOST')
port = os.getenv('REDIS_PORT')

r = redis.Redis(host=host, port=port)