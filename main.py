from urllib.request import build_opener, HTTPCookieProcessor
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup

def get_page(link, master_df):
    # open page with all the homes on this street
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    response = opener.open(link, timeout=30)
    property_page = BeautifulSoup(response, "html.parser")
    all_homes = property_page.findAll("h4", {'class': 'card-title'})
    all_homes_links = find_links(all_homes)
    # open page with individual home information
    for home in all_homes_links:
        home_to_open = "https://blockshopper.com" + home
        page_driver = webdriver.Chrome(ChromeDriverManager().install())
        page_driver.get(home_to_open)
        page_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        home_response = opener.open(home_to_open, timeout=30)
        ind_property_page = BeautifulSoup(home_response, "html.parser")
        community_info = ind_property_page.findAll("p", {"class": "info-data"})
        master_df = create_property_row(ind_property_page, community_info, master_df)
        page_driver.close()
        page_driver.quit()
    try:
        print("trying to find next page")
        next_page = property_page.find_all("li",{"class":"page-item next_page"})[0].find("a")["href"]
        print("found link for next page")
        next_page_link = "https://blockshopper.com" + next_page
        print("about to recursively go to next page")
        driver.close()
        driver.quit()
        return get_page(next_page_link, master_df)
    except:
        print("reached the last page")
        return master_df

def find_links(items):
    link_list = []
    for item in items:
        link = item.findNext('a')['href']
        if link not in all_links:
            link_list.append(link)
    return link_list

def create_property_row(property_page, community_info, master_df):
    try:
        address = [property_page.findAll("h1")[0].text.strip()]
        owner = [community_info[0].text.strip()]
        purchase_price = [community_info[1].text.strip()]
        property_tax = [community_info[2].text.strip()]
        median_income = [community_info[3].text.strip()]
        white = [community_info[4].text.strip()]
        latin = [community_info[5].text.strip()]
        black = [community_info[6].text.strip()]
        native = [community_info[7].text.strip()]
        pacific_islander =[community_info[8].text.strip()]
        asian= [community_info[9].text.strip()]
        us_representatives = [community_info[10].text.strip()]
        state_senator =[community_info[11].text.strip()]
        state_rep = [community_info[12].text.strip()]
        neighbourhood = [property_page.findAll("a", {"class": "col-xs-6 col-sm-4 col-md-6 col-lg-6"})[0].text.strip()]
        lot_size = [property_page.find(text="Lot Size").findNext('p').contents[0].strip()]
        acre_tax = [property_page.find(text="Tax $/Acre").findNext('p').contents[0].strip()]
        home_size = [property_page.find(text="Home Size").findNext('p').contents[0].strip()]
        bedrooms = [property_page.find(text="Beds").findNext('p').contents[0].strip()]
        bathrooms = [property_page.find(text="Baths").findNext('p').contents[0].strip()]
        built_year = [property_page.find(text="Built").findNext('p').contents[0].strip()]
        address_details = property_page.find_all("h2")[0].text.split(',')

    except:
        print("not a correct property format")
        address = [""]
        owner = [""]
        purchase_price = [""]
        property_tax = [""]
        median_income = [""]
        white = [""]
        latin = [""]
        black = [""]
        native = [""]
        pacific_islander =[""]
        asian= [""]
        us_representatives = [""]
        state_senator =[""]
        state_rep = [""]
        neighbourhood = [""]
        lot_size = [""]
        acre_tax = [""]
        home_size = [""]
        bedrooms = [""]
        bathrooms = [""]
        built_year = [""]
        address_details = [""]

    try:
        county = [address_details[0]]
    except:
        print("no county")
        county =[""]
    try:
        city = [address_details[1]]
    except:
        print("no city")
        city =[""]
    try:
        postal = [address_details[2]]
    except:
        print("no postal")
        postal = [""]

    try:
        middle_school = [property_page.find(text="Middle School:").findNext('strong').text.strip()]
    except:
        print("missing middle school")
        middle_school = [""]

    try:
        high_school = [property_page.find(text="High School:").findNext('strong').text.strip()]
    except:
        print("missing high school")
        high_school = [""]

    try:
        elementary_school = [property_page.find(text="Elementary School:").findNext('strong').text.strip()]
    except:
        print("missing elementary school")
        elementary_school = [""]

    community_dict = {'address': address, 'owner': owner, 'purchase_price': purchase_price,
                 'property_tax': property_tax, 'median_income':median_income,
                 'white':white, 'latin':latin, 'black':black, 'native':native, 'pacific_islander':pacific_islander,
                 'asian':asian, 'us_house_of_rep':us_representatives, 'state_senator':state_senator,
                 'state_rep':state_rep, 'elementary_school':elementary_school, 'middle_school':middle_school,
                 'high_school':high_school, 'neighbourhood':neighbourhood,
                 'bedrooms':bedrooms, 'bathrooms':bathrooms, "built_year":built_year,
                     "county":county, 'city':city,
                     'postal':postal, 'lot_size': lot_size, 'tax_per_acre': acre_tax,
                      'home_size':home_size
                     }
    print(community_dict)
    property_df = pd.DataFrame(community_dict)
    master_df = master_df.append(property_df)
    return master_df

if __name__ == "__main__":

    sf_home_page = 'https://blockshopper.com/ca/san-francisco-county/cities/san-francisco?page=2'
    opener = build_opener(HTTPCookieProcessor())
    homepage_response = opener.open(sf_home_page, timeout=30)
    master_df = pd.DataFrame()
    home_page = BeautifulSoup(homepage_response, "html.parser")
    while home_page.find_all("li", {"class":"page-item next_page"})[0].find("a")["href"]:
        next_button = home_page.find_all("li", {"class":"page-item next_page"})[0].find("a")["href"]

        all_items = home_page.findAll("td", {'class': None})
        all_links = []
        for item in all_items:
            link = item.findNext('a')['href']
            if link not in all_links:
                all_links.append(link)

        for link in all_links[:]:
            to_open = "https://blockshopper.com" + link
            print("opening " + link)
            master_df = get_page(to_open, master_df)
            master_df.to_csv("scraped_property_sf_2nd_page.csv", mode='w', header=True)
            print("finished " + link)
            master_df.to_csv("scraped_property_sf_2nd_page.csv")

        next_page_url = "https://blockshopper.com" + next_button
        next_homepage_response = opener.open(next_page_url, timeout=30)
        home_page = BeautifulSoup(next_homepage_response, "html.parser")
