# Recipe Dataset Scraper & Formatter

A Python tool that scrapes recipe websites and formats the data into Alpaca-style instruction datasets for AI fine-tuning.

## Features

- 🔍 Crawls recipe websites to find recipe links
- 📝 Scrapes recipe content and formats it into instruction-input-output pairs
- 🤖 Uses OpenAI's API to generate diverse training examples
- 💾 Saves data in JSONL format compatible with most fine-tuning frameworks

## Prerequisites

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Imagineer99/GPT-Recipe-Scraper
cd GPT-Recipe-Scraper
```

2. Install required packages:
```bash
pip install requests beautifulsoup4 openai
```

3. Set up your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

1. Basic usage:
```python
from scraper import WebsiteScraperAlpacaFormatter

base_url = 'https://your-recipe-website.com'
scraper = WebsiteScraperAlpacaFormatter(base_url, os.getenv('OPENAI_API_KEY'))

scraper.process_multiple_recipes(
    num_pairs_per_recipe=5,
    max_recipes=10,
    output_filename='recipe_dataset.jsonl'
)
```

2. The script will:
   - Find recipe links on the website
   - Scrape recipe content
   - Generate instruction-input-output pairs
   - Save the data in JSONL format

## Output Format

The script generates data in Alpaca format:
```json
{
    "instruction": "You are a chef who is an expert in Italian cuisine...",
    "input": "What is the best way to cook pasta carbonara?",
    "output": "# Classic Pasta Carbonara\n\n## Ingredients\n..."
}
```

## Configuration

You can customize the following parameters:
- `num_pairs_per_recipe`: Number of instruction pairs to generate per recipe
- `max_recipes`: Maximum number of recipes to process
- `max_links`: Maximum number of recipe links to collect

## Best Practices

- Be respectful of website rate limits
- Verify you have permission to scrape target websites
- Review generated instruction pairs for quality
- Consider adding error handling for specific website structures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

Please ensure you have permission to scrape your target websites and comply with their terms of service and robots.txt files.
