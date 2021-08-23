from flask import Flask, render_template
import requests
from markupsafe import escape
import time

app = Flask(__name__)

url = "https://{username}:{password}@{shop}.myshopify.com/admin/api/2021-07/"

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/customer-mail-tag', methods=['POST', 'GET'])
def customer_mail_tag():
    time.sleep(10)  # Wait 10 secs for the customer to be added to the list
    response = requests.get(url+"customers.json")
    customers = response.json()['customers']

    for customer in customers:
        customerId = customer['id']
        mailTag = customer['email'].split('@')[1].split('.')[0]
        if customer['tags'] != mailTag:
            requests.put(url+"customers/{}.json".format(customerId), json={"customer":{"id":customerId,"tags":mailTag}})
    
    tagAddedCustomers = requests.get(url+"customers.json")

    if tagAddedCustomers.status_code < 300:
        status = '<p>Success</p>'
    else:
        status = '<p>Fail!</p>'
    return '<h1>Shopify Customers PUT</h1>'+status+f"{escape(tagAddedCustomers.text)}"


@app.route('/order-tags', methods=['POST', 'GET'])
def order_tags():
    time.sleep(10)  # Wait 10 secs for the order to be added to the list
    orderResp = requests.get(url+"orders.json")
    orders = orderResp.json()['orders']

    for order in orders:
        orderId = order['id']
        orderHour = order['created_at'].split('T')[1].split(':')[0]
        orderHour = int(orderHour)
        if orderHour >= 0 and orderHour < 6:
            orderTag = "midnight"
        elif orderHour >= 6 and orderHour < 12:
            orderTag = "morning"
        elif orderHour >= 12 and orderHour < 18:
            orderTag = "noon"
        elif orderHour >= 18 and orderHour < 24:
            orderTag = "afternoon"
        
        orderMetafield = [{"key":"created_time_period","value":orderTag,"value_type":"string","namespace":"global"}]

        if order['tags'] != orderTag:
            requests.put(url+"orders/{}.json".format(orderId), json={"order":{"id":orderId,"tags":orderTag,"metafields":orderMetafield}})

    tagAddedOrders = requests.get(url+"orders.json")
    if tagAddedOrders.status_code < 300:
        status = '<p>Success</p>'
    else:
        status = '<p>Fail!</p>'
    return '<h1>Shopify Orders PUT</h1>'+status+f"{escape(tagAddedOrders.text)}"