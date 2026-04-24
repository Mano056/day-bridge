from groq import Groq
from dotenv import load_dotenv
import os
#import anthropic
#from openai import OpenAI

load_dotenv()

def chat(provider, messages):
    if provider.lower() == "groq":
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        groq_message = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
        return groq_message.choices[0].message.content
    #elif provider.lower() == "openai":
        #return NotImplementedError("OpenAI provider is not implemented yet.")
    #elif provider.lower() == "anthropic":
        #return NotImplementedError("Anthropic provider is not implemented yet.")
    else:
        return "Invalid provider"
    
