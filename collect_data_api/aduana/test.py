import os
from typing import Dict
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

EXPORTATION_TYPE = 0
IMPORTATION_TYPE = 1
WEIGHT_TYPE = 0
AMOUNT_TYPE = 1

DOMAIN = 'https://www.aduana.cl'
URLS = [
    '/exportacion-por-lugar-de-salida/aduana/2018-12-14/103453.html',
    '/importaciones-por-lugar-de-ingreso/aduana/2018-12-14/102639.html',
    '/trafico-terrestre/aduana/2018-12-14/110201.html'
]

def main():
    # Data to be loaded in DB
    land_traffic_data = []
    imp_exp_data = []

    # Download files
    year = 2022
    for url in URLS:
        download_file(url, year) 
    
    files = os.listdir(os.getcwd())
    for file in files:
        if file.endswith('.xlsx'):
            # Get data from file
            print("Extracting file %s" % file)
            if file.startswith('trafico_terrestre'):
                land_traffic_data = get_land_traffic_data(file)
            else:
                imp_exp_data.append({
                    'filename': file,
                    'type': EXPORTATION_TYPE if file.startswith('expo') else IMPORTATION_TYPE,
                    'data_type': WEIGHT_TYPE if file.find('peso') != -1 else AMOUNT_TYPE,
                    'data': get_imp_exp_data(file)
                })
            # Delete file
            os.remove(file)
    
    # Load data into DB
    # JSON Example
    with open('json_data.json', 'w') as outfile:
        json.dump(imp_exp_data, outfile)
                
def download_file(URL: str, year: int):
    page = requests.get(f'{DOMAIN}/{URL}')
    soup = BeautifulSoup(page.content, "html.parser")
    files_html = soup.find_all("a", string=str(year))
    
    files_urls = []
    files_names = []
    for html_url in files_html:
        file_url = html_url.get('href')
        file_name = file_url.split('/')[-1]
        if file_url.endswith('.xlsx'):
            files_urls.append(f'{DOMAIN}{file_url}')
            files_names.append(file_name)

    for name, url in zip(files_names,files_urls):
        print('Downloading %s' % name)
        os.system(f'curl -o {name} {url}')

def transform_land_traffic_data(dataset: Dict):
    pass

def get_land_traffic_data(file: str):
    pass       

def tranform_imp_exp_data(dataset: Dict):
    del dataset['Unnamed: 0']
    del dataset['Unnamed: 11']
    data = {
        'name': None,
        'year': None,
        'months_data': []
    }

    for text, value in dataset.items():
        if text.find('Lugar') != -1: # Name of aduana center
            data['name'] = value
        else:
            month, year = text.split('-')
            if not data['year']:
                data['year'] = int(year.strip())

            data['months_data'].append((month.strip(), value))
            
    return data

def get_imp_exp_data(file: str):    
    workbook = pd.read_excel(file, skiprows=[0,1,2])
    datasets = workbook.to_dict('records')[:-2]
    aduana_centers_datasets = []
    for data in datasets:
        transformed_data = tranform_imp_exp_data(data)
        aduana_centers_datasets.append(transformed_data)
        
    return aduana_centers_datasets

if __name__ == "__main__":
    main()