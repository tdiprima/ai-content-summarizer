# Content summarizer for web articles with specialized prompting
from bs4 import BeautifulSoup
import requests
import litellm
import os

PROMPT = """Create an engaging summary of this article that preserves the author's main point.
Style: Write like you're explaining it to a smart friend over coffee - clear, lively, but accurate.
If the topic is dry, add energy through word choice and pacing, not by inventing new content.
Length: 2-3 paragraphs that capture the essence.

Here's the content:
{content}"""


def extract_article_text(url: str) -> str:
    """Extract readable text content from a web page."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract paragraphs
        paragraphs = soup.find_all("p")
        article_text = "\n".join(p.get_text() for p in paragraphs)
        
        return article_text.strip()
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""


def summarize_with_prompt(article_text: str) -> str:
    """Send article text to AI for summarization."""
    try:
        full_prompt = PROMPT.format(content=article_text)
        
        response = litellm.completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return ""


def process_urls_from_file(urls_file: str, output_dir: str = "summaries1") -> None:
    """Process URLs from a text file and save summaries as markdown files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        with open(urls_file, "r") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        for i, url in enumerate(urls, 1):
            print(f"Processing URL {i}/{len(urls)}: {url}")
            
            # Extract content
            article_text = extract_article_text(url)
            if not article_text:
                print(f"  Skipping {url} - no content extracted")
                continue
            
            # Summarize
            summary = summarize_with_prompt(article_text)
            if not summary:
                print(f"  Skipping {url} - no summary generated")
                continue
            
            # Save summary
            filename = f"summary_{i:03d}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(f"**Source:** {url}\n\n")
                f.write(summary)
                f.write("\n\n<br>\n")
            
            print(f"  Saved summary to {filepath}")
    
    except FileNotFoundError:
        print(f"Error: Could not find file {urls_file}")
    except Exception as e:
        print(f"Error processing URLs: {e}")


def main():
    """Main function to run the content summarizer."""
    urls_file = "urls.txt"
    
    if not os.path.exists(urls_file):
        print(f"Creating sample {urls_file} file...")
        with open(urls_file, "w") as f:
            f.write("# Add URLs here, one per line\n")
            f.write("# Example:\n")
            f.write("# https://example.com/blog-post\n")
        print(f"Please add URLs to {urls_file} and run again.")
        return
    
    process_urls_from_file(urls_file)


if __name__ == "__main__":
    main()
