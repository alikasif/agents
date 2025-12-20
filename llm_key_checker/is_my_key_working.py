
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def is_key_working(key_prefix):

    print(f"\nchecking for {key_prefix}")
    print(f"\nAPI_KEY: {os.getenv(key_prefix+"_API_KEY")}")
    print(f"\nBASE_URL: {os.getenv(key_prefix+"_BASE_URL")}")
    print(f"\nMODEL: {os.getenv(key_prefix+"_MODEL")}")

    client = OpenAI(api_key=os.getenv(key_prefix+"_API_KEY"),
                    base_url=os.getenv(key_prefix+"_BASE_URL"))

    response = client.chat.completions.create(
        model=os.getenv(key_prefix+"_MODEL"),
        messages=[
            {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
        ]
    )

    print(f"\n\nresponse: {response.choices[0].message.content}")


is_key_working("GEMINI")
