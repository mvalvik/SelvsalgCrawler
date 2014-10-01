#!/usr/bin/env python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from urllib2 import urlopen
from HTMLParser import HTMLParser
import time
import sys
import shelve
import hashlib
import smtplib
from email.mime.text import MIMEText
import config as cfg

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")

hipsterZipCodes = [str(x) for x in range(cfg.selvsalg['hipsterCodesLow'], cfg.selvsalg['hipsterCodesMax'])]

class Residence():
	pass

def get_apartment(section_url):
    d = shelve.open('database.db')
    html = urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    residence_cards = soup.select(".properties-grid .property-card")
    
    residences = []

    for residence_card in residence_cards:
    	res = Residence()
    	res.type = str(residence_card.select(".ribbon")[0].contents[0])
    	res.price = str(residence_card.select("td.price")[0].contents[0]).replace(',', '').replace('.','').replace('-','')
    	res.description = str(residence_card.select("h6 a")[0].contents[0])
        res.ydelse = str(residence_card.select("td.hidden-xs")[0].contents[0])
    	
    	res.link = str(section_url + residence_card.select("h6 a")[0].attrs['href'])
    	res.adress = str(residence_card.select(".polaroid p")[0].contents[0])
    	print res
    	if any(x in res.adress for x in hipsterZipCodes) and int(res.price) < cfg.selvsalg['maxPrice']:
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
    	if not d.has_key(hashOfDescription):
    		d[hashOfDescription] = residence
    		sendEmail(residence)
    return residence_cards

def sendEmail(residence):
	FROM = 'selvsalg@gmail.com'
	TO = cfg.selvsalg['emailReceiver']
	SUBJECT = "Ny bolig på selvsalg: " + residence.description
	TEXT = "Beskrivelse: " + " Pris: " + residence.price + "  Adresse: " + residence.adress + " Link: " + residence.link

	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s"""%(FROM, ", ".join(TO), SUBJECT, TEXT)
	username = cfg.selvsalg['emailHostUsername']
	password = cfg.selvsalg['emailHostPassword']

	server = smtplib.SMTP(cfg.selvsalg['emailHostServer'])
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail('selvsalg@valvik.dk',cfg.selvsalg['emailReceiver'], message)
	server.quit()
	print 'email sent'
get_apartment("http://www.selvsalg.dk/resultater?since=" + time.strftime("%Y-%m-%d") + "&view=grid")
