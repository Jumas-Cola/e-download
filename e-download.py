
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium import webdriver
from copy import copy
import inspect
import time
import sys
import os


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def init_driver(path = r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'):
	gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))
	#...path to firefox.exe
	binary = FirefoxBinary(path)
	driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko+'.exe')
	driver.wait = WebDriverWait(driver, 5)
	return driver

def file_write(string, file_name=get_script_dir()+"/"+'e-hentai_urls.txt'):
	f = open(file_name,'a')
	f.write(str(string))
	f.write("\n")
	f.close()


if len(sys.argv) <2:
	print("--------------------------------------------------\n")
	print("Usage: e-download.py <urls> <download>\n")
	sys.exit(1)


try:
	urls = open(sys.argv[1], "r").readlines()
except:
	try:
		urls = sys.argv[1].split(',')
	except:
		print("[-] Error: Check your urls path\n")
		sys.exit(1)

try:
	download = sys.argv[2]
	if download!='True' and download!='False':
		raise Exception('Not Bool Type')
	elif download=='False':
		download = False
	else:
		download = True
except:
	download = True

print("--------------------------------------------------\n")
print("Urls: {}\n".format(sys.argv[1]))
print("Need to download: {}\n".format(str(download)))


browser = init_driver()
for url in urls:
	browser.get(url) # Загружаем страницу
	time.sleep(5)
	name = browser.find_element_by_css_selector("h1#gn").text
	alt_name = 0
	number = browser.find_element_by_css_selector("td.ptds").text
	prev_nunber = 0
	page = 0
	pages = []

	if download:
		try:
			os.makedirs(get_script_dir()+"/"+name)
			file_write(name)
		except:
			name = str(alt_name)
			print("Name error. Folder name: "+name)
			os.makedirs(get_script_dir()+"/"+name)
			file_write(name)
			alt_name+=1

	while number!=prev_nunber:
		place_block = browser.find_elements_by_css_selector("div.gdtm > div > a")
		for block in place_block:
			place_img = block.get_attribute('href')
			pages.append(place_img)
		prev_nunber = number
		page+=1
		browser.get(url+"?p="+str(page)) # Загружаем страницу
		time.sleep(5)
		number = browser.find_element_by_css_selector("td.ptds").text


	for url in pages:
		try:
			browser.get(url) # Загружаем страницу
			time.sleep(5)
			place_block = browser.find_element_by_css_selector("img#img")
			place_img = place_block.get_attribute('src')
			file_write(place_img)
			print(place_img)
			file = place_img.split('/')[-1]
			if download:
				urlretrieve(place_img, get_script_dir()+"/"+name+'/'+file)
		except:
			file_write('Cant download: '+url)
			print('Cant download: '+url)

browser.quit()
time.sleep(5)
print("--------------------------------------------------\n")
print("Finished!\n")
