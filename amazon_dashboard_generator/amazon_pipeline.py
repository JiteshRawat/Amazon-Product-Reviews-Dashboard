from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
import argparse

# add your user agent 
HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

# Function to extract Product Title
def get_title(soup):
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})
        # Inner NavigatableString Object
        title_value = title.text
        # Title as a string value
        title_string = title_value.strip()
    except AttributeError:
        title_string = ""
    return title_string

# Function to extract Product Price
def get_price(soup):
    try:
        # price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()
        price = soup.find("span", attrs={"class":'a-price-whole'}).text
        price= int(price.replace(",", "").replace(".",""))
    except AttributeError:
        try:
            # If there is some deal price
            price = soup.find("span", attrs={'id':'priceblock_dealprice'}).string.strip()
            price= int(price.replace(",", "").replace(".",""))
        except:
            price = 0
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
        rating= float(rating.split(" ")[0])
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
            rating= float(rating.split(" ")[0])
        except Exception as e:
            rating= 0
    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
        review_count= int(review_count.split(" ")[0].replace(",", ""))
    except:
        review_count = 0

    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()
    except:
        available = "Not Available"	
    return available

# Function to extract Product Rating percentages
def get_percent_ratings(soup):
    rates= []
    try:
        rating = soup.find_all("td", attrs={'class' : 'a-text-right a-nowrap' })
        for i in rating:
            rates.append(i.text.strip())
            
        for i in range(0, len(rates)):
            rates[i]= int(rates[i].replace("%", ""))
    except:
        rates= [0,0,0,0,0]
    return rates

# Function to extract Product Rating percentages
def get_img_link(soup):
    try:
        image = soup.find("div", attrs={"id":'imgTagWrapperId'}).find('img', attrs= {'id' : 'landingImage'})['src']
    except:
        image= ""
    return image


def get_bestseller(soup):
    try:
        bestseller= soup.find("i", attrs={"class":'a-icon a-icon-addon p13n-best-seller-badge'}).text
        if bestseller:
            ret_value = True
    except:
        try:
            bestseller= soup.find("span", attrs={"class":'a-size-small aok-float-left ac-badge-rectangle'}).text
            if bestseller:
                ret_value = True
        except:
            ret_value= False
        
    return ret_value

def get_total_ratings_and_reviews(soup):
    try:
        link= soup.find("a", attrs={"class":'a-link-emphasis a-text-bold'})
        link=  link.get("href")

        new_link= "https://www.amazon.in/" + link

        new_webpage = requests.get(new_link, headers=HEADERS)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")
        result= new_soup.find("div", attrs={"class":'a-row a-spacing-base a-size-base'}).text.strip()

        # Use regular expression to find numbers with commas
        total_rating= result.split("total ratings,")[0].replace(",", "")
        total_reviews= result.split("total ratings,")[1].strip().split(" ")[0].replace(",", "")

        # get positive reviews
        result= new_soup.find("a", attrs={"data-reftag":'cm_cr_arp_d_viewpnt_lft'})
        link = result.get("href")
        link= "https://www.amazon.in/" + link

        new_webpage = requests.get(link, headers=HEADERS)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")
        result= new_soup.find("div", attrs={"class":'a-row a-spacing-base a-size-base'}).text.strip()
        
        # Use regular expression to find numbers with commas
        total_positive_rating= result.split("total ratings,")[0].replace(",", "")
        total_positive_reviews= result.split("total ratings,")[1].strip().split(" ")[0].replace(",", "")
       
        # get negative reviews
        result= new_soup.find("a", attrs={"data-reftag":'cm_cr_arp_d_viewpnt_rgt'})
        link = result.get("href")
        link= "https://www.amazon.in/" + link

        new_webpage = requests.get(link, headers=HEADERS)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")
        result= new_soup.find("div", attrs={"class":'a-row a-spacing-base a-size-base'}).text.strip()
        
        # Use regular expression to find numbers with commas
        total_critical_rating= result.split("total ratings,")[0].replace(",", "")
        total_critical_reviews= result.split("total ratings,")[1].strip().split(" ")[0].replace(",", "")
    except:
        total_rating= 0
        total_reviews= 0
        total_positive_reviews= 0
        total_positive_rating= 0
        total_critical_rating= 0
        total_critical_reviews= 0
    return total_rating, total_reviews, total_positive_rating, total_positive_reviews, total_critical_rating, total_critical_reviews


def get_links(keyword):
    # The webpage URL
    URL =f"https://www.amazon.in/s?k={keyword}"
    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)
    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "html.parser")
    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})
    # Store the links
    links_list = []
    # Loop for extracting links from Tag Objects
    for link in links:
            links_list.append(link.get('href'))
            
    return links_list

def get_reviews(d, links_list):
    # Loop for extracting product details from each link 
    for link in links_list:
        try:
            if "https" not in link:
                link= "https://www.amazon.in" + link
            new_webpage = requests.get(link, headers=HEADERS)
            new_soup = BeautifulSoup(new_webpage.content, "html.parser")
            ## Function calls to display all necessary product information
            d['title'].append(get_title(new_soup))
            d['price'].append(get_price(new_soup))
            d['rating'].append(get_rating(new_soup))
            d['reviews_count'].append(get_review_count(new_soup))
            d['availability'].append(get_availability(new_soup))
            d['is_best_seller'].append(get_bestseller(new_soup))
            d['product_link'].append(link)
            d['img_link'].append(get_img_link(new_soup))
            tra_and_tre= get_total_ratings_and_reviews(new_soup)
            d['total_ratings'].append(tra_and_tre[0])
            d['total_reviews'].append(tra_and_tre[1])
            d['total_positive_ratings'].append(tra_and_tre[2])
            d['total_positive_reviews'].append(tra_and_tre[3])
            d['total_critical_ratings'].append(tra_and_tre[4])
            d['total_critical_reviews'].append(tra_and_tre[5])
            text= get_percent_ratings(new_soup)
            d['5_star_percent'].append(text[0])
            d['4_star_percent'].append(text[1])
            d['3_star_percent'].append(text[2])
            d['2_star_percent'].append(text[3])
            d['1_star_percent'].append(text[4])
                
        except Exception as e:
            pass
    
    return d    


def search(keyword):
    st = time.time()
    # keyword = keyword

    links_list= get_links(keyword)
    if len(links_list) > 15:
        links_list= links_list[:15]

    data_dict = {"title":[], "price":[], "rating":[], "reviews_count":[], 
         "availability":[], 'is_best_seller' : [],  'product_link' :[] , 'img_link' : [],
         'total_ratings' : [], 'total_reviews': [], 'total_positive_ratings': [], 'total_positive_reviews': [],
          'total_critical_ratings' : [], 'total_critical_reviews': [],  '5_star_percent': [], '4_star_percent': [],
          '3_star_percent' : [], '2_star_percent' : [], '1_star_percent' : [] }
    
    data= get_reviews(data_dict, links_list)
    
    amazon_df = pd.DataFrame.from_dict(data)
    amazon_df['title'].replace('', np.nan, inplace=True)
    amazon_df = amazon_df.dropna(subset=['title'])
    amazon_df[["total_ratings", "total_reviews", 'total_positive_ratings', 'total_positive_reviews', 'total_critical_ratings', 'total_critical_reviews']] = \
    amazon_df[["total_ratings", "total_reviews", 'total_positive_ratings', 'total_positive_reviews', 'total_critical_ratings', 'total_critical_reviews']].apply(pd.to_numeric)
    amazon_df.to_csv("data/amazon_data.csv", header=True, index=False)
    top_values = amazon_df.nlargest(5, 'rating').reset_index(drop=True)
    top_values.to_csv("data/top_products_by_ratings.csv", index= False)
   
    
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
    
    # return amazon_df, top_values
    return "Data Extraction Successful"