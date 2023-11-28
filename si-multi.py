import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import openai
from cachetools import cached, TTLCache
from datetime import datetime
from serpapi import GoogleSearch

# Configuration and Constants
load_dotenv()
PROMPTS = [
    "unique selling proposition",
    "competitive position",
    "key messages",
    "target audience",
    "products or services",
    "financial statements",
    "industry rivals",
    "social media",
    "strategic opportunities",
    "recent news",
    "industry outlook"
]
cache = TTLCache(maxsize=100, ttl=3600)
openai_response_cache = TTLCache(maxsize=100, ttl=3600)

openai.api_key = os.getenv("OPENAI_API_KEY")

class SerpAPIWrapper:
    @cached(cache)
    def results(self, query: str) -> dict:
        params = {
            "q": query,
            "location": "United States",
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }
        search = GoogleSearch(params)
        return search.get_dict()

serpapi_wrapper = SerpAPIWrapper()

def summarize_serpapi_results(results):
    snippets = results.get("organic_results", [{}])
    snippet_texts = [entry.get("snippet", "") for entry in snippets[:3]] 
    return " ".join(snippet_texts)

def generate_prompt(role, question, serp_summary):
    return f"{role}: {question}\n\nSerpAPI Results: {serp_summary}"

previous_responses = []

async def fetch_response(prompt, serpapi_results):
    role = "research agents"
    question = f"Based on the provided search results, can you tell me the {prompt}?"
    serp_summary = summarize_serpapi_results(serpapi_results)
    
    if not serp_summary:
        return f"No relevant information found in the search results for {prompt}."
    
    generated_prompt = generate_prompt(role, question, serp_summary)
    return await generate_response(generated_prompt)

async def generate_response(generated_prompt):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided Results directly without adding additional comments."},
            {"role": "user", "content": generated_prompt}
        ]
        response = await loop.run_in_executor(executor, lambda: openai.ChatCompletion.create(
            model='gpt-4-1106-preview',
            messages=messages,
            max_tokens=150
        ))
    return response['choices'][0]['message']['content'].strip()


async def analyze_and_refine_responses(responses: list) -> list:
    async def refine_response(response):
        messages = [
            {"role": "system", "content": "You are an editor. Refine the content to be concise and clear, but ensure core information remains intact."},
            {"role": "user", "content": response}
        ]

        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            edit_response = await loop.run_in_executor(executor, lambda: openai.ChatCompletion.create(
                model='gpt-4-1106-preview',
                messages=messages,
                max_tokens=150
            ))
        
        return edit_response['choices'][0]['message']['content'].strip()

    return await asyncio.gather(*(refine_response(response) for response in responses))

def save_to_markdown(company, responses):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"logs/{company}_{current_datetime}.md"
    with open(filename, 'w') as file:
        file.write(f"# {company} Research - {current_datetime}\n\n")
        for prompt, response in zip(PROMPTS, responses):
            file.write(f"## {prompt}\n\n")
            file.write(f"{response}\n\n")
    print(f"Saved output to {filename}")

async def handle_user_input():
    company = input("What company would you like to learn about? ")
    if company:
        try:
            start_time = time.time()

            serpapi_results = serpapi_wrapper.results(company)
            tasks = [fetch_response(prompt, serpapi_results) for prompt in PROMPTS]  # Removed 'mode' argument
            responses = await asyncio.gather(*tasks)
            
            # Analyze and refine the responses
            refined_responses = await analyze_and_refine_responses(responses)
            
            for response in refined_responses:
                print(response)
            save_to_markdown(company, refined_responses)

            end_time = time.time()  # Record the end time
            total_time = end_time - start_time  # Calculate the total time

            print(f"Total time to generate markdown file: {total_time} seconds")

        except Exception as e:
            print(f"An error occurred while fetching information for {company}: {str(e)}")




def main():
    asyncio.run(handle_user_input())


if __name__ == "__main__":
    main()