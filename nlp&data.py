##step 1 data extraction
## download dependencies first pip install pandas beautifulsoup4 requests nltk textblob openpyxl textstat
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

from textblob import TextBlob

# Read the input Excel filexlsx
input_df = pd.read_excel("Input.xlsx")

# Create a directory to save the extracted articles
os.makedirs('extracted_articles', exist_ok=True)

# Function to extract article title and text
def extract_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title and article text
    title = soup.find('h1').get_text(strip=True)  # Adjust selector based on actual HTML structure
    article_text = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])  # Extract paragraphs

    return title, article_text

# Loop through each URL in the DataFrame
for index, row in input_df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    
    title, article_text = extract_article(url)

    # Save the extracted article to a text file
    with open(f'extracted_articles/{url_id}.txt', 'w', encoding='utf-8') as f:
        f.write(f'Title: {title}\n\n{article_text}')
        
        
        ##Step 2 is Data Analysis
        
import pandas as pd
import os
import nltk
from nltk import pos_tag, word_tokenize
from collections import Counter
import textstat

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Function to compute text analysis variables
def analyze_text(article_text):
    blob = TextBlob(article_text)
    
    # Calculate scores
    positive_score = blob.sentiment.polarity if blob.sentiment.polarity > 0 else 0
    negative_score = -blob.sentiment.polarity if blob.sentiment.polarity < 0 else 0
    polarity_score = blob.sentiment.polarity
    subjectivity_score = blob.sentiment.subjectivity
    
    # Sentence analysis
    sentences = blob.sentences
    avg_sentence_length = len(article_text.split()) / len(sentences) if sentences else 0
    word_count = len(article_text.split())
    
    # Complex word count and percentage of complex words
    complex_words = [word for word in word_tokenize(article_text) if len(word) > 2 and word.isalpha()]
    complex_word_count = len(complex_words)
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count > 0 else 0
    
    # FOG Index
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    
    # Average number of words per sentence
    avg_words_per_sentence = word_count / len(sentences) if sentences else 0
    
    # Syllables per word using textstat
    syllable_count = sum(textstat.syllable_count(word) for word in complex_words)
    syllables_per_word = syllable_count / word_count if word_count > 0 else 0
    
    # Personal pronouns
    personal_pronouns = [word for word, tag in pos_tag(word_tokenize(article_text)) if tag in ['PRP', 'PRP$']]
    
    # Average word length
    avg_word_length = sum(len(word) for word in article_text.split()) / word_count if word_count > 0 else 0

    return {
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': avg_sentence_length,
        'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': word_count,
        'SYLLABLE PER WORD': syllables_per_word,
        'PERSONAL PRONOUNS': len(personal_pronouns),
        'AVG WORD LENGTH': avg_word_length
    }

# Prepare to save results
results = []

# Loop through extracted articles
for filename in os.listdir('extracted_articles'):
    if filename.endswith('.txt'):
        with open(os.path.join('extracted_articles', filename), 'r', encoding='utf-8') as f:
            article_text = f.read()
            analysis = analyze_text(article_text)
            results.append({**{'URL_ID': filename[:-4]}, **analysis})

# Create DataFrame and save to Excel
output_df = pd.DataFrame(results)
output_df.to_excel('Output Data Structure.xlsx', index=False)