import os
import openai
from config import OPENAI_KEY
openai.api_key = OPENAI_KEY
print(openai.Model.list())