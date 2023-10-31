import os
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
    "brand purpose",
    "value proposition",
    "company positioning",
    "company key messages",
    "target audience",
    "customer reviews",
    "products or services",
    "leadership team",
    "company size",
    "strategic opportunities",
    "industry outlook"
]
cache = TTLCache(maxsize=100, ttl=3600)
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
    return "{role}: {question}\n\nSerpAPI Results: {serp_summary}".format(
        role=role, question=question, serp_summary=serp_summary)


async def fetch_response(prompt, serpapi_results, mode="analysis"): 
    role = "research agents"
    question = "Based on the provided search results, can you tell me the {}?".format(prompt)
    serp_summary = summarize_serpapi_results(serpapi_results)
    
    if not serp_summary:
        return "No relevant information found in the search results for {}.".format(prompt)
    
    if mode == "analysis":
        generated_prompt = generate_prompt(role, question, serp_summary)
    else:
        prompt_template = "{role}: {question}\n\nSerpAPI Results: {serp_summary}"
        generated_prompt = prompt_template.format(role=role, question=question, serp_summary=serp_summary)
    
    return await generate_response(generated_prompt)


async def generate_response(generated_prompt):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided SerpAPI Results directly without adding additional comments about the nature of the search results or browsing limitations."},
            {"role": "user", "content": generated_prompt}
        ]
        response = await loop.run_in_executor(executor, lambda: openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k',
            messages=messages,
            max_tokens=150
        ))
    return response['choices'][0]['message']['content'].strip()

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


async def analyze_and_refine_responses(responses: list) -> list:
    """
    Analyze and refine the given responses for redundancy and conciseness.
    """
    refined_responses = []
    
    for response in responses:
        messages = [
            {"role": "system", "content": "You are an editor. Please refine the following content to remove redundancy and make it concise."},
            {"role": "user", "content": response}
        ]
        
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            edit_response = await loop.run_in_executor(executor, lambda: openai.ChatCompletion.create(
                model='gpt-3.5-turbo-16k',
                messages=messages,
                max_tokens=150
            ))
        
        refined_responses.append(edit_response['choices'][0]['message']['content'].strip())
        
    return refined_responses


async def handle_user_input():
    company = input("What company would you like to learn about? ")
    if company:
        try:
            serpapi_results = serpapi_wrapper.results(company)
            tasks = [fetch_response(prompt, serpapi_results, mode="analysis") for prompt in PROMPTS]
            responses = await asyncio.gather(*tasks)
            
            # Analyze and refine the responses
            refined_responses = await analyze_and_refine_responses(responses)
            
            for response in refined_responses:
                print(response)
            save_to_markdown(company, refined_responses)
        except Exception as e:
            print(f"An error occurred: {e}")



def main():
    asyncio.run(handle_user_input())


if __name__ == "__main__":
    main()