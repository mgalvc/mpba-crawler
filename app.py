import requests
import json
import smtplib
import datetime

from bs4 import BeautifulSoup
from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apscheduler.schedulers.blocking import BlockingScheduler

url = 'https://www.mpba.mp.br/institucional/ceaf/estagios/2018'

ADDRESS = open('utils/.email').read()
PASSWORD = open('utils/.password').read()

email_server = smtplib.SMTP('smtp.gmail.com', 587)
email_server.starttls()
email_server.login(ADDRESS, PASSWORD)

def scraper():
	"""
		This function reads the page and get a list with the available internships
	"""
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')

	internships_list = soup.find_all(class_='ceaf-estagio')

	internships_info = []

	for internship in internships_list:
		text = internship.find('a')
		internships_info.append(text.contents[0])

	return internships_info

def get_contacts():
	"""
		This function reads a file containing all the email addresses that must receive the message
	"""
	with open('utils/contacts.json', mode='r', encoding='utf-8') as contacts:
		return json.loads(contacts.read())

def read_template():
	"""
		This function reads the template
	"""
	with open('utils/template.txt', mode='r', encoding='utf-8') as template_file:
		return Template(template_file.read())

def get_fsa_internship():
	"""
		This function check if there is a internship in Feira de Santana
	"""
	for internship in scraper():
		if "feira de santana" in internship.lower() and "direito" in internship.lower():
			return internship

def send_ack_email():
	"""
		Sends an ack email just to check that the script is working well
	"""
	chief = get_contacts().get('Matheus')

	email_text = MIMEMultipart()
	message = "Internship not found, but I'm working well. Check it at {}".format(url)

	today = datetime.date.today()
	date = today.strftime('%d/%m')

	email_text['From'] = ADDRESS
	email_text['To'] = chief
	email_text['Subject'] = 'MPBA Ack - {}'.format(date)

	email_text.attach(MIMEText(message, 'plain'))

	email_server.send_message(email_text)

	del email_text
		
# scheduler = BlockingScheduler()

# @scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=14)
def send_emails():
	"""
		This function sends a email to all the subscribed emails when there is an available internship for Feira de Santana
		Also sends the ack email for the developer
	"""
	print('sending email...')
	
	contacts = get_contacts()
	fsa_internship = get_fsa_internship()

	if not fsa_internship:
		send_ack_email()
		return
	
	for name, email in contacts.items():
		email_text = MIMEMultipart()

		message = read_template().substitute(who=name, internship=fsa_internship, url=url)

		today = datetime.date.today()
		date = today.strftime('%d/%m')

		email_text['From'] = ADDRESS
		email_text['To'] = email
		email_text['Subject'] = 'Chamada MPBA - {}'.format(date)

		email_text.attach(MIMEText(message, 'plain'))

		email_server.send_message(email_text)

		del email_text

# scheduler.start()
send_emails()