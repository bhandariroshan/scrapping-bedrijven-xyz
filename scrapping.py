#!/usr/bin/env python
# encoding: utf-8

import urllib3
import time
from lxml import etree
from io import StringIO
import requests
import csv
import datetime
from Database import DB

categories = [
    'Podiumkunstenaars',
    'Psychologen',
    'Reclamebureaus',
    'Schilders',
    'Schoonheidsspecialisten',
    'Schoonmaakbedrijven',
    'Stratenmakers',
    'Stukadoors',
    'Tandartsen',
    'Tegelzetters',
    'Timmermannen',
    'Uitvaartverzorgers',
    'Uitzendbureaus',
    'Vastgoedbeheerders',
    'Verhuizers',
    'Webdesigners'
]


class Soce():
    def __init__(self):
        self.base_html = None
        self.response = None
        self.base_url = 'http://bedrijven.xyz/'

    def get_page(self, open_url):
        nav_link = self.base_url + open_url
        try:
            response = requests.get(nav_link)
            self.base_html = response.text
        except:
            time.sleep(60)
            return self.get_page(nav_link)

    def parse_links_in_page(self, category, page):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.base_html), parser)
        allAs = tree.xpath("//div[@class='item']/a")
        db = DB()
        for eachA in allAs:
            # print (eachA.xpath('./text()'), eachA.attrib['href'])
            try:
                db.add_links({
                    'link': eachA.attrib['href'],
                    'processed': False,
                    'category': category,
                    'page': page
                })
            except:
                pass

    def export_to_csv(self):
        db = DB()
        all_datas = db.get_all()
        newData = csv.writer(open("mydata.csv", "w"))
        newData.writerow([
            'date_scrapped',
            'category',
            'page',
            'url',
            'company_name',
            'zipcode',
            'street_address',
            'house_number',
            'city',
            'website',
            'email',
            'phone_number'
        ])

        for each_data in all_datas:
            newData.writerow([
                each_data['date_scrapped'],
                each_data['category'],
                each_data['page'],
                each_data['url'],
                each_data['company_name'],
                each_data['zipcode'],
                each_data['street_address'],
                each_data['house_number'],
                each_data['city'],
                each_data['website'],
                each_data['email'],
                each_data['phone_number']
            ])

    def navigate_page_for_data(self):
        db = DB()
        unprocessed = db.get_one_unprocessed()

        while unprocessed:
            phone = None
            date_scrapped = str(datetime.datetime.today().date())
            company_name = None
            zipcode = None
            street_address = None
            house_number = None
            city = None
            province = None
            website = None
            email = None
            
            try:
                nav_link = self.base_url + unprocessed['link'][1:]
                response = requests.get(nav_link)
                self.base_html = response.text
                parser = etree.HTMLParser()
                tree = etree.parse(StringIO(self.base_html), parser)
            except:
                print ("Could not Parse")

            try:
                company_name = tree.xpath("//td[@itemprop='legalName']")[0]
                company_name = str(company_name.xpath('./text()')[0])
            except:
                pass

            try:
                phone = tree.xpath("//td[@itemprop='telephone']")[0]
                phone = str(phone.xpath('./text()')[0])
            except:
                pass

            try:
                website = tree.xpath("//a[@itemprop='url']")[0]
                website = str(website.xpath('./text()')[0])
            except:
                pass

            try:
                email_response = requests.get(website)
                import re
                reobj = re.compile(
                    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}\b", re.IGNORECASE
                )
                found_email = re.findall(reobj, str(email_response.text))
                email = ''
                for each_email in found_email:
                    email += str(each_email) + ','
                email = email[0:len(email) - 1]
            except:
                pass

            try:
                zipcode = tree.xpath("//td[@itemprop='postalCode']")[0]
                zipcode = str(zipcode.xpath('./text()')[0])
            except:
                pass

            try:
                street_address = tree.xpath("//td[@itemprop='streetAddress']")[0]
                street_address = str(street_address.xpath('./text()')[0])
            except:
                pass

            try:
                city = tree.xpath("//span[@itemprop='addressLocality']")[0]
                city = str(city.xpath('./text()')[0])
            except:
                pass

            try:
                province = tree.xpath("//span[@itemprop='addressRegion']")[0]
                province = str(province.xpath('./text()')[0])
            except:
                pass
            try:
                db.add_data({
                    'date_scrapped': date_scrapped,
                    'category': unprocessed['category'],
                    'page': unprocessed['page'],
                    'url': nav_link,
                    'company_name': company_name,
                    'zipcode': zipcode,
                    'street_address': street_address,
                    'house_number': house_number,
                    'city': city,
                    'website': website,
                    'email': email,
                    'phone_number': phone
                })
            except:
                print ("Exception")

            db.update_link(unprocessed['link'])
            unprocessed = db.get_one_unprocessed()

soce = Soce()
# for each_category in categories:
#     max_pages = 300
#     for i in range(1, max_pages):
#         nav_link = each_category.lower().replace(' ', '-') + '/' + str(i)
#         soce.get_page(nav_link)
#         soce.parse_links_in_page(each_category, i)

def scrap_data():
    try:
        soce.navigate_page_for_data()
    except:
        scrap_data()

scrap_data()
# soce.export_to_csv()
