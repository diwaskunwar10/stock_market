import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from comfig import head, body 
import plotly.graph_objs as go
class StockScraper:
    def __init__(self):
        self.prev_market_price = None
        self.data_df = pd.DataFrame(columns=['Date', 'LTP', '% Change'])
        self.old_df_filter = self.scrape_old()

    def scrape_old(self):
        url = "url"

        response = requests.post(url, headers=head, data=body)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table table-bordered table-striped table-hover')
            headers = [th.text.strip() for th in table.find_all('th')]

            data_rows = soup.find_all('tr')[1:] 
            data = []
            for row in data_rows:
                row_data = [td.text.strip() for td in row.find_all('td')]
                data.append(row_data)

            old_df = pd.DataFrame(data, columns=headers)
            old_df.drop('#', axis=1, inplace=True)
            old_df['Date'] = pd.to_datetime(old_df['Date'])
            old_df['Date'] = old_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            old_df_filter = old_df[['Date', 'LTP', '% Change']]

            trace_candlestick = go.Candlestick(x=old_df['Date'],
                                   open=old_df['Open'].astype(float),
                                   high=old_df['High'].astype(float),
                                   low=old_df['Low'].astype(float),
                                   close=old_df['LTP'].astype(float),
                                   name='ADBL')

            trace_close = go.Scatter(x=old_df['Date'],
                                    y=old_df['LTP'].astype(float),
                                    mode='lines',
                                    name='Close')

            layout = go.Layout(title='Candlestick Chart for ADBL',
                            xaxis=dict(title='Date'),
                            yaxis=dict(title='Price'))

            fig = go.Figure(data=[trace_candlestick, trace_close], layout=layout)

            fig.show()



        

        else:
            print("Failed to retrieve the webpage")

        return old_df_filter


    def scrape_and_analyze(self):
        url = 'https://merolagani.com/CompanyDetail.aspx?symbol=ADBL'
        response = requests.get(url)

        final_df = self.old_df_filter  # Initialize final_df with old_df_filter before any updates

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            market_price = soup.find('span', id='ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice').text.strip()
            change = soup.find('span', id='ctl00_ContentPlaceHolder1_CompanyDetail1_lblChange').text
            change=change.replace("%","")
            change=change.strip()

            print("change",change.replace("%",""))

            if market_price != self.prev_market_price:
                self.prev_market_price = market_price
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                new_data = {'Date': timestamp, 'LTP': market_price, '% Change': change}

                new_row_df = pd.DataFrame([new_data], columns=self.old_df_filter.columns)
                
                final_df = pd.concat([self.old_df_filter, new_row_df], ignore_index=True)
                print(final_df)
                print("New market price detected. Updated DataFrame.")
            else:
                print("No change in market price.")
            time.sleep(5)

        else:
            print("Failed to retrieve data. Status code:", response.status_code)
        return final_df

if __name__ == "__main__":
    stock_scraper = StockScraper()
    while True:
        old_df_filter = stock_scraper.scrape_and_analyze()
        
