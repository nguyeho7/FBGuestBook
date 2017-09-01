#!/usr/bin/env python3
import requests
import config
import time
from flask import Flask, request
from escpos.printer import Usb

app = Flask(__name__)
product_id = config.product_id
vendor_id = config.vendor_id
ACCESS_TOKEN = config.ACCESS_TOKEN
max_len = config.max_len


def print_text(text):
    '''
    Prints the given text and cuts it. Returns True on success
    '''
    p = Usb(product_id, vendor_id) 
    curtime = time.strftime("%H:%M, %d/%m/%Y")
    to_print = curtime + "\n" + text
    p.text(to_print)
    p.text("\n")
    p.cut()

def print_image(filename):
    # have to tune the image size
    p.image()
    p.cut()

def reply(user_id, msg):
    '''
    Sends the given reply to the user ID
    '''
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.8/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    resp_json = resp.json()
    if "error" in resp_json:
        print(resp.content)

@app.route('/', methods=['POST', "GET"])
def handle_incoming_messages():
    if request.method == 'GET':
        # authenticate
        return request.args['hub.challenge']
    data = request.json
    try:
        sender = data['entry'][0]['messaging'][0]['sender']['id']
        message = data['entry'][0]['messaging'][0]['message']['text']
    except KeyError:
        message = 'emoji'
    print(message)
    if text.count('\n') < max_len:
        print_text(message)
        reply(sender, "Zpráva úspěšně přijata.")
    else:
        reply(sender, "Zpráva byla moc dlouhá.")
    return "ok"


if __name__ == '__main__':
    app.run(debug=False)
