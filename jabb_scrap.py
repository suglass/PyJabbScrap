import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
from selenium.webdriver.common.proxy import Proxy, ProxyType
from twocaptcha import TwoCaptcha
import requests
import random
import pyautogui

def enter_proxy_auth(proxy_username, proxy_password):
    time.sleep(1)
    pyautogui.typewrite(proxy_username)
    pyautogui.press('tab')
    pyautogui.typewrite(proxy_password)
    pyautogui.press('enter')

pyautogui.FAILSAFE = False
registered_file = open("success_registered.txt", "a")
accounts_failed_file = open("accounts_failed.txt", "a")

captcah_err_list = [
    'ERROR_ZERO_CAPTCHA_FILESIZE',
    'ERROR_WRONG_USER_KEY',
    'ERROR_KEY_DOES_NOT_EXIST',
    'ERROR_ZERO_BALANCE',
    'ERROR_PAGEURL',
    'ERROR_NO_SLOT_AVAILABLE',
    'ERROR_TOO_BIG_CAPTCHA_FILESIZE',
    'ERROR_WRONG_FILE_EXTENSION',
    'ERROR_IMAGE_TYPE_NOT_SUPPORTED',
    'CAPCHA_NOT_READY'
]

accounts_to_register = open("accounts_to_register.txt", "r")
for account_line in accounts_to_register:
    account_one = account_line
    if account_line.find('\n') != -1:
        account_one = account_line[:account_line.find('\n')]
    account_one = account_one.strip()
    user = account_one.split(":")[0]
    userpass = account_one.split(":")[1]

    retry_num = 0
    while True:
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

            proxy_file = open("proxy.txt", "r")
            proxy_list = proxy_file.readlines()
            proxy_line = random.choice(proxy_list)
            proxy = proxy_line
            if proxy_line.find('\n') != -1:
                proxy = proxy_line[:proxy_line.find('\n')]
            proxy = proxy.strip()

            proxy_ip = proxy.split(":")[0]
            proxy_port = proxy.split(":")[1]
            proxy_user = proxy.split(":")[2]
            proxy_password = proxy.split(":")[3]

            ### case 1 ###
            proxy = Proxy()
            proxy.proxyType = ProxyType.MANUAL
            proxy.autodetect = False
            proxy_string = proxy_ip + ":" + proxy_port
            proxy.httpProxy = proxy.sslProxy = proxy.socksProxy = proxy_string
            proxy.socksPassword = proxy_password
            proxy.socksUsername = proxy_user
            chrome_options.Proxy = proxy
            ### end case 1 ###

            chrome_options.add_argument('start-maximized')
            chrome_options.add_argument('--disable-gpu-vsync')
            chrome_options.add_argument('disable-infobars')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            ### case 2 ###
            chrome_options.add_argument('--proxy-server={}'.format(proxy_string))
            ### end case 2 ###

            chrome_driver = webdriver.Chrome(options=chrome_options)
            chrome_driver.implicitly_wait(5)
            chrome_driver.maximize_window()

            chrome_driver.get("https://jabb.im/reg/")
            chrome_driver.implicitly_wait(5)
            ### case 2 ###
            enter_proxy_auth(proxy_user, proxy_password)
            ### case 2 ###

            chrome_driver.implicitly_wait(5)

            domains = Select(chrome_driver.find_element(By.ID, 'domain'))
            domains.select_by_index(random.randint(0, 12))
            domain = domains.first_selected_option.text

            chrome_driver.find_element('id', 'vyraz').send_keys(user)
            time.sleep(1)
            chrome_driver.find_element('id', 'antispam').click()
            time.sleep(1)
            chrome_driver.find_element('id', 'pass1').send_keys(userpass)
            time.sleep(1)
            chrome_driver.find_element('id', 'pass2').send_keys(userpass)
            time.sleep(2)

            captcha_elem = chrome_driver.find_element(By.CLASS_NAME, "g-recaptcha")
            captcha_res_elem = chrome_driver.find_element(By.ID, "g-recaptcha-response")
            captcha_sitekey = captcha_elem.get_attribute("data-sitekey")

            config = {
                        'server':           '2captcha.com',
                        'apiKey':           '41ff0b3cd08e27c7aaaff9420b294fda',
                        'softId':            123,
                        'callback':         'https://jabb.im/reg/',
                        'defaultTimeout':    120,
                        'recaptchaTimeout':  600,
                        'pollingInterval':   10,
                    }

            solver = TwoCaptcha(**config)
            result = solver.recaptcha(sitekey=captcha_sitekey, url='https://jabb.im/reg/', version='v2')
            captcha_id = result['captchaId']
            print(captcha_id)

            url = 'http://2captcha.com/res.php?key=41ff0b3cd08e27c7aaaff9420b294fda&action=get&id=' + captcha_id
            token = ''
            while(True):
                response = requests.get(url)
                token = response.text
                print(token)
                if (token not in captcah_err_list):
                    break
                time.sleep(10)
            token = token[3:]
            print(token)

            script = "document.getElementById('g-recaptcha-response').innerHTML='" + token + "'"
            chrome_driver.execute_script(script)

            register_elem = WebDriverWait(chrome_driver, 20).until(EC.element_to_be_clickable((By.ID, "button")))
            register_elem.click()

            success = WebDriverWait(chrome_driver, 20).until(EC.element_to_be_clickable((By.ID, "success")))
            registered_file.write(user + "@" + domain + ":" + userpass + "\r\n")
            time.sleep(3)
            chrome_driver.close()
            chrome_driver.quit()
            proxy_file.close()
            break
        except Exception as ex:
            chrome_driver.close()
            chrome_driver.quit()
            retry_num += 1
        if retry_num > 2:
            accounts_failed_file.write(user + ":" + userpass + "\r\n")
            break

registered_file.close()
accounts_failed_file.close()
accounts_to_register.close()