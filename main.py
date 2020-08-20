import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import key
from Crypto.PublicKey import RSA
from selenium.webdriver.common.keys import Keys
from multiprocessing.pool import ThreadPool

Click = False
num_of_process = 2  

#return a string formatted MMDDYY_HHMM
def makedir_now():
    now = datetime.datetime.now()
    date_dir = now.strftime('%m%d%y_%H%M')
    try:
        os.mkdir(date_dir)
    except Exception as e:
        print(e)
    return date_dir

screenshot_cnt = 0

def shot(browser, dt_str):
    global screenshot_cnt
    browser.save_screenshot(dt_str + '//' + str(screenshot_cnt) + '.png')
    screenshot_cnt += 1


def login(browser, k):
    u = key.get_username(k)
    usr = u.decode('utf-8')
    p = key.get_pwd(k)
    pwd = p.decode('utf-8')
    login = browser.find_element_by_xpath(
        "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[3]/div/div[1]/div[1]/button")
    login.click()
    time.sleep(1)
    username = browser.find_element_by_id("login-username")
    for c in usr:
        username.send_keys(c)

    password = browser.find_element_by_id("password-input")
    for c in pwd:
        password.send_keys(c)
    password.send_keys(Keys.ENTER)


def authenticate(browser):
    auth = input('Authentication code is ')
    box = browser.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div/div[1]/div/div/div[2]/input')
    box.send_keys(auth)
    box.send_keys(Keys.ENTER)

    ''' Authenticate with email
    boxes = browser.find_elements_by_xpath(
        '/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div/div/input')
    count = 0
    for x in boxes:
        x.send_keys(auth[count])
        count += 1
    '''

def point(browser):
    global Click
    while True:
        if not Click:
            return
        try:
            wait = WebDriverWait(browser, 3)
            point_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/section/div/div[5]/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/button')))
            point_box.click()
            
            #= browser.find_element_by_xpath('//*[@id="c02bcaccfd7eb3a1da8dffb74cabcfb8"]/div/div[1]/div/div/div/div/div/section/div/div[5]/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/button')
        except Exception as e:
            pass
            #print(e, type(e))
    # state of outside div
    # tw-transition tw-transition--exit-done tw-transition__fade tw-transition__fade--exit-done

def main():
    global Click
    pool = ThreadPool(num_of_process)

    dt_str = makedir_now()
    f = open('key', 'r')
    K = RSA.importKey(f.read())
    f.close()


    browser = webdriver.Chrome()
    browser.set_window_size(1366, 768)
    browser.get('http://www.twitch.tv/never_loses')

    while True:
        cmd = input('command: ')
        if(cmd == 'goto') :
            addr = input('input the url: ')
            browser.get('http://' + addr)
            print('redirecting to http://' + addr)
        elif(cmd[0] == 'q'):
            browser.quit()
            break
        elif cmd[0] == 's':
            shot(browser, dt_str)
        elif cmd[0] == 'l':
            login(browser, K)
        elif cmd[0] == 'a':
            authenticate(browser)
        elif cmd[0] == 'c':
            if Click:
                print('Auto click is now off')
                Click = False
                pool.terminate()
                pool.join()
            else:
                print('Auto click is now on')
                Click = True
                pool = ThreadPool(num_of_process)
                pool.apply_async(point, (browser,))


if __name__ == "__main__":
    main()


# green box
# /html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/section/div/div[5]/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/button/span/div/div/div/svg/g/path
# /html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/section/div/div[5]/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/button
