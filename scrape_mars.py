# Dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import requests
import pymongo
import time

def init_browser():
    executable_path = {'executable_path': '/Users/lucyly/Downloads/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

# Scraping Mars news, images, weather, and facts... 
def scrape ():

    #-----------------------------------------
    # News 
    #-----------------------------------------
    # Empty dictionary to plug everything into at the very end
    mars = {}

    # Splinter
    executable_path = {'executable_path': '/Users/lucyly/Downloads/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    # URL of page to be scraped
    news_url = 'https://mars.nasa.gov/news/'

    browser.visit(news_url)
    html = browser.html

    # Create BeautifulSoup object
    news_soup = bs(html, "html.parser")

    # Retrieve news titles and paragraph texts

    time.sleep(2)
    news_title = news_soup.select('.content_title')[0].text
    news_p = news_soup.select('.article_teaser_body')[0].text
        
    # Run if title and paragraph are available
    if (news_title and news_p):
        print(news_title)
        print(news_p)

    browser.quit()

    # Add news title and paragraph to dictionary
    mars['news_title'] = news_title
    mars['news_paragraph'] = news_p

    #-----------------------------------------
    # JPL Images
    #-----------------------------------------

    # URL to be scraped
    images_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # Use splinter to navigate the site and find the image url for the current 
    # Featured Mars Image and assign the url string to a variable called featured_image_url
    executable_path = {'executable_path': '/Users/lucyly/Downloads/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    browser.visit(images_url)
    browser.find_by_css('ul.articles')

    image_soup = bs(browser.html, 'html.parser')
    image_src = image_soup.select('a.fancybox')[0]['data-fancybox-href']
    featured_image_url = 'https://www.jpl.nasa.gov/' + image_src
    browser.quit()

    # Add featured image to dictionary
    mars['featured_image'] = featured_image_url

    #-----------------------------------------
    # Weather
    #-----------------------------------------

    # URL of page to be scraped
    weather_url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    weather_response = requests.get(weather_url)
    # Create BeautifulSoup object
    weather_soup = bs(weather_response.text)

    # Retrieve weather tweet texts
    mars_weather_tweet = weather_soup.select('div.js-tweet-text-container')

    # Print tweets and add to MongoDB
    for tweet in mars_weather_tweet: 
        if tweet.text.strip().startswith('InSight'):
            mars_weather = tweet.text.strip()

    # Add weather to dictionary
    mars['mars_weather'] = mars_weather

    #-----------------------------------------
    # Facts
    #-----------------------------------------
    # URL to be scraped 
    facts_url = 'https://space-facts.com/mars/'

    #  use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    mars_df = pd.read_html(facts_url)
    mars_df = mars_df[0]
    mars_df.columns = ['Description', 'Value']
    mars_df.set_index('Description', inplace=True)

    # Use Pandas to convert the data to a HTML table string.
    mars_html = mars_df.to_html()
    mars_html = mars_html.replace('\n', ' ')
    
    # Add table to dictionary
    mars['mars_facts'] = mars_html

    #-----------------------------------------
    # Hemispheres
    #-----------------------------------------
    # Splinter
    executable_path = {'executable_path': '/Users/lucyly/Downloads/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    # URL to be scraped: 
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(hemi_url)
    html = browser.html

    # Save both the image url string for the full resolution hemisphere image, 
    # and the Hemisphere title containing the hemisphere name
    hemisphere_image_urls = []

    for i in range (4):
        time.sleep(3)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        soup = bs(html, 'html.parser')
        time.sleep(3)
        partial = soup.find("img", class_="wide-image")["src"]
        img_title = soup.find("h2",class_="title").text
        img_url = 'https://astrogeology.usgs.gov'+ partial
        hemi_dict={"title":img_title,"img_url":img_url}
        hemisphere_image_urls.append(hemi_dict)
        browser.back()

    # Append the dictionary with the image url string and the hemisphere title to a list. 
    # This list will contain one dictionary for each hemisphere.
    hemisphere_image_urls.append({'Title': img_title, 'img_url': img_url})

    browser.quit()

    # Add hemispheres to dictionary
    mars['mars_hemis'] = hemisphere_image_urls

    #-----------------------------------------
    # Dictionary of all data scraped to be returned
    #-----------------------------------------
    # mars = {
    #     'News Title': news_title,
    #     'News Teaser': news_p,
    #     'Featured Image': featured_image_url,
    #     'Mars Weather': mars_weather,
    #     'Mars Facts': mars_html,
    #     'Mars Hemispheres': hemisphere_image_urls
    # }
    return mars