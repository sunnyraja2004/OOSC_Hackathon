import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai
import os
from urllib.parse import urljoin
from sentence_transformers import SentenceTransformer, util

# Configure API and models
api_key = "YOUR_API_KEY_FOR_GEMINI" #for reference can use: AIzaSyCotfFeT5P1Rbr6n9IPuEgv3g10Ls5n91A
genai.configure(api_key=api_key)

model_gemini = genai.GenerativeModel('gemini-1.5-flash')
model_sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

# Ensure the directories exist before writing files
def ensure_directory_exists(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

# Function to check if the page is valid
def is_valid_page(response):
    """
    Check if the response URL or content indicates a login page, captcha, or JavaScript requirement.
    """
    invalid_keywords = ['login', 'silent-login', 'enable-js', 'captcha']
    for keyword in invalid_keywords:
        if keyword in response.url:
            return False

    # Check for captcha-related content in the response
    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.find(string=lambda text: text and ('captcha' in text.lower() or 'javascript' in text.lower())):
        return False

    return True

# Function to scrape the website and retrieve all links
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
    return links

# Function to save webpage content, generate questions, and find relevant links
def save_content_and_generate_questions(url, content_filepath, questions_filepath, site_map):
    try:
        response = requests.get(url)

        # Check if the page is valid based on the URL, headers, or response content
        if not is_valid_page(response):
            print(f"Skipping invalid page: {url}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all text from the webpage
        content = soup.get_text().strip()

        if not content:  # If content is empty, skip further processing
            print(f"No content found on the page: {url}")
            return

        # Ensure directories exist
        ensure_directory_exists(content_filepath)
        ensure_directory_exists(questions_filepath)

        # Save the content to a JSON file
        with open(content_filepath, 'w') as file:
            json.dump({'url': url, 'content': content}, file)

        # Generate questions using the Gemini API
        questions = generate_questions(content)

        # Find relevant links for each question
        relevant_links_for_questions = {}
        for question in questions:
            relevant_links_for_questions[question] = find_relevant_links(question, site_map)

        # Save the questions and relevant links to a separate JSON file
        with open(questions_filepath, 'w') as file:
            json.dump({'url': url, 'questions': relevant_links_for_questions}, file)

    except Exception as e:
        print(f"Error processing {url}: {e}")

# Function to generate questions using the Gemini API
def generate_questions(content, n=10):
    response = model_gemini.generate_content(
        f"Generate {n} concise questions under 80 characters from the following content:\n{content}\n"
    )

    result = response.text.strip() if hasattr(response, 'text') else response.content.strip()
    questions = [q.strip() for q in result.split('\n') if q.strip()]
    return questions

# Function to find relevant links for each question
def find_relevant_links(question, site_map):
    question_embedding = model_sentence_transformer.encode(question, convert_to_tensor=True)
    relevant_links = []

    for url, data in site_map.items():
        content_embedding = model_sentence_transformer.encode(data['content'], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(question_embedding, content_embedding)
        relevant_links.append((url, similarity.item()))

    # Sort by similarity and return top 2
    relevant_links.sort(key=lambda x: x[1], reverse=True)
    return [link for link, _ in relevant_links[:2]]

if __name__ == "__main__":
    website_url = "https://www.wsj.com/"
    links = scrape_website(website_url)

    site_map = {}

    # For each link, save the content, generate questions, and find relevant links in separate files
    for i, link in enumerate(links):
        if i > 100:  # Limiting to first 6 pages for the example
            break
        try:
            content_filepath = f'data/content/page_content_{i}.json'
            questions_filepath = f'data/questions/page_questions_{i}.json'

            # Scrape content, generate questions, and find relevant links
            save_content_and_generate_questions(link, content_filepath, questions_filepath, site_map)

            # Check if the content file was successfully created
            if os.path.exists(content_filepath):
                # Update the site map after processing each page
                with open(content_filepath, 'r') as file:
                    content_data = json.load(file)
                    site_map[link] = {'content': content_data['content']}
            else:
                print(f"Content not saved for {link}, skipping site map update.")

        except Exception as e:
            print(f"{i} Error processing {link}: {e}")
