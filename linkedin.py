# -*- coding: utf-8 -*-
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser
# from selenium import webdriver
from scrapy.selector import HtmlXPathSelector
from bs4 import BeautifulSoup
import json
import scrapy
#from scrapy.linkextractors.sgml import SgmlLinkExtractor
#from scrapy.spiders import Rule

class LikedinItem(scrapy.Item):
    # define the fields for your item here like:
    companyname = scrapy.Field()
    fullname = scrapy.Field()
    firstname = scrapy.Field()
    lastname = scrapy.Field()
    profileurl = scrapy.Field()

class MySpider(InitSpider):
    name = 'myspider'
    #allowed_domains = ['linkedin.com']
    login_page = 'https://www.linkedin.com/uas/login'
    start_urls = ['https://www.linkedin.com/vsearch/p?f_CC=3530383&trk=rr_connectedness']
    ids = []
    #extractor = SgmlLinkExtractor()

    #rules = (
        #Rule(extractor,
            #callback='parse_items', follow=True),
    #)

    #def start_requests(self):
        #yield Request('https://www.linkedin.com/vsearch/p?f_CC=3530383&trk=rr_connectedness', self.parse)

    def init_request(self):
        """This function is called before crawling starts."""
        f = open("linkedinIds.csv", "r")
        self.ids = [url.strip() for url in f.readlines()]
        f.close()
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """Generate a login request."""
        return FormRequest.from_response(response,
                    formdata={'session_key': 'xxx@gmail.com', 'session_password': 'xxx'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if "Sign Out" in response.body:
            print "huhuhuhuhuh"
            self.log("Successfully logged in. Let's start crawling!")
            # self.driver = webdriver.Chrome()
            # Now the crawling can begin..
            # f = open("linkedinIds.csv", "r")
            # ids = [url.strip() for url in f.readlines()]
            # f.close()
            for id in self.ids:
                url = 'https://www.linkedin.com/vsearch/p?f_CC=%s&trk=rr_connectedness' % id
                print "url=======%s" % url
                yield scrapy.Request(url, self.parsess)

            # yield Request('https://www.linkedin.com/vsearch/p?f_CC=208401&trk=rr_connectedness', self.parsess)
            # yield Request('https://www.linkedin.com/vsearch/p?f_CC=3530383&trk=rr_connectedness', self.parsess)
            self.initialized()

        else:
            self.log("Bad times :(")
            # Something went wrong, we couldn't log in, so nothing happens.

    def parsess(self, response):
        self.log("====parse_item")
        print response.url
        # hxs = HtmlXPathSelector(response)
        # print hxs.xpath('//div[@id="results-container"]').extract()
        with open('log_fpt.html', 'a') as f:
		    f.write(response.body)


        # self.driver.get(response.url)
        # self.driver.implicitly_wait(20)
        # Scrape data from page
        items = []

        # worked, but include u' :'(
        commented_json2 =  response.xpath('//code[@id="voltron_srp_main-content"]')[0].xpath('comment()').extract()[0]
        # print(repr(commented_json2))
        # removedTagsJson2 = self.remove_tags(commented_json2)

        # print "after removed tags=============== ", removedTagsJson2
        soup = BeautifulSoup(response.body, "lxml")
        # commented_json = soup.find('code', id="voltron_srp_main-content")
        print soup.code
        code = soup.find('code', id="voltron_srp_main-content").contents[0].replace(r'\u002d', '-')
        json_code = json.loads(code)

        employees = json_code['content']['page']['voltron_unified_search_json']['search']['results']
        # print employees
        # return employees
        # company_list = []
        # company_list = []
        profiles=[]
        for employee in employees:
            person = employee['person']
            profileUrl = person["link_nprofile_view_3"] if 'link_nprofile_view_3' in person else person['link_nprofile_view_headless']
            profileUrl = profileUrl[0:profileUrl.index("&")]
            firstName = person["firstName"] if 'firstName' in person else ""
            lastName = person["lastName"] if 'lastName' in person else ""
            fullName = person["fmt_name"] if 'fmt_name' in person else ""
            company = BeautifulSoup(person['snippets'][0]["heading"]).text
            item = LikedinItem(companyname=company, fullname=fullName, firstname=firstName, lastname=lastName, profileurl=profileUrl)
            profiles.append(item)
            # company_list.append("%s\t%s\t%s\t%s\n" % (name, fmt_industry, fmt_size, fmt_location))

        # for profile in profiles:
        #     with open('some.csv', 'wb') as f:
        #         f.write(profile.companyname & "," & profile.firstName & "," & profile.lastName & "," & profile.profileUrl)
            # writer = csv.writer(f)
            # writer.writerows(someiterable)
        # return profiles

        #print response.xpath('//code/text()').extract()[0]
        #with open('log.txt', 'a') as f:
		    #f.write(response.body)
        #open_in_browser(response)
        # for li in response.xpath('//div[@id="results-container"]/ol[@id="results"]/li'):
        #     aElement = li.xpath('div[@class="bd"]/h3/a')
        #     companies = li.xpath('//p[@class="title"]/b')
        #     print len(companies)
        #     companie = " ".join([company.xpath('text()').extract()[0] for company in companies])
        #     fullName = aElement.xpath('text()').extract()[0]
        #     fullNames = fullName.split(" ")
        #     firstName = ""
        #     lastName = ""
        #
        #     if len(fullNames) > 1:
        #         firstName = fullNames[0]
        #         fullNames.pop(0)
        #         lastName = " ".join(fullNames)
        #     profileUrl = aElement.xpath('@href').extract()[0]
        #     profileUrl = profileUrl[0:profileUrl.index("&")]
        #     items.append(item)
        #
        #     item = LikedinItem(companyname=companie, fullname=fullName, firstname=firstName, lastname=lastName, profileurl=profileUrl)
        #     items.append(item)
        print len(profiles)
        return profiles

    def get_employee_link(employes):
        profiles=[]
        for employee in employes:
            print employee['person']['link_nprofile_view_3']
            profiles.append(employee['person']['link_nprofile_view_3'])
        return profiles , len(profiles)

    def remove_tags(p, p2):
        print "remove_tags p++++++++++++++++", repr(p), "remove_tags p2###################", repr(p2)
        # p=str(p)

        # u'<!--{"content":{....."status":"ok"}-->'
        p3 = repr(p2)
        return p3[6: -4]
