import scrapy
import logging
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

class GooglePlaySpider(scrapy.Spider):
    name = 'google_play_spider'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/games']

    def __init__(self, *args, **kwargs):
        super(GooglePlaySpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # def parse(self, response):
    #     self.logger.debug(f"Parsing the main page: {response.url}")

    #     try:
    #         self.driver.get(response.url)
    #         selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

    #         # Extract the top chart game links
    #         top_chart_games = selenium_response.css('div.aoJE7e.b0ZfVe a::attr(href)').getall()
    #         self.logger.debug(f"Found {len(top_chart_games)} games in the top chart")

    #         for game in top_chart_games:
    #             game_url = response.urljoin(game)
    #             self.logger.debug(f"Following game URL: {game_url}")
    #             yield {'game_url': game_url}
    #     except Exception as e:
    #         self.logger.error(f"Error occurred while parsing the main page: {e}")
    def parse(self, response):
        self.logger.debug(f"Parsing the main page: {response.url}")

        try:
            self.driver.get(response.url)
            # Wait for the top chart game elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.aoJE7e.b0ZfVe a'))
            )

            selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

            # Extract the top chart game links
            top_chart_games = selenium_response.css('div.aoJE7e.b0ZfVe a::attr(href)').getall()
            self.logger.debug(f"Found {len(top_chart_games)} games in the top chart")

            game_ids = []
            for game in top_chart_games:
                game_url = response.urljoin(game)
                game_id = game.split('=')[-1]  # Extract the game ID from the URL
                self.logger.debug(f"Found game ID: {game_id}")
                game_ids.append(game_id)
                yield {'game_url': game_url, 'game_id': game_id}

            # Ensure the data directory exists
            os.makedirs('data', exist_ok=True)
            # Save the game IDs to a JSON file
            with open('data/game_ids.json', 'w') as f:
                json.dump(game_ids, f)

        except Exception as e:
            self.logger.error(f"Error occurred while parsing the main page: {e}")

    # def parse_game(self, response):
    #     self.logger.debug(f"Parsing game page: {response.url}")

    #     try:
    #         self.driver.get(response.url)
    #         selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

    #         # Extract data from the game page
    #         game_data = {
    #             'title': selenium_response.css('h1 span::text').get(),
    #             'rating': selenium_response.css('div.jILTFe::text').get(),
    #             'reviews': selenium_response.css('span.EymY4b span::text').get(),
    #             'developer': selenium_response.css('a.hrTbp.R8zArc::text').get(),
    #             'installs': selenium_response.css('div.hAyfc:nth-child(3) span.htlgb::text').get(),
    #             'last_updated': selenium_response.css('div.hAyfc:nth-child(2) span.htlgb::text').get(),
    #             'size': selenium_response.css('div.hAyfc:nth-child(1) span.htlgb::text').get(),
    #         }
    #         self.logger.debug(f"Extracted game data: {game_data}")

    #         # Follow the link to the reviews page if available
    #         reviews_link = selenium_response.css('a[href*="reviews"]::attr(href)').get()
    #         if reviews_link:
    #             reviews_url = response.urljoin(reviews_link)
    #             self.logger.debug(f"Following reviews URL: {reviews_url}")
    #             yield scrapy.Request(reviews_url, callback=self.parse_reviews, meta={'game_data': game_data})
    #         else:
    #             yield game_data
    #     except Exception as e:
    #         self.logger.error(f"Error occurred while parsing the game page: {e}")

    # def parse_reviews(self, response):
    #     self.logger.debug(f"Parsing reviews page: {response.url}")

    #     game_data = response.meta['game_data']
    #     try:
    #         self.driver.get(response.url)
    #         selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

    #         # Extract reviews data
    #         reviews = []
    #         review_elements = selenium_response.css('div.d15Mdf.bAhLNe')
    #         for review in review_elements:
    #             reviews.append({
    #                 'user': review.css('span.X43Kjb::text').get(),
    #                 'rating': review.css('div.pf5lIe div::attr(aria-label)').get(),
    #                 'date': review.css('span.p2TkOb::text').get(),
    #                 'content': review.css('span[jsname="bN97Pc"]::text').get() or review.css('span[jsname="fbQN7e"]::text').get(),
    #             })

    #         game_data['reviews'] = reviews
    #         self.logger.debug(f"Extracted reviews: {reviews}")

    #         yield game_data
    #     except Exception as e:
    #         self.logger.error(f"Error occurred while parsing the reviews page: {e}")

    def closed(self, reason):
        self.logger.debug(f"Spider closed: {reason}")
        self.driver.quit()
