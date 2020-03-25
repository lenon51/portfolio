from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import re
import autoit
import urllib
from datetime import datetime
from TypeSource import TypeSource 
import pyperclip
class Instagram():
    def __init__(self, username, password, user_agent_mobile=False):
        self.browserProfile = webdriver.ChromeOptions()
        
        if user_agent_mobile:
            self.browserProfile.add_argument("--user-agent=Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>")
        
        #Escolher o browser
        b = 1
        if b == 1:
            self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
            self.browser = webdriver.Chrome('chromedriver.exe',chrome_options=self.browserProfile)
        else:
            self.browser = webdriver.Firefox(executable_path='geckodriver.exe')
            
        self.username = username
        self.password = password
        self.url_base = 'https://www.instagram.com/'
        self.path = 'c:\\temp\\'

    def convertValue(self, value):
        value = ''.join(re.findall('[^,]', value))
        '''Converter k e m para milhares e milhões respectivamente'''
        if value.find('k') >= 0:
            value = int(round(float(value.replace('k','')) * 1000))
        elif value.find('m') >= 0:
            value = int(round(float(value.replace('m','')) * 10000000))            

        return value    
    
    def signIn(self):
        self.browser.get(self.url_base + 'accounts/login/')

        time.sleep(5)
        emailInput = self.browser.find_element_by_xpath('//*[@name="username"]')
        passwordInput = self.browser.find_element_by_xpath('//*[@name="password"]')

        emailInput.send_keys(self.username)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        time.sleep(5)
        
    def followUser(self, username):
        self.browser.get(self.url_base + username + '/')
        time.sleep(2)
        try:
            followButton = self.browser.find_element_by_xpath('//button[text() = "Follow"]')
            if (followButton.text != 'Following'):
                followButton.click()
                time.sleep(8)
            return True
        except:            
            print('Usuário não existe: {}'.format(username))
        return False
            
    def unfollowUser(self, username):
        self.browser.get(self.url_base + username + '/')
        time.sleep(2)
        try:
            followButton = self.browser.find_element_by_css_selector('button')
            if (followButton.text == 'Following'):
                followButton.click()
                time.sleep(8)
                confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
                confirmButton.click()
                time.sleep(5)
            return True
        except:
            print('Usuário não existe: {}'.format(username))
        return False
    
    def searchPicture(self, source, type_source):
        
        if type_source == TypeSource.Hashtag:
            url = self.url_base + 'explore/tags/' + source +'/'
        else:
            url = self.url_base + source
        
        self.browser.get(url)
        time.sleep(5)
        lst_post = self.browser.find_elements_by_xpath('//div[@class="v1Nh3 kIKUG  _bz0w"]/a')
        return [item.get_attribute("href").replace(self.url_base,'') for item in lst_post]
            
    def saveComment(self, url, text):
        self.browser.get(self.url_base + url)
        time.sleep(5)
        text = pyperclip.copy(text)
        if not self.browser.find_elements_by_xpath('//body[@class=" p-error dialog-404"]'):
            comment = lambda: self.browser.find_element_by_xpath("//textarea[@aria-label='Add a comment…']")
            try:
                comment().click()
                comment().clear()
                comment().send_keys(Keys.CONTROL,'v')
                time.sleep(5)
                comment().send_keys(Keys.ENTER)
                time.sleep(5)
            except:
                print('Não aceita comentário')

    def saveLike(self, url):
        self.browser.get(self.url_base + url)
        time.sleep(5)
        if not self.browser.find_elements_by_xpath('//body[@class=" p-error dialog-404"]'):
            button = self.browser.find_element_by_xpath('//*[@class="wpO6b "]')
            button.click() 
            time.sleep(5)
        
    def getPictureHistoric(self, url):
        self.browser.get(self.url_base + url)
        time.sleep(5)
        like = self.browser.find_elements_by_xpath('//div[@class="Nm9Fw"]')
        date_post = self.browser.find_elements_by_xpath('//time[@class="_1o9PC Nzb55"]')
        tag = self.browser.find_elements_by_xpath('//span[@class="eg3Fv"]')
        user = self.browser.find_elements_by_xpath('//a[@class="FPmhX notranslate  nJAzx"]')
        desc = self.browser.find_elements_by_xpath('//div[@class="C4VMK"]/span')        
        
        lst = {}
        lst['like'] = 0
        if len(like) > 0:
            lst['like'] = int(re.findall('(\d* (?:(?:others|other)|(?:likes|like)))',
                                         like[0].text)[0].replace(' others','').replace(' other','').replace(' likes','').replace(' like',''))
        if len(date_post) > 0:
            lst['date'] = date_post[0].get_attribute('datetime')        
            lst['user'] = user[0].text
        
        lst['description'] = ''
        if len(desc) > 0:
            lst['description'] = ''.join(re.findall('[\w# \d%@]', desc[0].text.replace('\n',' ')))
        
        lst_tag = []
        for item in tag:
            lst_tag.append(item.get_attribute("innerHTML"))
        
        lst['tag'] = ','.join(lst_tag)
        return lst
        
    def postPicture(self, image, text):
        text = pyperclip.copy(text)
        self.browser.get(self.url_base + self.username)
        time.sleep(5)
        button = self.browser.find_element_by_xpath('//*[@class="q02Nz _0TPg"]')
        button.click()
        time.sleep(5)
        handle = "[CLASS:#32770; TITLE:Open]"        
        autoit.control_set_text(handle, "Edit1", image)
        autoit.control_click(handle, "Button1")
        time.sleep(5)
        button = self.browser.find_element_by_xpath('//*[@class="UP43G"]')
        button.click()
        time.sleep(5)
        comment = lambda: self.browser.find_element_by_xpath("//textarea[@aria-label='Write a caption…']")
        comment().click()
        comment().clear()
        #comment().send_keys(text)
        comment().send_keys(Keys.CONTROL,'v')
        time.sleep(5)
        button = self.browser.find_element_by_xpath('//*[@class="UP43G"]')
        button.click()
        
    def getAccount(self, username):
        self.browser.get(self.url_base + username + '/')
        time.sleep(5)
        lst = {}
        lst['username'] = username        
        lst['post'] = '0'
        lst['follower'] = '0'
        lst['follow'] = '0'
        lst['private'] = False
        lst['bio'] = ''
        
        if not self.browser.find_elements_by_xpath('//body[@class=" p-error dialog-404"]'):
            header = self.browser.find_elements_by_xpath('//span[@class="g47SY "]')
            if len(header) > 0:
                lst['post'] = self.convertValue(header[0].text)
                lst['follower'] = self.convertValue(header[1].text)
                lst['follow'] = self.convertValue(header[2].text)
            
            if len(self.browser.find_elements_by_xpath('//h2[@class="rkEop"]')) > 0:
                lst['private'] =  True
            
            description = self.browser.find_elements_by_xpath('//div[@class="-vDIg"]')
            if len(description) > 0:
                lst['bio'] = description[0].text
            
        time.sleep(5)
        return lst

    def getFollower(self, username):
        self.browser.get(self.url_base + username +'/')
        time.sleep(5)
        header = self.browser.find_elements_by_xpath('//span[@class="g47SY "]')
        follower = header[1]
        qty_follower = self.convertValue(header[1].text)
        follower.click()
        time.sleep(5)
        box = self.browser.find_elements_by_xpath('//div[@role="dialog"]')
        time.sleep(5)
        script = '''var fDialog = document.querySelector('div[role="dialog"] .isgrP'); fDialog.scrollTop = %s'''
        try:
            for index in range(1, int(qty_follower)*50, 500):
                self.browser.execute_script(script % index, box)
                time.sleep(3)
        except Exception as e: 
            print(e)
       
        lst_follower = self.browser.find_elements_by_xpath('//a[@class="FPmhX notranslate  _0imsa "]')
        ret_follower = []
        for item in lst_follower:
            ret_follower.append(item.text)
            
        return ret_follower
    
    def getPost(self, url):
        self.browser.get(self.url_base + url)
        time.sleep(10)
        image = self.browser.find_elements_by_xpath('//img[@class="FFVAD"]')
        #user = self.browser.find_elements_by_xpath('//h2[@class="BrX75"]')
        user = self.browser.find_elements_by_xpath('//a[@class="sqdOP yWX7d     _8A5w5   ZIAjV "]')

        try:
            lst = {}
            lst['image'] = image[0].get_attribute("src")
            lst['username'] = user[0].text

            filename = '{}_{}_{}_{}_{}_{}_{}.jpg'.format(datetime.now().year, 
                                                     datetime.now().month, 
                                                     datetime.now().day, 
                                                     datetime.now().hour, 
                                                     datetime.now().minute, 
                                                     datetime.now().second,
                                                     lst['username'])      
            urllib.request.urlretrieve(lst['image'], 
                                       self.path + filename)
            time.sleep(5)

            return self.path + filename
        except:
            print('Não é imagem.')
            
        return None 

    def getStories(self):
        button = self.browser.find_elements_by_xpath('//a[@class="sqdOP yWX7d     _8A5w5   ZIAjV "]')
        warning = self.browser.find_elements_by_xpath('//button[text() = "Not Now"]')
        if len(warning) > 0:
            warning[0].click()
            time.sleep(3)
        button[0].click()
        time.sleep(300)       
    
    def closeBrowser(self):
        self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()