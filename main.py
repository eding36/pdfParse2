import pandas as pd
import numpy as np
import urllib.request
from urllib import request
from bs4 import BeautifulSoup
import requests
import time
import os
import pdfplumber



"""Read in raw data, gather all url links to drug information page"""

master_df = pd.read_csv('EPAR_table_4.csv',header = 0,skiprows = 8)
df = master_df[master_df['Category'] == 'Human']
df2 = df[df['Authorisation status'] == 'Authorised']

url_list = df2['URL'].tolist()
print(url_list)


"""Parses through html code of the drug information page to find the drug information pdf containing pregnancy/pediatric use case information"""

product_info_url_list = []
for i in range(len(url_list)):
    success = False
    print(i)
    while not success:   
        link = url_list[i]
        response = requests.get(link)
        if response.status_code == 200:  
            web_content = response.text
            soup = BeautifulSoup(web_content, 'html.parser')
            soups = soup.find_all('a')
            href_links = [tag.get('href') for tag in soups]
            for j in range(len(href_links)):
                if '/en/documents/product-information' in str(href_links[j]):
                    product_info_url_list.append(str(href_links[j]))
            success = True
        else:
            print('error')
            time.sleep(15)
            
"""Download pdf files to source through them locally"""

os.makedirs('pdf_files', exist_ok=True)
# Iterate through the list of URLs
for i, url in enumerate(product_info_url_list[1298:], start=1298):
        # Send a GET request to the URL
    success = False
    while not success:
        response = requests.get('https://www.ema.europa.eu'+ url)
    
        # Check if the request was successful
        if response.status_code == 200:
                # Define the PDF file name
            pdf_file_name = os.path.join('pdf_files', f'{str(product_info_url_list[i]).replace("/","-")}')
    
                # Write the content to a PDF file
            with open(pdf_file_name, 'wb') as pdf_file:
                    pdf_file.write(response.content)
    
            print(f"Downloaded: {pdf_file_name}")
            success = True
        else:
            print('error')
            time.sleep(15)

"""Read in drug information pdf files, extract sentences in pdf files with keywords related to children and pregnant women"""

keywords = ['children','pediatric','pregnant','childbearing','breastfeeding']
useful_info = []
files = os.listdir('pdf_files')

# Filter out only the PDF files
pdf_files = [f for f in files if f.endswith('.pdf')]
i=0
# Iterate through each PDF file
for pdf_file in pdf_files:
    print(i)
    useful_info_row = []
    pdf_path = os.path.join('pdf_files', pdf_file)
    useful_info_row.append(pdf_path.split('-')[5])
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = []
            for page in pdf.pages:
                pdf_text.append(page.extract_text())
            for j in range(len(pdf_text)):
                text = pdf_text[j]
                sentence_list = text.split('.')
                for k in range(len(sentence_list)):
                    if any(keyword in sentence_list[k] for keyword in keywords):
                        sentence_clean = sentence_list[k].replace('\n','').lstrip()
                        useful_info_row.append(sentence_clean)
        useful_info.append(useful_info_row)
        i=i+1
    except Exception:
        i=i+1
        continue
    
"""Format export file format"""
  
final_info_list = []
for i in range(len(useful_info)):
    lst = useful_info[i]
    new_list = [lst[0],lst[1:]]
    final_info_list.append(new_list)

print(len(final_info_list))

"""Export csv file with drug name corresponding to it's use cases for pregnant women and children."""

import pandas as pd
final_df = pd.DataFrame(final_info_list, columns = ['drug name', 'relevant info'])
print(final_df)
final_df.to_csv('pediatric and pregnancy info for EMA drugs.csv')
