# 📝 Summer Intern - Smart Research Assistant

Summer Intern is an business strategy agent, designed to serve as a quick research assistant for its users. Easily query specific information about brands and companies, fetching insights about their purpose, positioning, products, key messages, and more. The application uses GPT-4 combined with the capabilities of SerpAPI for real-time web search, ensuring accurate and timely data retrieval. As users input their queries, the app thoughtfully constructs relevant prompts, systematically dissecting the queried brand or company to provide a comprehensive analysis. 

## 📖 Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Support](#support)
4. [Dependencies](#dependencies)
5. [License](#license)

## 🚨 Features
- Search public sources to obtain company insights such as:
  - Brand Purpose
  - Value Proposition
  - Positioning
  - Target Audience
  - Customer Reviews
  - Products/Services
  - Key Messages
  - Company Size
  - Opportunities
  - Outlook
- Uses Streamlit for the UI.
- Caching results for efficiency.

## ⚙️ Installation

To get started locally, follow these instructions:
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/summer-intern.git
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Start the Streamlit app:
    ```bash
    streamlit run summerintern.py
    ```

## 🙌🏽 Support

If you find this project helpful, you can support by making a small donation. Every contribution will help keep the project running.

[Donate Here](https://buy.stripe.com/3cs02ge1AbbQ3h67sA)

## 🐐 Dependencies
- os
- streamlit
- datetime
- dotenv
- cachetools
- custom modules (like `langchain`)

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
