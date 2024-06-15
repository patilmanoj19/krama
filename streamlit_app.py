import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
from io import StringIO
import time
from webdriver_manager.chrome import ChromeDriverManager

def fetch_data(selected_months, selected_years, crops):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://krama.karnataka.gov.in/reports/DateWiseReport.aspx")

    markets = ["AllMarkets"]
    data_frames = []

    for year in selected_years:
        for month in selected_months:
            for crop in crops:
                for market in markets:
                    month_dropdown = Select(driver.find_element(By.ID, "_ctl0_content5_ddlmonth"))
                    month_dropdown.select_by_visible_text(month)

                    year_dropdown = Select(driver.find_element(By.ID, "_ctl0_content5_ddlyear"))
                    year_dropdown.select_by_visible_text(year)

                    commodity_dropdown = Select(driver.find_element(By.ID, "_ctl0_content5_ddlcommodity"))
                    commodity_dropdown.select_by_visible_text(crop.strip())

                    market_dropdown = Select(driver.find_element(By.ID, "_ctl0_content5_ddlmarket"))
                    market_dropdown.select_by_visible_text(market)

                    view_button = driver.find_element(By.ID, "_ctl0_content5_viewreport")
                    view_button.click()

                    time.sleep(5)

                    table = driver.find_element(By.ID, "_ctl0_content5_gv")
                    table_html = table.get_attribute("outerHTML")

                    html_buffer = StringIO(table_html)
                    df = pd.read_html(html_buffer)[0]
                    df['Commodity'] = crop.strip()
                    data_frames.append(df)

                    driver.back()
                    time.sleep(2)

    driver.quit()
    final_dataframe = pd.concat(data_frames, ignore_index=True)
    return final_dataframe

def main():
    st.title("Commodity Prices Scraper")

    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
    years = [str(year) for year in range(2000, 2031)]

    selected_months = st.multiselect("Select Months", options=["All"] + months, default="All")
    selected_years = st.multiselect("Select Years", options=["All"] + years, default="All")
    crop_input = st.text_input("Enter Crop Names (separated by comma)", "GROUNDNUT, BENGALGRAM")

    if "All" in selected_months:
        selected_months = months
    if "All" in selected_years:
        selected_years = years

    crops = [crop.strip() for crop in crop_input.split(",")]

    if st.button("Fetch Data"):
        with st.spinner("Fetching data..."):
            data = fetch_data(selected_months, selected_years, crops)
        st.success("Data fetched successfully!")
        st.dataframe(data)

if __name__ == "__main__":
    main()
