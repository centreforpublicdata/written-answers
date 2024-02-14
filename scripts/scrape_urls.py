import csv
from datetime import date
import os
import re
import requests
import time

from pyquery import PyQuery as pq


BASE_URL = 'https://www.theyworkforyou.com'

def scrape_answer(url, date_submitted, date_answered, question_id):
	'''
	Scrape an individual Written Answer from a TWFY URL.
	Here's an example: 
	https://www.theyworkforyou.com/wrans/?id=2019-12-20.326.h
	We will scrape the following fields:
	- Title
	- Date
	- Department being asked
	- Question text (NB there may be multiple questions)
	- Answer text
	- Whether it has an attachment
	- Reader vote breakdown
	'''
	response = requests.get(url)
	doc = pq(response.text)
	data = {}

	data['url'] = url
	data['title'] = doc('.debate-header h1').text()
	header = doc('.debate-header p.lead').text().split('–')
	data['department'] = header[0].replace(" written question", "").strip()
	data['date_submitted'] = date_submitted # header[1].replace(" answered on", "").replace('.', '').strip()
	data['date_answered'] = date_answered

	question0 = doc('#g%s\\.q0' % question_id)
	question0q = pq(question0)
	data['question_speaker'] = question0q('.debate-speech__speaker__name').text()
	data['question_position'] = question0q('.debate-speech__speaker__position').text()
	question_text = ""
	questions = doc('.debate-speech')
	q = pq(questions)
	for q in questions:
		t = pq(q)
		if ".q" in t.attr('id'):
			temp = t(".debate-speech__content")
			question_text += temp.text().replace('\n', '') + "\n\n"
	data["question_text"] = question_text

	answer = doc('#g%s\\.r0' % question_id)
	ans = pq(answer)
	data['answer_speaker'] = ans('.debate-speech__speaker__name').text()
	data['answer_position'] = ans('.debate-speech__speaker__position').text()
	data['answer_text'] = ans('.debate-speech__content').text().replace('\n', '')
	question_answered = doc('.question-answered-result__vote-text')
	votes_answered = question_answered.eq(0).text().\
		replace(" person thinks so", '').replace("people think so", "").strip()
	votes_notanswered = question_answered.eq(1).text().\
		replace(" person thinks not", '').replace("people think not", "").strip()
	data['votes_answered'] = votes_answered
	data['votes_notanswered'] = votes_notanswered
	if votes_answered and votes_notanswered:
		data['votes_diff'] = int(votes_notanswered) - int(votes_answered)
	else:
		data['votes_diff'] = 0

	data['attachment'] = doc('.qna-result-attachments-container').text()
	return data

def get_answers(year):
	'''
	Process a list of input URLs, and any data we have already scraped,
	and store to an output file.
	'''
	url_file = "../data/urls/written_answer_urls_%s.csv" % year
	outfile = "../data/raw_answers/output_%s.csv" % year
	today = date.today()

	# First check for answers we have already scraped, and
	# rename the output file if necessary.
	previously_scraped_urls = []
	if os.path.exists(outfile):
		reader = csv.DictReader(open(outfile, "r"))
		for row in reader:
			previously_scraped_urls.append({row['url']: row})
		outfile = '../data/raw_answers/output_%s_%s.csv' % \
			(year, today.strftime("%Y-%m-%d"))
	if previously_scraped_urls:
		print(len(previously_scraped_urls), 'previously scraped URLs found')

	header = [
		'url', 'title', 'department', 'date_submitted', 'date_answered',
		'question_speaker', 'question_position', 'question_text',
		'answer_speaker', 'answer_position', 'answer_text',
		'votes_answered', 'votes_notanswered', 'votes_diff', 'attachment'
	]
	writer = csv.DictWriter(open(outfile, 'w'), fieldnames=header)
	writer.writeheader()
	reader = csv.DictReader(open(url_file, 'r'))
	counter = 0
	for row in reader:
		counter += 1
		url = row['url']
		if url in previously_scraped_urls:
			writer.writerow(urls[url])
		else:
			date_answered = row['date_answered']
			date_submitted = re.search(r'id=(.*?)\.', url).group(1)
			question_id = re.search(r'id=(.*?)\.(.*?)\.', url).group(2)
			if (counter % 100) == 0:
				print(counter)
			row = scrape_answer(url, date_submitted, date_answered, question_id)
			writer.writerow(row)
			# time.sleep(2)

def main(args):
	get_answers(args.year)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(\
		description="Fetch all written answers from a given year from TWFY.")
	parser.add_argument('-y', '--year', help='Year to process',
		required=True)
	args = parser.parse_args()

	main(args)
