# Web Scraper & Content Analyzer

<b> Problem Statement</b> <a href = "https://docs.google.com/document/d/1GaQza95lxQJHXrCtrdntavKL3a0_Bg_Kvj3QmZuDNWA/edit?usp=sharing">here.</a>

## Solution 

This Python script scrapes webpages, extracts content, generates relevant questions, and finds links with similar content. It processes multiple pages from a given website (e.g., "https://www.wsj.com/") and stores the results in structured JSON files.

## Features

1. **Webpage Scraping**: Extracts content from multiple links on the provided website.
2. **Question Generation**: Automatically generates 10 concise and relevant questions for each webpage using Google's Generative AI.
3. **Content Similarity Matching**: Finds the top 2 similar links from the website based on the content of each question.
4. **Error Handling**: Skips invalid pages, such as login pages, CAPTCHA-protected pages, or pages that require JavaScript.

## Directory Structure

The script creates the following directories under your working directory:

- `data/`
  - `content/`: Stores webpage content in JSON format.
  - `questions/`: Stores generated questions and relevant links in JSON format.

## How It Works

1. **Scrape the Website**: 
   - The script scrapes all links from the main page of the provided website.
   - For each valid link (non-login, non-CAPTCHA, etc.), the content is extracted and stored in `data/content/`.
   
2. **Generate Questions**: 
   - The extracted content is passed to Google's Generative AI model to generate 10 relevant questions.
   - These questions are saved in JSON format under `data/questions/`.

3. **Find Similar Content**: 
   - For each generated question, the script finds the top 2 most similar links within the website based on content similarity.
   - The relevant links are added alongside the questions in the JSON files.

4. **Error Handling**:
   - The script skips invalid or empty pages and logs any issues encountered during processing.

## Setup

1. Install the required libraries:

   ```bash
   pip install requests beautifulsoup4 google-generativeai sentence-transformers
