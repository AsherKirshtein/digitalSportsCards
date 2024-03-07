from urllib import response
import boto3
from updateDB.cardInfoFinder import read_info_from_file
from tqdm import tqdm

def setup_dynamodb():
    # Set up DynamoDB client
    # Replace 'your_access_key_id' and 'your_secret_access_key' with your actual AWS credentials
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id='AKIAYXVK5WVEONT4I4BH',
                              aws_secret_access_key='K+77ZupdTYeXeZQ7PUKIFmGiwolAXldd3F7gqoOV',
                              region_name='us-east-1')  # e.g., 'us-west-2'
    return dynamodb.Table('DigitalSportsCardsDB')  # Replace with your table name

def write_result_to_dynamodb(table, link, task_id, card_data):
    for card in card_data:
        item = {
            'task_id': task_id,
            'link': link,
            'player_name': card['player_name'],
            'series': card['series'],
            'amountOfCards': card['amountOfCards'],
            'rating': card['rating'],
            'front_image_url': card['front_image_url'],
            'back_image_url': card['back_image_url'],
            'additional_info': card['additional_info']
        }
        print('writing Item to db: ', item)
        table.put_item(Item=item)
        
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
            print(f"Failed to write to DynamoDB: {response}")


def process_result(result):
    cards = []
    num_fields = 7   # Number of fields per card

    for i in range(0, len(result), num_fields):
        card = {
            'player_name': result[i],
            'series': result[i + 1],
            'amountOfCards': result[i + 2],
            'rating': result[i + 3],
            'front_image_url': result[i + 4],
            'back_image_url': result[i + 5],
            'additional_info': result[i + 6]  # Adjust field names as needed
        }
        cards.append(card)

    return cards

def send_all_work(table):
    
    with open('links.txt', 'r') as file:
        lines = file.readlines()

    # Dispatch tasks
    for line in tqdm(lines, desc="Processing links"):
        link = line.strip()
        read_info_from_file.delay(link)
    return "Completed processing all tasks."

def get_all_items():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('DigitalSportsCardsDB')

    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    return data

if __name__ == "__main__":
    table = setup_dynamodb()
    status = send_all_work(table)