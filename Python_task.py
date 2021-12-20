import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

def product_base_links():
    bed_base_link = 'https://www.moebelfreude.de/'
    url = "https://www.moebelfreude.de/boxspringbetten"
    response = requests.get(url)
    page_content=response.text
    doc=BeautifulSoup(page_content, 'html.parser')

    product_tags=doc.find_all('a', class_="image-link")

    substr = 'bett/'
    product_links = []
    for i in range(len(product_tags)):
        product_suffix = str(product_tags[i].get('href'))
        if substr in product_suffix:
            link = bed_base_link+product_suffix
            product_links.append(link)
    product_links = list(set(product_links))
    
    return product_links

def get_link_blocks(doc):
    available_chs = doc.find_all('span', class_="label label-variation")
    list_chs = [a.text for a in available_chs]
    
    substring = 'cm'
    size_list = [chs for chs in list_chs if substring in chs]
    
    ch_list = [sh for sh in list_chs if sh not in size_list]
    ch_list = [ch.replace("/","-").lower() for ch in ch_list]
    
    #separate color and hardness -->  obtained using replace, split and strip methods
    substr = [' h2',' h3',' h2-h3']
    new_ch = []
    for ch in ch_list:
        for s in substr:
            if s in ch:
                new_ch.append(ch.replace(s,('/'+s.strip())).strip().split('/'))
    #new size list with '-' and proper format is obtained
    new_size = []
    for s in size_list:
        link=('-'+s.replace('x','-x-').replace('cm','-cm-')).strip()
        new_size.append(link)
    
    return new_ch, new_size


def get_item_urls(base_url,new_ch,new_size):
    return_dict={'LINK':[],'SIZE':[],'HARDNESS':[],'COLOR':[]}

    for ch in new_ch:
        for s in new_size:
            link = str(base_url+'-'+ch[0]+s+ch[1]).replace(' ','-').replace('--','-')
            return_dict['LINK'].append(link)
            return_dict['SIZE'].append(s)
            return_dict['HARDNESS'].append(ch[1])
            return_dict['COLOR'].append(ch[0])

    return_df = pd.DataFrame.from_dict(return_dict)
    return return_df

def get_Title(doc):
    name_class = "h1"
    name_tags = doc.find_all('div', class_=name_class)
    title = name_tags[0].text
    
    return str(title)

def get_Price(doc):
    price_class = 'price'
    price_tags = doc.find_all('span', class_=price_class)
    price = price_tags[0].text.strip()
    
    return str(price)

def main():
    product_links = product_base_links()
    result_dictionary={'LINK':[],'TITLE':[],'SIZE':[],'HARDNESS':[],'COLOR':[],'PRICE':[],'AVAILABILITY':[]}

    for url in tqdm(product_links):

        response = requests.get(url)
        page_content=response.text
        doc=BeautifulSoup(page_content, 'html.parser')
        base_url = url
        
        title=get_Title(doc)
        ch_list, size_list = get_link_blocks(doc)
        
        final_urls = get_item_urls(base_url,ch_list, size_list)

        for i in range(len(final_urls)):
            url = final_urls['LINK'].iloc[i]
            response = requests.get(url)
            response_code = response.status_code

            if response_code in range(200,300):
                page_content=response.text
                doc=BeautifulSoup(page_content, 'html.parser')
                result_dictionary['LINK'].append(url)
                result_dictionary['TITLE'].append(title)
                result_dictionary['SIZE'].append(str(final_urls['SIZE'].iloc[i]).replace('-',''))
                result_dictionary['HARDNESS'].append(str(final_urls['HARDNESS'].iloc[i]).upper())
                result_dictionary['COLOR'].append(final_urls['COLOR'].iloc[i])
                result_dictionary['PRICE'].append(get_Price(doc))
                result_dictionary['AVAILABILITY'].append('Y')
            else:
                page_content=response.text
                doc=BeautifulSoup(page_content, 'html.parser')
                result_dictionary['LINK'].append(url)
                result_dictionary['TITLE'].append(title)
                result_dictionary['SIZE'].append(str(final_urls['SIZE'].iloc[i]).replace('-',''))
                result_dictionary['HARDNESS'].append(str(final_urls['HARDNESS'].iloc[i]).upper())
                result_dictionary['COLOR'].append(final_urls['COLOR'].iloc[i])
                result_dictionary['PRICE'].append('NA')
                result_dictionary['AVAILABILITY'].append('N')
    
    df = pd.DataFrame.from_dict(result_dictionary)
    df=df.drop_duplicates(subset=['LINK'])
    df.to_csv('Python_web_scraping_results.csv',index=False)
    
    print('CSV File Generated Successfully!')   
    
main()