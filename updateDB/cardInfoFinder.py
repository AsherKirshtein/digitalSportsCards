from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
from IPython.display import clear_output
import requests
from celery import Celery
from bs4 import BeautifulSoup

realUrl = "https://www.tcdb.com/Person.cfm/pid/366340/col/1/yea/0/Neil-Abbatiello?sTeam=&sCardNum=&sNote=&sSetName=&sBrand="

def fetch_links_from_page(page_index, base_url):
    url = base_url.format(page_index)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding all <a> tags and filtering based on href attribute
    header = "https://www.tcdb.com"
    links = [header + a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith("/ViewCard.cfm")]
    last_Page = False
    if not links:
        last_Page = True
    return links, last_Page

def find_Last_Page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)

    # Regular expression to match 'PageIndex=' and capture the following number
    regex = re.compile(r'PageIndex=(\d+)')

    page_indices = []
    for link in links:
        href = link['href']
        match = regex.search(href)
        if match:
            page_index = match.group(1)
            page_indices.append(page_index)
    try:
        max_number = max(map(int, page_indices))
    except Exception as e:
        max_number = 0
    return max_number
    
def getAllCardLinks(url):
    index = 1
    currentPage = fetch_links_from_page(index, url)
    allCards = []
    allCards.extend(currentPage[0])
    lastPageNum = find_Last_Page(url)
    p_num = 0
    start = time.time()
    #print("Acquiring All Links to cards")
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks to executor
        future_to_page = {executor.submit(fetch_links_from_page, index,url): index for index in range(1, lastPageNum + 1)}

        # Process results as they complete
        for future in as_completed(future_to_page):
            page_index = future_to_page[future]
            try:
                links, _ = future.result()
                allCards.extend(links)
                p_num +=1
            except Exception as exc:
                print(f"Page {page_index} generated an exception: {exc}")
    return allCards

def update_progress_bar(total, processed, startTime, length=50):
    current_time = time.time()
    elapsed_time = current_time - startTime
    percent = (processed / total) * 100
    bar_length = int(length * processed // total)
    bar = '#' * bar_length + '-' * (length - bar_length)
    
    if elapsed_time > 15 and processed > 0:
        total_time_est = (elapsed_time / processed) * total
        remaining_time = total_time_est - elapsed_time
        eta_str = f" - Time Remaining: {format_time(remaining_time)}"
    else:
        eta_str = ""
    
    clear_output(wait=True)
    print(f"\rProgress: [{bar}] {percent:.2f}%{eta_str}", end='')
    if percent == 100:
        total_time_est = (elapsed_time / processed) * total
        print("Time took: ",  total_time_est)

def getAllCardInfo(links, p_player):
    cardInfo = []
    # Define the number of threads. You can adjust this number based on your requirements and resources.
    links_to_Process = len(links)
    processed = 0
    startTime = time.time()
    #print("\nGetting All info from cards for: ", p_player)
    with ThreadPoolExecutor(max_workers=None) as executor:
        # Submit tasks to the executor.
        future_to_link = {executor.submit(infoHandler, link): link for link in links}

        # Process results as they complete
        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                result = future.result()
                cardInfo.extend(result)
                links_to_Process -= 1
                processed += 1
                #update_progress_bar(links_to_Process,processed, startTime) 
            except Exception as exc:
                print(f'Link {link} generated an exception: {exc}')
    return cardInfo
    
def infoHandler(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    player = extract_player_name(link)
    Card_Title = soup.find('strong').get_text()
    total_cards_text = soup.find(string="Total Cards:")
    total_cards = total_cards_text.next_element.get_text() if total_cards_text else None
    rating_text = soup.find(string="Rating: ")
    rating = rating_text.next_element.get_text() if rating_text else None
    Front_Image, Back_Image = getImages(soup)
    return player, Card_Title,total_cards,rating, Front_Image, Back_Image

def extract_player_name(url):
    # Split the URL on slashes and take the last part
    last_part = url.rsplit('/', 1)[-1]
    # Split the last part on hyphens and extract the player's name
    name_parts = last_part.split('-')[-2:]  # Last two parts are first name and last name
    player_name = ' '.join(name_parts)

    return player_name

def getImages(soup):
    images = soup.findAll('img')
    front_image = None
    back_image = None
    for img in images:
        if img.get('alt') and "Front" in img['alt']:
            front_image = "https://www.tcdb.com" + img['src']
        elif img.get('alt') and "Back" in img['alt']:
            back_image = "https://www.tcdb.com" + img['src']
    return front_image, back_image
    
def getPlayerTitle(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    player_name = soup.find('strong').get_text()
    bday_text = soup.find(string="Born:")
    bday = bday_text.next_element.get_text() if bday_text else None
    college_Text = soup.find(string="College:")
    college = college_Text.next_element.get_text() if college_Text else None
    return player_name, bday, college
    

def format_time(seconds):
    """Format seconds into a human-readable hh:mm:ss format"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"  

def format_url(base_url):
    # Split the base URL at '?'
    parts = base_url.split('?')

    # Check if the URL is already in the correct format
    if len(parts) > 1 and 'PageIndex=' in parts[1]:
        return base_url  # The URL is already correctly formatted

    # Insert 'PageIndex={}' before other parameters
    formatted_url = f"{parts[0]}?PageIndex={{}}&{parts[1]}" if len(parts) > 1 else f"{base_url}?PageIndex={{}}"

    return formatted_url

app = Celery('cardInfoFinder')
app.config_from_object('celeryconfig')
# Additional configurations can be added here


@app.task 
def read_info_from_file(url):
        realUrl = url.strip()
        p_name = getPlayerTitle(realUrl)
        base_url = format_url(realUrl)
        links = getAllCardLinks(base_url)
        info = getAllCardInfo(links,p_name)
        return info

#To run workers: 
# start the redis server: redis-server
# start the worker nodes: celery -A cardInfoFinder worker --loglevel=info
# start the big daddy boss: python3 bigDaddyBoss.py

