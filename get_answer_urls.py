import csv
from datetime import date
import re
import requests
import sys
import time
from pyquery import PyQuery as pq
from pprint import pprint

YEAR = 2022
BASE_URL = 'https://www.theyworkforyou.com'


# Get all written answers from TWFY for a year.
# If you want to look at one particular date, use the Parliament site:
# https://questions-statements.parliament.uk/written-questions?AnsweredFrom=12%2F12%2F2019&AnsweredTo=01%2F01%2F2020&House=Commons
def get_answer_urls_for_date(date_url, date_answered, writer):
	response = requests.get(date_url)
	doc = pq(response.text)
	links = doc('a.business-list__title')
	for link in links:
		href = link.attrib['href']
		if not href.endswith('.mh'):
			writer.writerow({'url': BASE_URL + href, 'date_answered': date_answered})

def get_answer_urls(year):
	print("Getting URLs for %s" % year)
	url_header = ['url', 'date_answered']
	writer = csv.DictWriter(open('./data/written_answer_urls_%s.csv' % year, 'w'), \
		fieldnames=url_header)
	writer.writeheader()
	year_url = 'https://www.theyworkforyou.com/wrans/?y=%s' % year
	response = requests.get(year_url)
	doc = pq(response.text)
	links = doc('.calendar a')
	for link in links:
		href = link.attrib['href']
		date_answered = href.split('/?d=')[1]
		get_answer_urls_for_date(BASE_URL + href, date_answered, writer)

# TODO make this a command-line argument
get_answer_urls(YEAR)