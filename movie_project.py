from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import re
from itertools import zip_longest
import time

options = Options()
options.headless = True

print("open Browser....")
driver = webdriver.Firefox(options=options)

driver.get("https://www.imdb.com/chart/top/")

time.sleep(5)

html = driver.page_source

soup = BeautifulSoup(html, "lxml")

movies_titles = []
movies_years = []
movies_times = []
movies_Rs = []
movies_rates = []
links = []
genres = []
directors = []
stars = []
countries = []
budgets = []
grosses = []

main_ul = soup.find("ul", {'class': 'ipc-metadata-list ipc-metadata-list--dividers-between sc-a1e81754-0 dHaCOW compact-list-view ipc-metadata-list--base'})
print("Main Ul that Contain all Movie is Found") if main_ul else print("Not Found")
li_items = main_ul.find_all("li", {'class': 'ipc-metadata-list-summary-item sc-4929eaf6-0 DLYcv cli-parent'})

print(f"{len(li_items)} movies Found.")

for item in li_items:
    movie_title = item.find("h3", {'class': 'ipc-title__text'})
    movies_titles.append(re.sub(r'^\d+\.\s*', '', movie_title.text.strip()) if movie_title else "Unknown Title")

    movie_link = item.find("a", {'class': 'ipc-title-link-wrapper'})
    link_needed = "https://www.imdb.com" + movie_link['href'] if movie_link else "No Link"
    links.append(link_needed)

    main_div = item.find("div", {"class": "sc-732ea2d-5 kHnTQb cli-title-metadata"})
    spans = main_div.find_all("span", {'class': 'sc-732ea2d-6 gbTbSy cli-title-metadata-item'})
    
    if len(spans) >= 1:
        movies_years.append(spans[0].text.strip())
    else:
        movies_years.append("Unknown Year")
    
    if len(spans) >= 2:
        movies_times.append(spans[1].text.strip())
    else:
        movies_times.append("Unknown Time")
    
    if len(spans) >= 3:
        movies_Rs.append(spans[2].text.strip())
    else:
        movies_Rs.append("Unknown Rated R")

    movie_rate = item.find("span", {"class": "ipc-rating-star--rating"})
    movies_rates.append(movie_rate.text.strip() if movie_rate else "No Rate")

print("Main Page is Done, Let's dive into additional Pages to get more data....")

for link in links:
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(link)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    index = links.index(link) + 1
    print(f"we're in page Num {index}")
    genre = soup.find("div", {'class': 'ipc-chip-list__scroller'})
    genre_specific = genre.find_all("a", {"class": "ipc-chip ipc-chip--on-baseAlt"})
    genre_needed = ""
    for g in range(len(genre_specific)):
        if len(genre_specific) > 1:
            genre_needed = genre_needed + genre_specific[g].text.strip() + "|" + " "
        else:
            genre_needed = genre_needed + genre_specific[g].text.strip()
    genre_needed = genre_needed[:-3] if len(genre_specific) > 1 else genre_needed
    genres.append(genre_needed)
    print("genres Gotten.")
    main_div_new = soup.find("div", {'class': 'sc-70a366cc-2 bscNnP'})
    director_writer_star = main_div_new.find_all("ul", {'class': 'ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline ipc-metadata-list-item__list-content baseAlt'} )
    director = director_writer_star[0]
    director_specific = director.find_all("li", {"class": "ipc-inline-list__item"})
    print(len(director_specific))
    director_needed = ""
    for d in range(len(director_specific)):
        if len(director_specific) > 1:
            director_needed = director_needed + director_specific[d].text.strip() + "|" + " "
        else:
            director_needed = director_needed + director_specific[d].text.strip()
    director_needed = director_needed[:-3] if len(director_specific) > 1 else director_needed
    directors.append(director_needed)
    print("Directors Gotten.")
    star = director_writer_star[2]
    star_specific = star.find_all("li", {"class": "ipc-inline-list__item"})
    star_needed = ""
    for s in range(len(star_specific)):
        if len(star_specific) > 1:
            star_needed = star_needed + star_specific[s].text.strip() + "|" + " "
        else:
            star_needed = star_needed + star_specific[s].text.strip()
    star_needed = star_needed[:-3] if len(star_specific) > 1 else star_needed
    stars.append(star_needed)
    print("Stars Gotten.")
    country_origin = soup.find_all("a", {'class': 'ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link', 'href': '/search/title/?country_of_origin=US&ref_=tt_dt_cn'})
    country_needed = ""
    for c in range(len(country_origin)):
        if len(country_origin) > 1:
            country_needed = country_needed + country_origin[c].text.strip() + "|" + " "
        else:
            country_needed = country_needed + country_origin[c].text.strip()
    country_needed = country_needed[:-3] if len(country_origin) > 1 else country_needed
    countries.append(country_needed)
    print("Country Gotten.")
    li_needed = soup.find_all("li", {'class': 'ipc-metadata-list__item sc-1bec5ca1-2 eoigIp'})
    for li in range(len(li_needed)):
        budget_or_grossWorldWide = li_needed[li].find("span", {'class': 'ipc-metadata-list-item__label'}).text
        if budget_or_grossWorldWide == "Budget":
            budget = li_needed[li].find("span", {'class': 'ipc-metadata-list-item__list-content-item'})
            budgets.append(budget.text)
        elif budget_or_grossWorldWide == "Gross worldwide":
            gross_worldwide = li_needed[li].find("span", {'class': 'ipc-metadata-list-item__list-content-item'})
            grosses.append(gross_worldwide.text)
    if budget == False:
        budgets.append("Not Found Budget")
    if gross_worldwide == False:
        grosses.append("Gross Worldwide Not Found")

    print("Budgets & Gross Gotten.")

    print(f"Movie Number {index} is added")
    print("-*-*-*-" * 2)
    driver.close()
    if index == 3:
        break

driver.quit()

files_list = [movies_titles, movies_years, movies_times, movies_Rs, movies_rates, genres, directors, stars, countries, budgets, grosses]
exported = zip_longest(*files_list)

with open(r"F:\Projects\test files\movie_project_test.csv", "w", encoding="utf-8", newline="") as myfile:
    wr = csv.writer(myfile)
    wr.writerow(["Movie Title", "Year", "Time", "R Rated", "Rate", "Genres", "Directors", "Stars", "Country", "Budget", "Worldwide Gross"])
    wr.writerows(exported)

print("Process Done.")