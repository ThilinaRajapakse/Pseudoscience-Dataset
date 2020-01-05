from processors import selectors
from scrape import scrape_page
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
import json
import sys
from tqdm.auto import tqdm


checkpoint_steps = 100


def scrape_site(site):
    session = HTMLSession()
    with open(f'links/{site}_urls.txt', 'r') as f:
        urls = f.readlines()

    urls = {url[:-1] for url in urls}

    save_dir = f'data/{site}/'
    os.makedirs(save_dir, exist_ok=True)

    scraped = []
    if os.path.isfile(save_dir + 'scraped_urls.txt'):
        with open(save_dir + 'scraped_urls.txt', 'r') as f:
            scraped = f.readlines()

    if scraped:
        with open(save_dir + 'data.json', 'r') as f:
            data = json.load(f)
    else:
        data = {'title': [], 'text': [], 'site': []}

    scraped = {url[:-1] for url in scraped}

    to_scrape = urls - scraped

    if not to_scrape:
        print(f'{site} scraping completed.')
        return

    print(f'{site} scraping initiated!')
    for i, url in enumerate(tqdm(to_scrape)):
        try:
            title, text = scrape_page(url, selectors[site], session)
            data['title'].append(title)
            data['text'].append(text)
            data['site'].append(site)
            scraped.add(url)
        except Exception as e:
            print(e)
        if i % checkpoint_steps == 0 and i > 0:
            with open(save_dir + 'data.json', 'w') as f:
                json.dump(data, f)
            with open(save_dir + 'scraped_urls.txt', 'w') as f:
                f.writelines(scraped)
            print(f'{site}: {i} of {len(to_scrape)} done.')

    data_df = pd.DataFrame(data)
    data_df.to_csv(save_dir + 'data_all.tsv', sep='\t', index=False)
    print(f'{site} scraping completed.')

    # print(urls[:5])

    # print(scrape_page(urls[-10], selectors[site], session))
    # print(scrape_page(urls[10], selectors[site], session))
    # print(scrape_page(urls[0], selectors[site], session))


def patch_pyppeteer():
    import pyppeteer.connection
    original_method = pyppeteer.connection.websockets.client.connect

    def new_method(*args, **kwargs):
        kwargs['ping_interval'] = None
        kwargs['ping_timeout'] = None
        return original_method(*args, **kwargs)

    pyppeteer.connection.websockets.client.connect = new_method


patch_pyppeteer()

sites = ['thinkingmomsrevolution', 'snopes', 'pnas']


with ThreadPoolExecutor(3) as executor:
    results = executor.map(scrape_site, sites)
