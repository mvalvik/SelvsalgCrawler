#!/usr/bin/env python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from urllib2 import urlopen
from HTMLParser import HTMLParser
import sys
import shelve
import hashlib
import smtplib
from email.mime.text import MIMEText

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")

hipsterZipCodes = [str(x) for x in range(999,2300)]

class Residence():
	pass

def get_apartment(section_url):
    d = shelve.open('database.db')
    html = urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    residence_cards = soup.select(".section-recent .properties-grid .property-card")

    residences = []

    for residence_card in residence_cards:
    	res = Residence()
    	res.type = str(residence_card.select(".ribbon")[0].contents[0])
    	res.price = int(str(residence_card.select("td.price")[0].contents[0]).replace(',', '').replace('.','').replace('-',''))
    	res.ydelse = str(residence_card.select("td.hidden-xs")[0].contents[0])
    	res.description = str(residence_card.select("h6 a")[0].contents[0])
    	res.link = str(section_url + residence_card.select("h6 a")[0].attrs['href'])
    	res.adress = str(residence_card.select(".polaroid p")[0].contents[0])
    	print res
    	if any(x in res.adress for x in hipsterZipCodes) and res.price < 1200000:
    		residences.append(res)

    for residence in residences:
    	m = hashlib.md5()
    	print residence.type
    	print residence.ydelse
    	print residence.price
    	print residence.description
    	print residence.adress
    	m.update(residence.description)
    	hashOfDescription = m.digest()
    	#if not d.has_key(hashOfDescription):
    	#	d[hashOfDescription] = residence
    	#	sendEmail(residence)
    return residence_cards

def sendEmail(residence):
	FROM = 'selvsalg@gmail.com'
	TO = ['morten@valvik.com']
	SUBJECT = "Ny bolig på selvsalg: " + residence.description
	TEXT = "Beskrivelse: " + " Pris: " + residence.price + "  Adresse: " + residence.adress + " Link: " + residence.link

	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s"""%(FROM, ", ".join(TO), SUBJECT, TEXT)
	username = 'mrvalvik@gmail.com'
	password = 'hbmsnvwygiuldhhe'

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail('selvsalg@valvik.dk','morten@valvik.dk', message)
	server.quit()
	print 'email sent'

get_apartment("http://www.selvsalg.dk")
