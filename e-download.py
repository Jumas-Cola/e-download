
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from multiprocessing import Pool
from selenium import webdriver
from functools import partial
import time
import sys
import os


def init_driver(path=r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'):
    gecko = os.path.normpath(os.path.join(
        os.path.dirname(__file__), 'geckodriver'))
    # ...path to firefox.exe
    binary = FirefoxBinary(path)
    driver = webdriver.Firefox(
        firefox_binary=binary, executable_path=gecko + '.exe')
    driver.wait = WebDriverWait(driver, 5)
    return driver


def file_write(string, file='e-hentai_urls.txt'):
    f = open(file, 'a')
    f.write(str(string) + '\n')
    f.close()


def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]


def pages_scrapper(download, dir, pages):
    driver = init_driver()
    for url in pages:
        try:
            driver.get(url)  # Загружаем страницу
            time.sleep(5)
            img = driver.find_element_by_css_selector('img#img')
            src = img.get_attribute('src')
            file_write(src)
            print(src)
            file = src.split('/')[-1]
            if download:
                urlretrieve(src, dir + '/' + file)
        except:
            file_write('Cant download: ' + url)
            print('Cant download: ' + url)
    driver.quit()


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('--------------------------------------------------\n')
        print('Usage: e-download.py <urls> <download (-t/-f)> <threads>\n')
        exit()

    try:
        urls = open(sys.argv[1], 'r').readlines()
    except:
        try:
            urls = sys.argv[1].split(',')
        except:
            print('[-] Error: Check your urls path\n')
            exit()

    try:
        download = sys.argv[2]
        if download != '-t' and download != '-f':
            raise Exception('Not Bool Type')
        elif download == '-f':
            download = False
        else:
            download = True
    except:
        download = True

    try:
        threads = int(sys.argv[3])
    except:
        threads = 1

    print('--------------------------------------------------\n')
    print('Urls: {}\n'.format(sys.argv[1]))
    print('Need to download: {}\n'.format(str(download)))
    print('Threads: {}\n'.format(str(threads)))

    browser = init_driver()
    alt_dir_num = 0

    for url in urls:
        page = 0
        pages = []
        prev_number = 0

        browser.get(url)  # Загружаем страницу
        print('--------------------------------------------------\n')
        print(url+'\n')
        print('--------------------------------------------------\n')
        time.sleep(5)
        dir = browser.find_element_by_css_selector('h1#gn').text
        number = browser.find_element_by_css_selector('td.ptds').text

        if download:
            try:
                os.makedirs(dir)
                file_write(dir)
            except:
                dir = 'New_Folder_' + str(alt_dir_num)
                while os.path.exists(dir):
                    alt_dir_num += 1
                    dir = 'New_Folder_' + str(alt_dir_num)
                os.makedirs(dir)
                print('[-] Name error. Folder name: ' + dir)
                file_write(dir)

        while number != prev_number:
            links_a = browser.find_elements_by_css_selector(
                'div[class^="gdt"] a')
            for a in links_a:
                href = a.get_attribute('href')
                pages.append(href)
            prev_number = number
            page += 1
            browser.get(url + '?p=' + str(page))  # Загружаем страницу
            time.sleep(5)
            number = browser.find_element_by_css_selector('td.ptds').text

        func = partial(pages_scrapper, download, dir)
        p = Pool(threads)
        p.map(func, chunkify(pages, threads))

    browser.quit()
    time.sleep(5)
    print('--------------------------------------------------\n')
    print('Finished!\n')
