# Google Image Scraper
A library created to scrape Google Images with Playwright.<br>

Largely inspired from [ohyicong/Google-Image-Scraper](https://github.com/ohyicong/Google-Image-Scraper) - which uses Selenium webdriver instead. <br>

Other image sources such as Bing, Shutterstock to be added soon!

## Pre-requisites:
1. Python 3.10 or above

## Setup
1. Clone this repository
2. Install python dependencies
    ```
    pip install -r requirements.txt
    ```
3. Install Playwright dependencies (installs playwright browsers)
    ```
    playwright install
    ```
4. Edit your desired parameters in main.py
    ```
    search_keys         = Strings that will be searched for
    number of images    = Desired number of images for each search_key
    headless            = Chrome GUI behaviour. If True, there will be no GUI
    min_resolution      = Minimum desired image resolution
    max_resolution      = Maximum desired image resolution
    max_missed          = Maximum number of failed image grabs before program terminates. Increase this number to ensure large queries do not exit.
    ```
4. Run the program
    ```
    python main.py
    ```
