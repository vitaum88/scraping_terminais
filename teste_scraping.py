from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

import time
import pandas as pd
import datetime as dt
import xlsxwriter
import excel2img

PATH = r'D:\programas\executables\chromedriver.exe'
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options, executable_path=PATH)
driver.maximize_window()

agora = dt.datetime.now()


# PARANAGUA

URL = 'https://cliente.tcp.com.br/publico/programacao/navios'

driver.get(URL)
time.sleep(5)

dias_gate_png = 5
header_row = driver.find_element_by_css_selector('.mat-header-row')
rows = driver.find_elements_by_css_selector('.mat-row')
splitted_rows = map(lambda x: x.text.split('\n'), rows)
png = pd.DataFrame(columns=header_row.text.split('\n'), data=splitted_rows)
png.DeadLine = pd.to_datetime(png.DeadLine, dayfirst=True, errors = 'coerce')
png.dropna(subset=['DeadLine'], inplace=True)
png = png[(png.DeadLine > agora)&(png['Nome Navio'].str.contains('Mercosul|Login'))]
png['Abertura do Gate'] = png.DeadLine - dt.timedelta(days=dias_gate_png)
png['Gate'] = png['Abertura do Gate'].apply(lambda x: 'Já abriu' if agora > x else 'Ainda fechado')


print('\n\n')
print('TCP - Paranaguá')
print(png[['Nome Navio','Viagem TCP','Abertura do Gate','DeadLine','Gate']].sort_values(by='DeadLine'))


# SANTOS - DPW

URL = 'http://www.embraportonline.com.br/Navios/Escala' 

driver.get(URL)
time.sleep(2)

button = driver.find_element_by_id('ornext')
df = pd.read_html(driver.page_source)[0]
ActionChains(driver).click(button).perform()
time.sleep(5)
df = df.append(pd.read_html(driver.page_source)[0])
ActionChains(driver).click(button).perform()
time.sleep(5)
df = df.append(pd.read_html(driver.page_source)[0])

ssz = df[['Navio','Serviço','Abertura de Gate','Deadline (Armador)']][df['Serviço'].isin(['SAS','NEXCO','BRACO'])]
ssz['Abertura de Gate'] = pd.to_datetime(ssz['Abertura de Gate'], dayfirst=True)
ssz['Deadline (Armador)'] = pd.to_datetime(ssz['Deadline (Armador)'], dayfirst=True)
ssz['Gate'] = ssz['Abertura de Gate'].apply(lambda x: 'Já abriu' if agora > x else 'Ainda fechado')

print('\n\n')
print('Embraport - SANTOS')
print(ssz.sort_values(by='Deadline (Armador)'))


# ITAJAÍ - APM

URL = 'https://www.apmterminals.com/pt/itajai/practical-information/vessel-schedule'
itj = pd.DataFrame()
for armador in ['Mercosul','Log-in']:
    driver.get(URL)
    s = driver.find_element_by_class_name('vessel-schedule-filters__search-input')
    s.send_keys(armador)
    s.send_keys(Keys.RETURN)
    time.sleep(5)
    resultados = int(driver.find_element_by_class_name('vessel-schedule__results-val').text)
    
    if resultados:
        tables = pd.read_html(driver.page_source)
        nomes = driver.find_elements_by_class_name('vessel-schedule__title')
        nomes = list(map(lambda x: x.split('|')[0].split('Chegando'), map(lambda x: x.text, nomes)))
        df = pd.concat(tables)
        df['Navio'] = [nome[0] for nome in nomes]
        df['Viagem'] = [nome[1] for nome in nomes]
        
        itj = itj.append(df)

if itj.shape[0]:
    itj['Abertura do Gate'] = pd.to_datetime(itj['Abertura do Gate'], dayfirst=True)
    itj['Fechamento do Gate'] = pd.to_datetime(itj['Fechamento do Gate'], dayfirst=True)
    itj['Gate'] = itj['Abertura do Gate'].apply(lambda x: 'Já abriu' if agora > x else 'Ainda fechado')
    
    print('\n\n')
    print('ITAJAÍ - APM')
    print(itj[['Navio','Viagem','Abertura do Gate','Fechamento do Gate','Gate']].sort_values(by='Fechamento do Gate'))

driver.quit()
