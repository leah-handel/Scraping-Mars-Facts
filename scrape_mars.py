from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
from webdriver_manager.chrome import ChromeDriverManager
from urlpath import URL
import pandas as pd

def init_browser():

    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    
    #scraping NASA news
    
    browser = init_browser()
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    #NASA results

    news_title = soup.find("div", {"class": "image_and_description_container"}).find("div", {"class": "content_title"}).text
    news_p = soup.find("div", {"class": "image_and_description_container"}).find("div", {"class": "article_teaser_body"}).text

    #scraping jpl images

    url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    base = URL(browser.url).parent
    href = soup.find("a", {"class": "fancybox-thumbs"})["href"]

    #jpl results

    featured_image_url =f"{base}/{href}"

    #scraping mars facts

    url = "https://space-facts.com/mars/"
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    col1 = soup.find("table", {"id": "tablepress-p-mars"}).find_all("td", {"class":"column-1"})
    labels = []
    for cell in col1:
        labels.append(cell.text)

    col2 = soup.find("table", {"id": "tablepress-p-mars"}).find_all("td", {"class":"column-2"})
    facts = []
    for cell in col2:
        facts.append(cell.text)

    table_df = pd.DataFrame([*zip(labels,facts)])

    #facts results

    facts_table = table_df.to_html(index=False, header=False)

    #scraping hemispheres

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    all_links = soup.find_all("a", {"class", "itemLink"})

    #scrape got each link twice, making a list of unique links to loop through
    links = []
    for link in all_links:
        if link["href"] not in links:
            links.append(link["href"])

    base = URL(browser.url).parent.parent

    #list of dictionaries
    images = []

    for link in links:
        url = f"{base}{link}"
        browser.visit(url)

        time.sleep(1)

        html = browser.html
        soup = bs(html, "html.parser")
    
        #dictionary for each hemisphere
        info={}
    
        #getting title, popping "enhanced" at the end
        long_title = soup.find("h2", class_ = "title").text
        list_title = long_title.split(" ")
        list_title.pop(-1)
        title = " ".join(list_title)   #ty to https://stackoverflow.com/questions/12453580/how-to-concatenate-items-in-a-list-to-a-single-string
        info["title"] = title
    
        #getting image urls
        image = soup.find("img", class_ = "wide-image")["src"]
        info["img_url"] = f"{base}{image}"
    
        #append dictionary with title and url to list
        images.append(info)

    results = {"news":{"news_title":news_title, "news_paragraph":news_p},\
        "featured_image_url":featured_image_url,\
        "facts_table": facts_table,\
        "hemispheres": images}

    browser.quit()

    return results
