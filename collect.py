import requests
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime

def parse(html):
	soup = BeautifulSoup(html.text, 'html.parser')
	table = soup.find('table')
	body = table.find('tbody')
	output = []
	for row in body.find_all('tr'):
		try:
			doc_col, date, case = row.find_all('td')
			doc_links = doc_col.find_all('a')
			docs = [(d.text, d['href']) for d in doc_links if '.pdf' in d['href'] and 'monetary' in d.text.lower()]
			date = datetime.strptime(date.text.split(":")[1].strip(), '%B %d, %Y')
			if docs:
				o = {"date":date.strftime('%Y-%m-%d'), "case": case.text.split(":")[1].strip(), "doc_name": docs[0][0], "doc_link": docs[0][1]}
			else: 
				o = {"date": date.text.split(":")[1].strip(), "case": case.text.split(":")[1].strip(), "doc_name": '', "doc_link": ''}
			output.append(o)
		except Exception as e:
			print(e)
			print(row)
		
	return output

def to_csv(rows):
	with open('ftc_monetary_judgements.csv', 'w') as outfile:
		writer = csv.DictWriter(outfile, fieldnames=['date', 'case', 'doc_name', 'doc_link'])
		writer.writeheader()
		for r in rows:
			if r:
				writer.writerow(r)

def run():
	rows = []
	try:
		# Arbitrary high number because I don't know what the max page is
		for i in range(200):
			print('%d of 200' % i)
			headers = {
			    'Upgrade-Insecure-Requests': '1',
			    'Referer': 'https://www.ftc.gov/enforcement/cases-proceedings/case-document-search?title=&field_document_description=MONETARY',
			    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
			}
			# Can tweak params for different searches.
			# Current looking for all cases with documentation that have the word monetary in it.
			params = (
			    ('title', ''),
			    ('field_document_description', 'MONETARY'),
			    ('page', '%d'%(i)),
			)
			response = requests.get('https://www.ftc.gov/enforcement/cases-proceedings/case-document-search', headers=headers, params=params)
			new = parse(response)
			if new:
				rows += new
			time.sleep(1)
	except Exception as e:
		print(e)
	finally:
		to_csv(rows)

run()