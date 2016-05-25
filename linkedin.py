# _*_ coding:utf-8 _*_
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
    companyId = scrapy.Field()
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
    base_url = 'https://www.linkedin.com'
    custom_settings = {
        "FEED_EXPORT_FIELDS" : ["companyId", "companyname", "firstname" ,"lastname","fullname","profileurl"]
    }
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
                    formdata={'session_key': 'dangduonghung@gmail.com', 'session_password': 'matkhaucuatui123'},
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
                yield scrapy.Request(url, self.parsess, meta={'company_id': id})

            # yield Request('https://www.linkedin.com/vsearch/p?f_CC=208401&trk=rr_connectedness', self.parsess)
            # yield Request('https://www.linkedin.com/vsearch/p?f_CC=3530383&trk=rr_connectedness', self.parsess)
            self.initialized()

        else:
            self.log("Incorrect username/password!")
            # Something went wrong, we couldn't log in, so nothing happens.

    def parsess(self, response):
        self.log("====parse_item")
        print response.url
        print "+++COMPANY_ID***", response.meta['company_id']
        # hxs = HtmlXPathSelector(response)
        # print hxs.xpath('//div[@id="resulfts-container"]').extract()
        with open('log_111.html', 'a') as f:
		    f.write(response.body)


        # self.driver.get(response.url)
        # self.driver.implicitly_wait(20)
        # Scrape data from page
        items = []

        # worked, but include u' :'(
        # commented_json2 =  response.xpath('//code[@id="voltron_srp_main-content"]')[0].xpath('comment()').extract()[0]
        # print(repr(commented_json2))
        # removedTagsJson2 = self.remove_tags(commented_json2)

        # print "after removed tags=============== ", removedTagsJson2
        # soup = BeautifulSoup(response.body, "lxml")
        # soup = BeautifulSoup(response.body, "html.parser")
        soup = BeautifulSoup(response.body, "html5lib")
        # commented_json = soup.find('code', id="voltron_srp_main-content")
        # print soup.prettify()
        # with open('logsoup.html', 'a') as f:
		#     f.write(soup.prettify().encode("utf-8"))

        if soup.find('code', id="voltron_srp_main-content") is None:
            print "========++ no contents for request url"
            return

        code = soup.find('code', id="voltron_srp_main-content").contents[0].replace(r'\u002d', '-')
        json_code = json.loads(code)

        resultPagination = None
        if 'resultPagination' in json_code['content']['page']['voltron_unified_search_json']['search']['baseData']:
            resultPagination = json_code['content']['page']['voltron_unified_search_json']['search']['baseData']['resultPagination']

        # print resultPagination['nextPage']['pageURL']
        if (resultPagination is not None ) and ('nextPage' in resultPagination) and ('pageURL' in resultPagination['nextPage']) and (resultPagination['nextPage']['pageURL'].strip()):
            nextPageUrl =  self.__to_absolute_url(self.base_url, resultPagination['nextPage']['pageURL'].strip())
            yield Request(nextPageUrl, self.parsess, meta={'company_id': response.meta['company_id']})

        employees = json_code['content']['page']['voltron_unified_search_json']['search']['results']

        profiles=[]
        for employee in employees:
            if 'person' not in employee:
                continue

            person = employee['person']
            profileUrl = person["link_nprofile_view_3"] if 'link_nprofile_view_3' in person else person['link_nprofile_view_headless']
            profileUrl = profileUrl[0:profileUrl.index("&")]
            firstName = person["firstName"] if 'firstName' in person else ""
            lastName = person["lastName"] if 'lastName' in person else ""
            fullName = person["fmt_name"] if 'fmt_name' in person else ""
            # company = BeautifulSoup(person['snippets'][0]["heading"]).text
            company = ""
            if ('snippets' in person) and (len(person['snippets']) > 0) and ('heading' in person['snippets'][0]):
                company = self.remove_tags(person['snippets'][0]["heading"])
            else:
                print "company empty=============", repr(person['snippets'])

            company_id = response.meta['company_id']

            item = LikedinItem(companyId=company_id, companyname=company, fullname=fullName, firstname=firstName, lastname=lastName, profileurl=profileUrl)
            profiles.append(item)
            yield item
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
        # print len(profiles)
        # yield profiles

    def get_employee_link(employes):
        profiles=[]
        for employee in employes:
            print employee['person']['link_nprofile_view_3']
            profiles.append(employee['person']['link_nprofile_view_3'])
        return profiles , len(profiles)

    def remove_tags(p, p2):
        # print "remove_tags p++++++++++++++++", repr(p), "remove_tags p2###################", repr(p2)
        # p=str(p)

        soup = BeautifulSoup(p2, 'html.parser')
        print "++++++++++++++++ soup removed tags: ", soup.get_text()
        return soup.get_text()
        # u'<!--{"content":{....."status":"ok"}-->'
        # p3 = repr(p2)
        # return p3[6: -4]

    def __to_absolute_url(self, base_url, link):
        '''
        Convert relative URL to absolute url
        '''

        import urlparse
        link = urlparse.urljoin(base_url, link)
        return link
