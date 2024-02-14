import csv
import requests

from pyquery import PyQuery as pq


BASE_URL = 'https://www.theyworkforyou.com'

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
	writer = csv.DictWriter(open('../data/urls/written_answer_urls_%s.csv' % year, 'w'), \
		fieldnames=url_header)
	writer.writeheader()
	year_url = '%s/wrans/?y=%s' % (BASE_URL, year)
	response = requests.get(year_url)
	doc = pq(response.text)
	links = doc('.calendar a')
	for link in links:
		href = link.attrib['href']
		date_answered = href.split('/?d=')[1]
		get_answer_urls_for_date(BASE_URL + href, date_answered, writer)

def main(args):
	get_answer_urls(args.year)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(\
    	description="Get URLs of written answers from TWFY for a given year.")
    parser.add_argument('-y', '--year', help='Year to process',
    	required=True)
    args = parser.parse_args()

    main(args)
