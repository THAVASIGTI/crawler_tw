#!/usr/bin/python3

from selenium import webdriver
from selenium.common import exceptions
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os,time,re,csv,logging,getpass

class Broswer():
    def __init__(self):
        #assgin variable
        self.last_position = int()
        self.curr_position = int()
        self.login_url = "https://www.twitter.com/login"

    def set_setup(self):
        try:
            chromeOptions = webdriver.ChromeOptions()
            chromeDriver = ChromeDriverManager().install()
            chromeOptions.add_argument("--start-maximized")
            driver = webdriver.Chrome(executable_path=chromeDriver, chrome_options=chromeOptions)
            return driver
        except Exception as e:
            logging.error(e)
            return None

    def login(self,driver,user,passwd):
        try:
            driver.get(self.login_url)
            time.sleep(3)
            #input fill email id
            username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
            username.send_keys(user)
            #input fill pwd 
            password = driver.find_element_by_xpath('//input[@name="session[password]"]')
            password.send_keys(passwd)
            password.send_keys(Keys.RETURN)
            time.sleep(3)
            return True
        except Exception as e:
            logging.error(e)
            return None

    def search(self,driver,search_qry):
        try:
            #enter search qry
            search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
            search_input.send_keys(search_qry)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            driver.find_element_by_link_text('Latest').click()
            time.sleep(2)
            return True
        except Exception as e:
            print(e)
            return None

    def scroll(self,driver):
        try:
            if 0 is self.last_position:
                self.last_position = driver.execute_script("return window.pageYOffset;")
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            self.curr_position = driver.execute_script("return window.pageYOffset;")
            scroll_attempt = 0
            while True:
                if self.last_position == self.curr_position:
                    if scroll_attempt > 3:
                        return None
                    else:
                        scroll_attempt += 1
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        time.sleep(2)
                        self.curr_position = driver.execute_script("return window.pageYOffset;")
                else:
                    self.last_position = self.curr_position
                    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
                    return page_cards
        except Exception as e:
            logging.error(e)
            return None

class DataParser():
    def __init__(self):
        self.startHeader = int()
    
    def beautify(self,source):
        try:
            for card in source:
                try:
                    username = card.find_element_by_xpath('.//span').text
                except (NoSuchElementException,Exception):
                    username = str()
                
                try:
                    handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
                except (NoSuchElementException,Exception):
                    handle = str()

                try:
                    postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
                except (NoSuchElementException,Exception):
                    postdate = str()

                try:
                    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
                except (NoSuchElementException,Exception):
                    comment = str()

                try:
                    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
                except (NoSuchElementException,Exception):
                    responding = str()

                #join comment and responding
                textComment = str(comment) + str(responding)

                try:
                    reply_cnt = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
                except (NoSuchElementException,Exception):
                    reply_cnt = int()

                try:
                    retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
                except (NoSuchElementException,Exception):
                    retweet_cnt = int()

                try:
                    like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text
                except (NoSuchElementException,Exception):
                    like_cnt = int()

                wraper = [username,handle,postdate,textComment,reply_cnt,like_cnt,retweet_cnt]
                wr = self.csv_file_write(wraper)
                return wr
        except Exception as e:
            logging.error(e)
            return None

    def csv_file_write(self,data):
        try:
            with open('turkcell_tweets.csv', mode='a') as f:
                fs = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if self.startHeader <= 0:
                    header = ['UserName', 'Handle', 'Timestamp', 'Text', 'Comments', 'Likes', 'Retweets']
                    fs.writerow(header)
                    self.startHeader += 1
                fs.writerow(data)
                print(data)
            f.close()
            return True
        except Exception as e:
            logging.error(e)
            return None

class Manager():
    def __init__(self):
        #assgin class object
        self.br = Broswer()
        self.dp = DataParser()

        #assgin variables
        # self.tag = self.getTag()
        # self.user = self.getUser()
        # self.passwd = self.getPasswdOption()
        self.tag = "#CyCloneUpdate"
        self.user = "geneshanthavasi1032000@gmail.com"
        self.passwd = "gtiGTI@1032000"

    def manager(self):
        try:
            driver = self.br.set_setup()
            if driver is not None:
                login = self.br.login(driver,self.user,self.passwd)
                if login is not None:
                    search = self.br.search(driver,self.tag)
                    if search is not None:
                        while True:
                            source_data = self.br.scroll(driver)
                            if source_data is None:
                                logging.info("finish")
                                break
                            else:
                                status = self.dp.beautify(source_data)
                                if status is None:
                                    logging.error("writter error.")
        except Exception as e:
            logging.error(e)


    def getPasswdOption(self):
        try:
            while True:
                self.clear()
                tmp_passwd_option = str(input("\nPassWord Enter Mode:\n1. visible \n2. hidden\n=> "))
                if tmp_passwd_option in "1":
                    tmp_passwd = self.getPasswd(tmp_passwd_option)
                    if tmp_passwd is not None:
                        return tmp_passwd
                elif tmp_passwd_option in "2":
                    tmp_passwd = self.getPasswd(tmp_passwd_option)
                    if tmp_passwd is not None:
                        return tmp_passwd
                else:
                    continue
        except Exception as e:
            logging.error(e)
            return None

    def getPasswd(self,act):
        try:
            tmp_user = str()
            while True:
                if len(tmp_user) > 4:
                    break
                else:
                    self.clear()
                    if act in "1":
                        print("\nEnter PassWord :\n=> ")
                        tmp_user = str(input())
                    elif act in "2":
                        tmp_user = str(getpass.getpass())
            self.clear()
            return tmp_user
        except Exception as e:
            logging.error(e)
            return None

    def getUser(self):
        try:
            tmp_user = str()
            while True:
                if len(tmp_user) > 5:
                    break
                else:
                    self.clear()
                    tmp_user = str(input("\nEnter The Twitter Register Gamil Id :\n=> "))
            return tmp_user
        except Exception as e:
            logging.error(e)
            return None

    def getTag(self):
        try:
            tmp_tag = str()
            while True:
                if len(tmp_tag) > 1:
                    break
                else:
                    self.clear()
                    tmp_tag = str(input("\nEnter The Twitter Search (hash tag , key word) :\n=> "))
            return tmp_tag
        except Exception as e:
            logging.error(e)
            return None
    
    def clear(self):
        try:
            if os.name == "posix":
                os.system("clear")
            else:
                os.system("cls")
        except Exception as e:
            logging.error(e)
if __name__ == "__main__":
    Manager().manager()