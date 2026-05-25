import asyncio
import os
import time
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncOpenAI(
        api_key=os.getenv("NIM_API_KEY"),
        base_url=os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    )
    
    print("Sending request to meta/llama-3.1-8b-instruct...")
    start = time.time()
    try:
        response = await client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": "Hello, write a 1-sentence greeting."}],
            temperature=0.7,
            max_tokens=50
        )
        print("Response:", response.choices[0].message.content)
        print(f"Time taken: {time.time() - start:.2f}s")
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
