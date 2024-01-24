from bs4 import BeautifulSoup
import timeit
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def getJSON(url):
    #above is an atempt to trick detection of bot
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    r=requests.get(url, headers=headers)
    soup1 = BeautifulSoup(r.content, 'html5lib') 
    return soup1
    
def getTotalCardsInDB(soup1):   
    div_elements = soup1.find_all('tbody')
    sports = []
    count = []
    for tbody in div_elements:
        # Find all 'tr' elements within the tbody
        rows = tbody.find_all('tr', class_='stats_row')

        # Iterate through each row and extract the required data
        for row in rows:
            sport = row.find('a').text.strip()  # Extracts the sport name
            number = row.find_all('td')[1].text.strip()  # Extracts the number
            sports.append(sport)
            count.append(number)
    return sports,count

def getCardsLinks(sports):
    start = timeit.timeit() 
    base_url = "https://www.tcdb.com/Names.cfm/sp/{sport}/let/{letter}?MODE=GET"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Assuming you want to iterate over all letters
    links = []
    for sport in sports:
            print("Processing ", sport)
            for letter in letters:
                url = base_url.format(sport=sport, letter=letter)
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    li_elements = soup.find_all('li')
                        # Iterate through each 'li' element
                    for li in li_elements:
                        a_tag = li.find('a')
                        if a_tag:
                            # Extract href attribute
                            link = a_tag.get('href')
                            if(link.__contains__("Person")):
                                links.append("https://www.tcdb.com" + link)
                            #print(f"Name: {name}, Link: {link}")
    end = timeit.timeit()
    total = end - start
    print("getCardsLinks took", total, " seconds to process") 
    return links

def getPlayerCardsMorePage(playerPage):
    
    response = requests.get(playerPage)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the div with class 'more'
    div_more = soup.find('div', class_='more')

    # Check if the div is found
    if div_more:
        # Find all <a> tags within this div
        a_tags = div_more.find_all('a')

        # Iterate through each <a> tag
        for tag in a_tags:
            if tag.text.strip() == "Cards":
                # Extract the href attribute
                cards_link = tag['href']
                moreCardsLink = "https://www.tcdb.com" + cards_link
                return moreCardsLink
    

def getTotalCount(counts):
    integer_list = [int(number.replace(',', '')) for number in counts]
    # Sum up the numbers
    total = sum(integer_list)
    return total
                        




def getAllPLayerPageLinks():
    d = getTotalCardsInDB(totalSetsjson)
    #expectedCount = getTotalCount(d[1])
    cardLinks = getCardsLinks(d[0])
    #print("\nLength:", len(cardLinks), "\nExpected count: ", expectedCount)
    return cardLinks

def updateLinksListonDisk():
    playerPages = getAllPLayerPageLinks()
    #print(playerPages)
    results = []
    with ThreadPoolExecutor(max_workers=None) as executor:
        # Submit tasks to the executor
        future_to_playerPage = {executor.submit(getPlayerCardsMorePage, playerPage): playerPage for playerPage in playerPages}
        # Process results as they become available
        for i, future in enumerate(as_completed(future_to_playerPage), 1):
            try:
                morePage = future.result(timeout=10)  # Set a reasonable timeout
                results.append(morePage + "\n")
                print(i)
            except Exception as e:
                print(f"Error in future: {e}")
    with open('urls.txt', 'w') as file:
        for page in results:
            file.write(page)
    file.close()
    return 
    

totalSetsjson = getJSON("https://www.tcdb.com/Stats.cfm?MODE=Sets&Report=1")

updateLinksListonDisk()