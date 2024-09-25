# Import necessary libraries
import requests  # Used for making HTTP requests
from bs4 import BeautifulSoup  # Used for parsing HTML content
from urllib.parse import urljoin  # Used to join base URL with relative URLs
import pandas as pd  # Used for creating and manipulating dataframes

# Define custom headers to mimic a web browser
custom_headers = {
    'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept-language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.amazon.com/'
}

# Set to keep track of visited URLs to avoid duplicates
visited_urls = set()


# Function to extract product information from a given URL
def get_product_info(url):
    # Make a request to the URL with custom headers
    response = requests.get(url, headers=custom_headers)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Error in getting webpage: {url}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Find the element containing the product title
    title_element = soup.select_one("#productTitle")
    title = title_element.text.strip() if title_element else None

    # Find the element containing the product price
    price_element = soup.select_one('span.a-offscreen')
    price = price_element.text if price_element else None

    # Find the element containing the product rating
    rating_element = soup.select_one("#acrPopover")
    rating_text = rating_element.attrs.get("title") if rating_element else None
    rating = rating_text.replace("out of 5 stars", "") if rating_text else None

    # Find the element containing the product image URL
    image_element = soup.select_one("#landingImage")
    image = image_element.attrs.get("src") if image_element else None

    # Find the element containing the product description
    description_element = soup.select_one("#productDescription")
    description = description_element.text.strip() if description_element else None

    # Return a dictionary containing the extracted product information
    return {
        "title": title,
        "price": price,
        "rating": rating,
        "image": image,
        "description": description,
        "url": url
    }


# Function to parse product listings from a given URL
def parse_listing(listing_url):
    global visited_urls  # Access the global variable keeping track of visited URLs

    # Make a request to the listing URL with custom headers
    response = requests.get(listing_url, headers=custom_headers)
    print(response.status_code)  # Print the response status code (for debugging)

    # Parse the HTML content using BeautifulSoup
    soup_search = BeautifulSoup(response.text, "lxml")

    # Find all links to product pages within the listing
    link_elements = soup_search.select("[data-asin] h2 a")
    page_data = []  # List to store extracted product information

    for link in link_elements:
        # Construct the full URL for the product page
        full_url = urljoin(listing_url, link.attrs.get("href"))

        # Check if the URL has already been visited
        if full_url not in visited_urls:
            visited_urls.add(full_url)  # Add the URL to the visited set
            print(f"Scraping product from {full_url[:100]}", flush=True)  # Print progress

            # Extract product information from the product page
            product_info = get_product_info(full_url)
            if product_info:  # Check if product info was successfully extracted
                page_data.append(product_info)  # Add product info to the list

          # Find the element for the next page link
    next_page_el = soup_search.select_one('a.s-pagination-next')

    # Check if there's a next page
    if next_page_el:
        # Get the URL for the next page
        next_page_url = next_page_el.attrs.get('href')
        next_page_url = urljoin(listing_url, next_page_url)
        print(f'Scraping next page: {next_page_url}', flush=True)


        # Recursively call parse_listing to scrape the next page
        page_data += parse_listing(next_page_url)

    # Return the collected product data
    return page_data


# Main function to start the scraping process
def main():
    data = []
    search_url = "https://www.amazon.com/s?k=bose&rh=n%3A12097479011&ref=nb_sb_noss"
    data = parse_listing(search_url)
    df = pd.DataFrame(data)
    df.to_csv("headphone.csv")



if __name__ == '__main__':
    main()
