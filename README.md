# 📝 Summer Intern - Smart Research Assistant

Summer Intern is a Streamlit application that acts as a strategy agent to help users get quick insights into brands and companies.

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Support](#support)
5. [Dependencies](#dependencies)
6. [License](#license)

## Features
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

## Installation

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
    streamlit run your_script_name.py
    ```

## Usage

1. Visit the Streamlit application.
2. Input a company name in the provided text field.
3. Click on the "Send" button to get smart summaries on the provided company's background.

## Support

If you find this project helpful, you can support by making a small donation. Every contribution will help keep the project running.

[Donate Here](https://buy.stripe.com/3cs02ge1AbbQ3h67sA)

## Dependencies
- os
- streamlit
- datetime
- dotenv
- cachetools
- custom modules (like `langchain`)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.