import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
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

llm = OpenAI(
    #model_name='gpt-3.5-turbo-16k',
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

# Page header
st.title(':memo: Summer Intern')
st.subheader('Get smart quickly on brands and companies.')

# Sidebar
st.sidebar.title('About the app')
st.sidebar.markdown("""
    Summer Intern is an experimental strategy agent that is your helpful researcher. Summer Intern will search public sources to return summaries on a given company's background: Brand Purpose, Value Proposition, Positioning, Target Audience, Customer Reviews, Products, Key Messages, Company size, Opportunities, Outlook.
    """)

st.sidebar.markdown('#### Support the project')
st.sidebar.markdown("""
    If you like this project and want to support it, please consider making a small donation.
    Every contribution helps keep the project running. Thank you!
    """)
donate_button = '[Donate](https://buy.stripe.com/3cs02ge1AbbQ3h67sA)'
st.sidebar.markdown(donate_button, unsafe_allow_html=True)

# User input form
with st.form("chat_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        company = col1.text_input(
            label="Your message:",
            placeholder="What company would you like to learn about?",
            label_visibility="collapsed",
        )
    submit_button = col2.form_submit_button("Send", use_container_width=True)

prompt_template = "You are a {role}. {question} {company}"

# Process user input and display results
if submit_button and company:
    # List of prompts
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

    # String for collecting all responses for the summarize prompt
    response_summary = ""

    # Create a container for the output
    container = st.expander("Results")

    # Instantiate the SerpAPIWrapper
    serpapi_wrapper = SerpAPIWrapper()

    # Iterate through each prompt
    for prompt in prompts:
        # Generate the prompt using the template
        role = "brand strategist and analyst"
        question = "What is the {} of".format(prompt)
        generated_prompt = prompt_template.format(role=role, question=question, company=company)

        # Run the agent with the generated prompt
        result = agent.run(generated_prompt)
        response_summary += result + " "

        with container:
            st.markdown(f"* {result}")

    # Add a final summary prompt
    final_prompt = "Summarize all the previous results for {}: ".format(company)
    final_prompt += response_summary
    final_result = agent.run(final_prompt)