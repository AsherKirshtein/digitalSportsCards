## Sports Card Data Extraction
# Overview
This project is a web scraping application that extracts detailed information about sports cards from a specified website. It utilizes Python, BeautifulSoup, and requests for data extraction, and employs Celery for asynchronous task management. The extracted data is stored in AWS DynamoDB using Boto3, and a Flask-based RESTful API is implemented for data retrieval and manipulation.

# Features
Web Scraping: Extracts sports card data using BeautifulSoup and requests.
Asynchronous Task Management: Utilizes Celery to manage asynchronous tasks.
Scalable Data Storage: Stores extracted data in AWS DynamoDB with Boto3 integration.
RESTful API: Provides a Flask-based API for data access and manipulation.
Parallel Processing: Employs ThreadPoolExecutor for efficient parallel data extraction.

# Prerequisites
Python 3.x
Redis (for Celery)
AWS account (for DynamoDB)
Flask
BeautifulSoup
requests
Boto3
Celery
