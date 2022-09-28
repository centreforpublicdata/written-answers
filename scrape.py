import csv
from datetime import date
import re
import requests
import sys
import time
from pyquery import PyQuery as pq
from pprint import pprint

'''
Fetch all written answers from a given year, and dump them into a CSV file.
Here's an example: https://www.theyworkforyou.com/wrans/?id=2019-12-20.326.h
We will scrape the following fields into our CSV file:
- Title
- Date
- Department being asked
- Question text (NB there may be multiple questions)
- Answer text
- Whether it has an attachment
- Reader vote breakdown, in case this is useful for spotting unanswered questions
'''

BASE_URL = 'https://www.theyworkforyou.com'

# Now we have all the URLs, so scrape each individual Written Answer.
def scrape_answer(url, date_submitted, date_answered, question_id):
	response = requests.get(url)
	doc = pq(response.text)
	data = {}

	data['url'] = url
	data['title'] = doc('.debate-header h1').text()
	header = doc('.debate-header p.lead').text().split('–')
	data['department'] = header[0].replace(" written question", "").strip()
	data['date_submitted'] = date_submitted # header[1].replace(" answered on", "").replace('.', '').strip()
	data['date_answered'] = date_answered
	# print(title, department, date_submitted)

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
	# print(question_speaker, question_position)
	# print(question_text)

	answer = doc('#g%s\\.r0' % question_id)
	ans = pq(answer)
	data['answer_speaker'] = ans('.debate-speech__speaker__name').text()
	data['answer_position'] = ans('.debate-speech__speaker__position').text()
	data['answer_text'] = ans('.debate-speech__content').text().replace('\n', '')
	# print(answer_speaker, answer_position)
	# print(answer_text)

	question_answered = doc('.question-answered-result__vote-text')
	votes_answered = question_answered.eq(0).text().\
		replace(" person thinks so", '').replace("people think so", "").strip()
	votes_notanswered = question_answered.eq(1).text().\
		replace(" person thinks not", '').replace("people think not", "").strip()
	# print(votes_answered)
	# print(votes_notanswered)
	data['votes_answered'] = votes_answered
	data['votes_notanswered'] = votes_notanswered
	if votes_answered and votes_notanswered:
		data['votes_diff'] = int(votes_notanswered) - int(votes_answered)
	else:
		data['votes_diff'] = 0

	data['attachment'] = doc('.qna-result-attachments-container').text()
	# pprint(data)
	# sys.exit()
	return data

def get_answers(url_file, params, outfile_name):
	print("Scraping answers")

	today = date.today()
	if not outfile_name:
		outfile_name = './data/output_%s.csv' % today.strftime("%Y-%m-%d")

	# Check which URLs you have already scraped, and load them into local data.
	previously_scraped_urls = []
	# reader = csv.DictReader(open("./data/output_%s.csv" % params, "r"))
	# for row in reader:
	# 	previously_scraped_urls.append({row['url']: row})

	# Prepare your output file. TODO: improve the naming.
	header = [
		'url', 'title', 'department', 'date_submitted', 'date_answered',
		'question_speaker', 'question_position', 'question_text',
		'answer_speaker', 'answer_position', 'answer_text',
		'votes_answered', 'votes_notanswered', 'votes_diff', 'attachment'
	]
	writer = csv.DictWriter(open(outfile_name, 'w'), fieldnames=header)
	writer.writeheader()

	# Open your URL file.
	reader = csv.DictReader(open(url_file, 'r'))
	counter = 0
	for row in reader:
		url = row['url']
		if url in previously_scraped_urls:
			writer.writerow(urls[url])
		else:
			# print('SCRAPING', url)
			date_answered = row['date_answered']
			date_submitted = re.search(r'id=(.*?)\.', url).group(1)
			question_id = re.search(r'id=(.*?)\.(.*?)\.', url).group(2)
			if (counter % 100) == 0:
				print(counter)
			row = scrape_answer(url, date_submitted, date_answered, question_id)
			# pprint(row)
			writer.writerow(row)
			# time.sleep(2)
		counter += 1
		# print()
		# print()


# TODO: Make filenames a command-line argument
YEAR = 2022
params = {
	"department": "",
	"year": YEAR
}
url_file = "./data/written_answer_urls_%s.csv" % YEAR
get_answers(url_file, params, "./data/output_%s.csv" % YEAR)

