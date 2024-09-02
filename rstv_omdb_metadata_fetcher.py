import os
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from io import BytesIO
import rstv_config  # Import the rstv_config module

IMDB_BASE_URL = "https://www.imdb.com"
SEARCH_URL = IMDB_BASE_URL + "/find?q="
POSTER_DIR = "posters"

# Define a Mozilla Firefox User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    sha1_checksum = calculate_sha1(file_path)
    date_added = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
    
    return {
        "filename": file_name,
        "sha1_checksum": sha1_checksum,
        "date_added": date_added,
        "date_modified": date_modified
    }

def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def get_movie_metadata(movie_title):
    attempt = 0
    while attempt < 2:
        print(f"Attempt {attempt + 1}: Searching for '{movie_title}' on IMDb.")
        search_url = SEARCH_URL + movie_title.replace(" ", "+")
        response = requests.get(search_url, headers=HEADERS)
        print(f"Request URL: {search_url}")
        print(f"Response Status Code: {response.status_code}")
        
        # Print raw HTML response for debugging
        print("Raw HTML Response:")
        print(response.text)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            results = soup.find_all('div', class_='ipc-metadata-list')
            if results:
                print("Titles found:")
                movies = []
                for i, result in enumerate(results[:3]):  # Limit to 3 options
                    title_tag = result.find('a', href=True)
                    if title_tag:
                        title = title_tag.text.strip()
                        imdb_id = title_tag['href'].split('/')[2]
                        year_tag = result.find('span', class_='sc-16ede01-2')
                        year_text = year_tag.text.strip('()') if year_tag else 'Unknown'
                        movies.append((title, year_text, imdb_id))
                        print(f"{i + 1}: {title} ({year_text})")
                
                choice = input("Select the correct movie by number (or enter 0 to skip): ").strip()
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(movies):
                        imdb_id = movies[choice_index][2]
                        return fetch_movie_details(imdb_id)
                except ValueError:
                    pass

                print("No valid selection made or user skipped. Skipping metadata fetching.")
                return None
            elif attempt == 0:
                movie_title = remove_year_from_title(movie_title)
                print(f"Movie not found. Trying without year: '{movie_title}'")
        attempt += 1
        print("Trying to find another match...")
    print("No suitable movie found or confirmation failed. Skipping metadata fetching.")
    return None

def remove_year_from_title(title):
    import re
    return re.sub(r"\(\d{4}\)", "", title).strip()

def fetch_movie_details(imdb_id):
    print(f"Fetching detailed information for IMDb ID: {imdb_id}")
    url = f"{IMDB_BASE_URL}/title/{imdb_id}/"
    response = requests.get(url, headers=HEADERS)
    print(f"Request URL: {url}")
    print(f"Response Status Code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        metadata = {
            "Title": soup.find('h1').text.strip(),
            "Year": soup.find('span', id='titleYear').text.strip('()'),
            "Released": soup.find('a', title='See more release dates').text.strip(),
            "Genre": ', '.join([genre.text for genre in soup.find_all('span', class_='sc-16ede01-2 gkKpFf')]),
            "Director": ', '.join([director.text for director in soup.find_all('a', href=True) if '/name/nm' in director['href']]),
            "Writer": ', '.join([writer.text for writer in soup.find_all('a', href=True) if '/name/nm' in writer['href']]),
            "Actors": ', '.join([actor.text for actor in soup.find_all('a', href=True) if '/name/nm' in actor['href']]),
            "Plot": soup.find('span', class_='sc-16ede01-2 iQZ2xq').text.strip(),
            "Language": ', '.join([language.text for language in soup.find_all('a', href=True) if '/language' in language['href']]),
            "Country": ', '.join([country.text for country in soup.find_all('a', href=True) if '/country' in country['href']]),
            "Awards": soup.find('span', class_='sc-16ede01-2 iQZ2xq').text.strip(),
            "Poster": soup.find('div', class_='ipc-poster').find('img')['src']
        }
        save_poster_image(metadata['Poster'], os.path.join(POSTER_DIR, imdb_id + ".jpg"))
        return metadata
    return None

def save_poster_image(poster_url, save_path):
    print(f"Downloading poster image from URL: {poster_url}")
    response = requests.get(poster_url, headers=HEADERS)
    print(f"Response Status Code: {response.status_code}")
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
        print(f"Poster image saved at: {save_path}")

def update_or_write_json(file_path, json_path, file_info):
    movie_title = os.path.splitext(file_info["filename"])[0]
    movie_metadata = get_movie_metadata(movie_title)
    if movie_metadata:
        file_info.update(movie_metadata)
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
            if existing_data['sha1_checksum'] == file_info['sha1_checksum']:
                print("SHA1 checksum is the same. No update needed.")
                return
            else:
                print("SHA1 checksum is different. Updating JSON file.")
    
    with open(json_path, 'w') as f:
        json.dump(file_info, f, indent=4)
    print(f"JSON file saved at {json_path}")

def main(file_path):
    if not os.path.isfile(file_path):
        print(f"The provided path '{file_path}' is not a valid file.")
        return
    
    file_info = get_file_info(file_path)
    json_path = file_path + '.json'
    
    update_or_write_json(file_path, json_path, file_info)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
    else:
        main(sys.argv[1])
