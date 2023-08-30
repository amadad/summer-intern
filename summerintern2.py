import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from langchain.agents import load_tools, initialize_agent
from langchain.llms import OpenAI
from langchain.utilities import SerpAPIWrapper as BaseSerpAPIWrapper

# Load environment variables from .env file
load_dotenv()

# Adjust the cache size (maxsize) and expiration time (ttl) as needed
cache = TTLCache(maxsize=100, ttl=3600)

class SerpAPIWrapper(BaseSerpAPIWrapper):
    @cached(cache)
    def results(self, query: str) -> dict:
        """Run query through SerpAPI and return the raw result (with caching)."""
        return super().results(query)

def setup_agent():
    llm = OpenAI(
        model_name='gpt-4',
        temperature=0.0,
        max_tokens=200
    )
    tool_names = ["serpapi"]
    tools = load_tools(tool_names)
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    return agent

def generate_prompts(company, agent):
    prompt_template = "You are a {role}. {question} {company}"
    prompts = [
        "brand purpose",
        "value proposition",
        "company positioning",
        "target audience",
        "customer reviews",
        "products or services",
        "company key messages",
        "leadership team",
        "company size",
        "strategic opportunities",
        "industry outlook"
    ]
    response_summary = ""
    container = st.expander("Results")
    serpapi_wrapper = SerpAPIWrapper()
    for prompt in prompts:
        role = "brand strategist and analyst"
        question = "What is the {} of".format(prompt)
        generated_prompt = prompt_template.format(role=role, question=question, company=company)
        result = agent.run(generated_prompt)
        response_summary += result + " "
        with container:
            st.markdown(f"* {result}")
    final_prompt = "Summarize all the previous results for {}: ".format(company)
    final_prompt += response_summary
    final_result = agent.run(final_prompt)
    return final_result

def main():
    st.title(':memo: Summer Intern')
    st.subheader('Get smart quickly on brands and companies.')
    
    # Sidebar
    st.sidebar.title('About the app')
    st.sidebar.markdown("""
        Summer Intern is an experimental strategy agent that is your helpful researcher. Summer Intern will search public sources to return summaries on a given company's background.
        """)
    donate_button = '[Donate](https://buy.stripe.com/3cs02ge1AbbQ3h67sA)'
    st.sidebar.markdown(donate_button, unsafe_allow_html=True)

    # User input form
    with st.form("chat_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            company = col1.text_input("What company would you like to learn about?")
        submit_button = col2.form_submit_button("Send")

    if submit_button and company:
        agent = setup_agent()
        summary = generate_prompts(company, agent)
        st.write("Summary: ", summary)

if __name__ == "__main__":
    main()

