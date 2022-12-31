from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import threading
import twilio
import smtplib
import re

app = Flask(__name__)

def send_sms(to, body):
    # Account SID from twilio.com/console
    account_sid = "AC0cba614f7209c13e65ab2aec7477af10"
    # Your Auth Token from twilio.com/console
    auth_token  = "18f9cdd9d473756f3c75387ced38701f"

    client = twilio.Client(account_sid, auth_token)

    message = client.messages.create(
        to=to,
        from_="+15092848065",
        body=body)

    print(message.sid)
import requests

def get_stock_price(ticker):
    if not isinstance(ticker, str) or ticker.strip() == '':
        raise ValueError('Invalid ticker symbol')

        # Make request to Yahoo Finance website
    url = f'https://finance.yahoo.com/quote/{ticker}'
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        raise Exception('Error making request:', e)

    # Parse HTML response and extract stock price
    soup = BeautifulSoup(response.text, 'lxml')
    stock_price_el = soup.find('div', {'class': 'Fz(12px)'})
    if stock_price_el:
        # Extract stock price from element text
        stock_price_str = stock_price_el.text
        pattern = r'^\$([\d,]+\.\d+)'
        match = re.search(pattern, stock_price_str)
        if match:
            stock_price = float(match.group(1).replace(',', ''))
            return stock_price
        else:
            raise Exception('Stock price not found')
    else:
        raise Exception('Stock price not found')


def check_stock_price(ticker, threshold, frequency, notification_type):
    # Retrieve the current stock price
    stock_price = get_stock_price(ticker)


    if stock_price >= threshold:
        send_notification(ticker, stock_price, frequency, notification_type)
    return stock_price
    print(stock_price)
def send_notification(ticker, stock_price, frequency, notification_type):
    if notification_type == 'email':
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Set up the email server and create the email message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("giririri041@gmail.com", "dntjgxybmxzqfslj")
        msg = MIMEMultipart()
        msg['From'] = "insight.ws56@gmail.com"
        msg['To'] = "barshap116@gmail.com"
        msg['Subject'] = "Stock Price Alert"
        body = f'The price of {ticker} has reached or exceeded ${stock_price}.'
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail("your_email_address@gmail.com", "recipient_email_address@gmail.com", msg.as_string())
        server.quit()
        # Send an email notification

    elif notification_type == 'sms':
        # Send an SMS notification
        send_sms('+9779840147368', f'The price of {ticker} has reached or exceeded ${stock_price}.')
    else:
        # Handle other notification types
        pass

    # timer to check the stock price again at the specified frequency
    if frequency == 'hourly':
        timer = 3600  # Check every hour
    elif frequency == 'daily':
        timer = 86400  # Check every day
    elif frequency == 'weekly':
        timer = 604800  # Check every week
    else:
        # Handle other frequencies
        timer = 0

    # timer to call the check_stock_price function again after the specified interval
    threading.Timer(timer, check_stock_price, [ticker, threshold, frequency, notification_type]).start()
    return True


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        try:
            threshold = float(request.form['threshold'])
        except ValueError:
            threshold = 0
        frequency = request.form['frequency']
        notification_type = request.form['notification_type']
        # Check the stock price and send a notification if necessary
        check_stock_price(ticker, threshold, frequency, notification_type)
    return render_template('stock_notification.html')

if __name__ == '__main__':
    app.run()
