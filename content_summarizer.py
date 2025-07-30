"""
Web article processor for extracting and summarizing web/text file content using AI

# Default web mode (uses urls.txt)
python content_summarizer.py

# Web mode with custom files
python content_summarizer.py --mode web --input my_urls.txt --output my_summaries/

# Text file mode (default input.txt)
python content_summarizer.py --mode text

# Text file with custom input/output
python content_summarizer.py --mode text --input article.txt --output article_summary.md

"""
from bs4 import BeautifulSoup
import requests
import litellm
import os
import argparse


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


def read_text_file(filepath: str) -> str:
    """Read text content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""


def summarize_with_prompt(article_text: str) -> str:
    """Send article text to ChatGPT for summarization using the prompt template."""
    try:
        with open("prompt.txt", "r") as f:
            prompt_template = f.read()
        
        full_prompt = prompt_template.replace("{{ insert blog post or raw dev thread here }}", article_text)
        
        response = litellm.completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return ""


def process_urls_from_file(urls_file: str, output_dir: str = "summaries") -> None:
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
                f.write(f"# Summary for:\n{url}\n\n")
                f.write(summary)
                f.write("\n\n<br>\n")
            
            print(f"  Saved summary to {filepath}")
    
    except FileNotFoundError:
        print(f"Error: Could not find file {urls_file}")
    except Exception as e:
        print(f"Error processing URLs: {e}")


def process_text_file(text_file: str, output_file: str = None) -> None:
    """Process a single text file and save the summary."""
    print(f"Processing text file: {text_file}")
    
    # Read content
    article_text = read_text_file(text_file)
    if not article_text:
        print(f"Error: No content found in {text_file}")
        return
    
    # Summarize
    summary = summarize_with_prompt(article_text)
    if not summary:
        print(f"Error: Could not generate summary for {text_file}")
        return
    
    # Determine output filename
    if output_file is None:
        base_name = os.path.splitext(text_file)[0]
        output_file = f"{base_name}_summary.md"
    
    # Save summary
    with open(output_file, "w") as f:
        f.write(f"# Summary for: {text_file}\n\n")
        f.write(summary)
        f.write("\n")
    
    print(f"Saved summary to {output_file}")


def main():
    """Main function to run the content summarizer."""
    parser = argparse.ArgumentParser(description="Summarize web articles or text files using AI")
    parser.add_argument("--mode", choices=["web", "text"], default="web",
                       help="Processing mode: 'web' for URLs or 'text' for text file")
    parser.add_argument("--input", default=None,
                       help="Input file: URLs file for web mode, text file for text mode")
    parser.add_argument("--output", default=None,
                       help="Output location: directory for web mode, file for text mode")
    
    args = parser.parse_args()
    
    # Check if prompt.txt exists
    if not os.path.exists("prompt.txt"):
        print("Error: prompt.txt not found. Please create it with your summarization prompt.")
        print("Example content: 'Please summarize the following content:\n\n{{ insert blog post or raw dev thread here }}'")
        return
    
    if args.mode == "web":
        # Web mode: process URLs
        urls_file = args.input or "urls.txt"
        output_dir = args.output or "summaries"
        
        if not os.path.exists(urls_file):
            print(f"Creating sample {urls_file} file...")
            with open(urls_file, "w") as f:
                f.write("# Add URLs here, one per line\n")
                f.write("# Example:\n")
                f.write("# https://example.com/blog-post\n")
            print(f"Please add URLs to {urls_file} and run again.")
            return
        
        process_urls_from_file(urls_file, output_dir)
    
    else:
        # Text mode: process single text file
        text_file = args.input or "input.txt"
        
        if not os.path.exists(text_file):
            print(f"Error: Input file {text_file} not found.")
            print("Please specify a text file using --input or create input.txt")
            return
        
        process_text_file(text_file, args.output)


if __name__ == "__main__":
    main()
