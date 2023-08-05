import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext

# Configure Selenium to use Firefox in headless mode
options = Options()
options.add_argument('-headless')
options.binary_location = "C:/Program Files (x86)/Mozilla Firefox/firefox.exe"  # Path to Firefox binary
driver = webdriver.Firefox(options=options)

# Create the GUI window
window = tk.Tk()
window.title("Scraping Output")

# Create a scrolled text widget
output_text = scrolledtext.ScrolledText(window, width=80, height=20)
output_text.pack()

# Open the text file for writing
output_file = open("football.txt", "w")

# Function to update the output text widget and write to the text file
def update_output_text(text):
    output_text.insert(tk.END, text)
    output_text.see(tk.END)
    window.update()
    output_file.write(text)
    output_file.flush()  # Flush the output to ensure it's written immediately

# Update the output text to indicate that scraping is in progress
update_output_text("Scraping in progress...\n")

# Load the webpage
driver.get("https://oddspedia.com/football/")

# Wait for the page to load
time.sleep(5)

# Click the second filter button
filter_buttons = driver.find_elements(By.CLASS_NAME, "btn-filter")
if len(filter_buttons) >= 2:
    filter_buttons[1].click()
    time.sleep(2)

    # Function to click "ml-show-more-btn" buttons
    def click_show_more_buttons():
        show_more_buttons = driver.find_elements(By.CLASS_NAME, "ml-show-more-btn")
        while show_more_buttons:
            for button in show_more_buttons:
                try:
                    button.click()
                    time.sleep(2)
                except Exception as e:
                    print(f"Error clicking button: {e}")
            show_more_buttons = driver.find_elements(By.CLASS_NAME, "ml-show-more-btn")

    # Click "ml-show-more-btn" buttons until there are no more
    click_show_more_buttons()

    # Get the updated page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all "div" elements with the class "match"
    match_divs = soup.find_all("div", class_="match")
    total_matches = 0

    # Create a set to store scraped links and avoid duplication
    scraped_links = set()

    # Scrape the links under each match div
    for match_div in match_divs:
        # Find all link elements under the match div
        links = match_div.find_all("a")

        # Scrape and process each link
        href_count = 0
        for link in links:
            href = link.get("href")
            if href:
                # Add the base URL to the front of the link
                full_url = "https://oddspedia.com" + href

                # Skip if the link has already been scraped
                if full_url in scraped_links:
                    continue

                # Add the link to the set of scraped links
                scraped_links.add(full_url)

                # Open the link in the same browser instance
                driver.get(full_url)
                time.sleep(2)
                more_buttons = driver.find_elements(By.CLASS_NAME, "h2h-results-pagination")
                for button in more_buttons:
                    button.click()
                    time.sleep(2)

                # Get the page source of the opened link
                page_source = driver.page_source

                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(page_source, "html.parser")

                # Find the section with the id "stats"
                stats_section = soup.find("section", id="stats")
                date_section = soup.find("section", id="event-header")

                try:
                    dates = date_section.find("span", class_="event-start-date").get_text(strip=True)
                except AttributeError:
                    continue

                if stats_section:
                    h2h_results_primary = stats_section.find("div", class_="h2h-results-primary")
                    hora = soup.find_all("li", class_="h2h-graph__score")

                    # Process the stats section as needed
                    if h2h_results_primary:
                        h2h_results_primary_items = h2h_results_primary.find_all("a")

                        for item in h2h_results_primary_items:
                            data = item.get("title")
                            if data:
                                update_output_text(f"Teams: {data}\n")
                                score = item.find("div", class_="h2h-results-primary__score-desktop").get_text(strip=True)
                                if score:
                                    href_count += 1
                                    update_output_text(f"Score: {score}\n")

                        total_matches += href_count
                        update_output_text(f"Total Matches: {href_count}\n")

                        if dates:
                            update_output_text(f"Date: {dates}\n")

                        if hora:
                            wins = []
                            for result in hora:
                                f_hora = result.get_text(strip=True)
                                wins.append(f_hora)

                            formatted_output = ' - '.join(wins)
                            update_output_text(f"Result: {formatted_output}\n")

                        update_output_text("\n")

                else:
                    update_output_text(f"No stats section found for link: {full_url}\n")
                    continue

    update_output_text(f"Total Matches Scraped: {total_matches}\n")
else:
    update_output_text("Error: Filter buttons not found.\n")

# Close the browser
driver.quit()

# Close the text file
output_file.close()

# Start the GUI event loop
window.mainloop()
