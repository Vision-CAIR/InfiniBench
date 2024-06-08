from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import json


def get_fqa_questions(movie_id):
    # Load the webpage
    driver = webdriver.Chrome()
    url = f'https://www.imdb.com/title/{movie_id}/faq/'
    driver.get(url)

    # Find the button and click it
    button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "ipc-btn ipc-btn--single-padding ipc-btn--center-align-content ipc-btn--default-height ipc-btn--core-base ipc-btn--theme-base ipc-btn--on-error ipc-text-button ipc-see-more__button")]'))
    )

    # Find the body element and scroll down using Page Down key
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.PAGE_DOWN)
    # Wait for a moment to let the page scroll
    time.sleep(2)
    try:
        button.click()
        time.sleep(3)
    except:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
        button.click()
        time.sleep(3)
    # Wait for a moment to let the page load
    # Get the modified HTML after clicking the button
    html_content = driver.page_source
    # Close the WebDriver
    driver.quit()

    # Now you can proceed to scrape data from the modified HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # Scraping code here...
    summary_content = soup.find_all("ul", {"class":"ipc-metadata-list ipc-metadata-list--dividers-between sc-d1777989-0 FVBoi meta-data-list-full ipc-metadata-list--base"})
    print(len(summary_content))
    # select some specific content from this list by using beautifulsoup
    new_soup = BeautifulSoup(str(summary_content[1]), 'html.parser')
    questions= new_soup.find_all("span", {"class":"ipc-accordion__item__title"})
    answers = new_soup.find_all("div", {"class":"ipc-html-content-inner-div"})
    q=[]
    a=[]
    for i in range(len(questions)):
        q.append(questions[i].get_text())
        a.append(answers[i].get_text())
    return q,a

with open("movie_fqa.json", "r") as f:
    movie_ids = json.load(f)

results = {}
for movie_id in movie_ids:
    try:
        questions, answers = get_fqa_questions(movie_id)
        results[movie_id] = {"questions": questions, "answers": answers}
        print(f"Successfully got the questions and answers for {movie_id}")
    except:
        print(f"Failed to get the questions and answers for {movie_id}")
        continue

with open("fqa_questions_answers.json", "w") as f:
    json.dump(results, f, indent=4)
