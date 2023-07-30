import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Part 1: Scraping Product Listings

def scrape_product_listing_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_data = []
    
    # Extract product details from the page
    # For example:
    product_listings = soup.find_all('div', class_='s-result-item')
    for product in product_listings:
        product_url = product.find('a', class_='a-link-normal')
        if product_url:
            product_url = product_url['href']
            if not product_url.startswith('http'):
                product_url = f'https://www.amazon.in{product_url}'
        else:
            product_url = None
        
        product_name = product.find('span', class_='a-size-medium')
        if product_name:
            product_name = product_name.text.strip()
        else:
            product_name = "N/A"
        
        product_price = product.find('span', class_='a-offscreen')
        if product_price:
            product_price = product_price.text.strip()
        else:
            product_price = "N/A"
        
        product_rating = product.find('span', class_='a-icon-alt')
        if product_rating:
            product_rating = product_rating.text.split()[0]
        else:
            product_rating = "N/A"
        
        product_num_reviews = product.find('span', {'aria-label': 'ratings'})
        if product_num_reviews:
            product_num_reviews = product_num_reviews.text.strip().split()[0]
        else:
            product_num_reviews = "N/A"
        
        product_data.append({
            'Product URL': product_url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': product_rating,
            'Number of Reviews': product_num_reviews
        })
    
    return product_data

# Iterate through 20 pages and scrape product listings
all_product_data = []
for page_num in range(1, 21):
    url = f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page_num}'
    product_data = scrape_product_listing_page(url)
    all_product_data.extend(product_data)
    time.sleep(2)  # Add a delay between requests to avoid overwhelming the server

# Part 2: Hitting Product URLs

def scrape_product_details(product_url):
    if product_url is None:
        return None
    
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract additional product details
    # For example:
    description = soup.find('meta', {'name': 'description'})
    if description:
        description = description['content']
    else:
        description = "N/A"
    
    asin = soup.find('input', {'id': 'ASIN'})
    if asin:
        asin = asin['value']
    else:
        asin = "N/A"
    
    product_description = soup.find('div', {'id': 'productDescription'})
    if product_description:
        product_description = product_description.text.strip()
    else:
        product_description = "N/A"
    
    manufacturer = soup.find('a', {'id': 'bylineInfo'})
    if manufacturer:
        manufacturer = manufacturer.text.strip()
    else:
        manufacturer = "N/A"
    
    product_details = {
        'Description': description,
        'ASIN': asin,
        'Product Description': product_description,
        'Manufacturer': manufacturer
    }
    
    return product_details

# Limit the number of product URLs to scrape (e.g., 200)
max_product_urls_to_scrape = 200
final_product_data = []

for product in all_product_data[:max_product_urls_to_scrape]:
    product_url = product['Product URL']
    product_details = scrape_product_details(product_url)
    if product_details is not None:
        product.update(product_details)
        final_product_data.append(product)
    time.sleep(2)  # Add a delay between requests to avoid overwhelming the server

# Export data to a CSV file
df = pd.DataFrame(final_product_data)
df.to_csv('amazon_products.csv', index=False)