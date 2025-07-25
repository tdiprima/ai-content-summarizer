# Content Summarizer

A Python tool that extracts content from web pages and summarizes it using ChatGPT with a specialized prompt for developers.

Some code adapted from the article  [*"This ChatGPT Prompt Was So Good, I Saved It in 3 Places"*](https://medium.com/gitconnected/this-chatgpt-prompt-was-so-good-i-saved-it-in-3-places-6910bf07f3d2) by Maria Ali.

## Features

- Extracts readable text from web pages using `BeautifulSoup`
- Uses `litellm` for ChatGPT integration
- Processes multiple URLs from a text file
- Saves summaries as markdown files
- Specialized prompt for technical content analysis

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key:

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

1. Create a `urls.txt` file with URLs to process (one per line)
2. Run the script:

   ```bash
   python content_summarizer.py
   ```

3. Summaries will be saved in the `summaries/` directory

## Output Format

Each summary includes:

1. TL;DR (technical summary)
2. Code Patterns / Gotchas Mentioned
3. Things To Try Myself (small projects)
4. Related Concepts I Should Look Into
5. Python equivalents (if content is in other languages)

<br>
