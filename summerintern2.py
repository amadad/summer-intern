import os
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from cachetools import cached, TTLCache
#from langchain.agents import load_tools
import openai

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

# Adjust the cache size (maxsize) and expiration time (ttl) as needed
cache = TTLCache(maxsize=100, ttl=3600)

openai.api_key = os.getenv("OPENAI_API_KEY")

#tool_names = ["serpapi"]
#tools = load_tools(tool_names)

class SerpAPIWrapper:
    @cached(cache)
    def results(self, query: str) -> dict:
        """Run query through SerpAPI and return the raw result (with caching)."""
        # Import the GoogleSearch package from serpapi
        from serpapi import GoogleSearch
        
        # Set up the parameters for the search
        params = {
            "q": query,
            "location": "United States",
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }
        
        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Return the results
        return results

serpapi_wrapper = SerpAPIWrapper()

def setup_streamlit():
    """Setup Streamlit configuration."""
    st.set_page_config(page_title="Summer Intern", page_icon="📈")
    st.markdown("# Summer Intern")
    st.sidebar.header("Summer Intern")
    st.write("""Lightning briefings on companies and brands""")

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

def display_chat_history():
    """Display chat messages from history on app rerun."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def get_serpapi_results(query):
    """Get search results from SerpAPI."""
    # Implement the method to get results from SerpAPI
    return serpapi_wrapper.results(query)

def summarize_serpapi_results(results):
    """Summarize the results from SerpAPI."""
    # Implement the method to summarize the results
    # This is a placeholder implementation, replace it with the actual summarization logic
    summary = "Summary of the results: " + str(results)
    return summary

def handle_user_input():
    """Handle user input and display responses."""
    company = st.chat_input("What company would you like to learn about?")
    
    if company:
        st.session_state.messages.append({"role": "user", "content": company})
        with st.chat_message("user"):
            st.markdown(company)

        # Get search results from SerpAPI
        serpapi_results = serpapi_wrapper.results(company)

        response_summary = ""
        prompt_template = "{role}: {question} {company}?"

        for prompt in PROMPTS:
            # Generate the prompt using the template
            role = "brand strategist and analyst"
            question = "What is the {} of".format(prompt)
            generated_prompt = prompt_template.format(role=role, question=question, company=company)

            # Add SerpAPI results to the prompt
            generated_prompt += "\n\nSerpAPI Results: " + str(serpapi_results)

            # Run the agent with the generated prompt
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo-16k',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": generated_prompt}
                ]
            )
            result = response['choices'][0]['message']['content'].strip()
            response_summary += result + " "

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = str(result)
                response_so_far = ""
                for chunk in full_response.split():
                    response_so_far += chunk + " "
                    message_placeholder.markdown(response_so_far + "▌")
                    time.sleep(0.05)
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    setup_streamlit()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    display_chat_history()
    handle_user_input()

if __name__ == "__main__":
    main()