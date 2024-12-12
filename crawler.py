import requests
from bs4 import BeautifulSoup
import json
from openai import OpenAI
import os
import time

class WebsiteScraperAlpacaFormatter:
    def __init__(self, base_url, openai_api_key):
        """
        Initialize the scraper and formatter
        
        :param base_url: Base website URL to start crawling
        :param openai_api_key: OpenAI API key for text generation
        """
        self.base_url = base_url
        self.client = OpenAI(api_key=openai_api_key)
        self.visited_urls = set()
        
    def find_recipe_links(self, url, max_links=10):
        """
        Find recipe links from a given URL
        
        :param url: URL to search for recipe links
        :param max_links: Maximum number of links to return
        :return: List of recipe URLs
        """
        recipe_links = set()
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common patterns for recipe URLs
            recipe_patterns = [
                '/recipe/', '/recipes/', 
                'recipe-', 'recipes-',
                'cooking/', 'food/'
            ]
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = requests.compat.urljoin(url, href)
                
                # Check if URL matches recipe patterns and belongs to same domain
                if (any(pattern in href.lower() for pattern in recipe_patterns) and 
                    self.base_url in href and 
                    href not in self.visited_urls):
                    recipe_links.add(href)
                    if len(recipe_links) >= max_links:
                        break
            
        except requests.RequestException as e:
            print(f"Error finding recipe links: {e}")
        
        return list(recipe_links)
    
    def scrape_website(self):
        """
        Scrape the HTML content of the website
        
        :return: Extracted text content
        """
        try:
            # Send a GET request to the URL
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text (you might want to customize this based on the specific website)
            text_content = soup.get_text(separator=' ', strip=True)
            
            return text_content
        
        except requests.RequestException as e:
            print(f"Error scraping website: {e}")
            return None
    
    def generate_instruction_pairs(self, text_content, num_pairs=10):
        """
        Generate instruction-input-output pairs using OpenAI API
        
        :param text_content: Scraped text content
        :param num_pairs: Number of instruction pairs to generate
        :return: List of instruction pairs
        """
        instruction_pairs = []
        
        # Create a better system prompt
        system_prompt = """
        You are a culinary assistant that creates detailed instruction-input-output pairs for italian recipes.
        For each pair:
        1. Instruction should be a clear generalization of the task (like a system prompt)
        2. Input should contain relevant context or specific questions
        3. Output should be detailed, including ingredients, steps, or explanations in markdown format
        
        Make each pair unique and focus on different aspects (ingredients, preparation, cooking tips, variations, etc.)
        """
        
        for _ in range(num_pairs):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"""
                        Create a unique instruction-input-output pair based on this recipe: {text_content[:2000]}
                        
                        Format as:
                        INSTRUCTION: A generalised overview of the instructions for the recipe
                        INPUT: [Context or specific question]
                        OUTPUT: [Detailed response in markdown format]
                        
                        Make sure the output includes proper markdown formatting with lists, headers, or emphasis where appropriate.
                        """}
                    ]
                )
                
                # Extract and parse the generated content
                generated_content = response.choices[0].message.content
                parts = generated_content.split('INPUT:')
                
                if len(parts) == 2:
                    instruction = parts[0].replace('INSTRUCTION:', '').strip()
                    input_output = parts[1].split('OUTPUT:')
                    
                    if len(input_output) == 2:
                        input_text = input_output[0].strip()
                        output_text = input_output[1].strip()
                        
                        instruction_pairs.append({
                            "instruction": instruction,
                            "input": input_text,
                            "output": output_text
                        })
            
            except Exception as e:
                print(f"Error generating instruction pair: {e}")
        
        return instruction_pairs
    
    def save_to_jsonl(self, instruction_pairs, filename='alpaca_dataset.jsonl'):
        """
        Append instruction pairs to a JSONL file
        
        :param instruction_pairs: List of instruction pairs
        :param filename: Output filename
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        # Count existing entries if file exists
        existing_count = 0
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_count = sum(1 for _ in f)
        
        # Append new pairs
        with open(filename, 'a', encoding='utf-8') as f:
            for pair in instruction_pairs:
                f.write(json.dumps(pair) + '\n')
        
        print(f"Added {len(instruction_pairs)} instruction pairs to {filename} (now contains {existing_count + len(instruction_pairs)} total entries)")
    
    def process_multiple_recipes(self, num_pairs_per_recipe=5, max_recipes=10, output_filename='alpaca_dataset.jsonl'):
        """
        Process multiple recipes from the website
        
        :param num_pairs_per_recipe: Number of instruction pairs to generate per recipe
        :param max_recipes: Maximum number of recipes to process
        :param output_filename: Output filename for JSONL
        """
        recipe_links = self.find_recipe_links(self.base_url, max_recipes)
        
        for recipe_url in recipe_links:
            print(f"Processing recipe: {recipe_url}")
            self.url = recipe_url
            self.visited_urls.add(recipe_url)
            
            # Process this recipe
            text_content = self.scrape_website()
            if text_content:
                instruction_pairs = self.generate_instruction_pairs(text_content, num_pairs_per_recipe)
                self.save_to_jsonl(instruction_pairs, output_filename)
            
            # Small delay to be nice to the server
            time.sleep(2)

# Example usage
def main():
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    # Base URL for a recipe website
    base_url = 'https://www.bbcgoodfood.com/recipes/carbonara-arancini'
    
    scraper = WebsiteScraperAlpacaFormatter(base_url, OPENAI_API_KEY)
    
    # Process multiple recipes
    scraper.process_multiple_recipes(
        num_pairs_per_recipe=5,
        max_recipes=10,
        output_filename='website_alpaca_dataset.jsonl'
    )

if __name__ == '__main__':
    main()
