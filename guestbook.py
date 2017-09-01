#!/usr/bin/env python3
import requests
import config
import time
from flask import Flask, request
from escpos.printer import Usb
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)
product_id = config.product_id
vendor_id = config.vendor_id
ACCESS_TOKEN = config.ACCESS_TOKEN
max_len = config.max_len
size = config.size

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
    p = Usb(product_id, vendor_id) 
    p.image(filename, center=True)
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
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']
    if "text" in message:
        handle_text(message, sender)
    elif "attachments" in message:
        sticker_flag = "sticker_id" in message['attachments'][0]['payload']
        handle_image(message, sender, sticker_flag)
    return "ok"

def handle_text(data, sender):
    message = data['text']
    print(message)
    if message.count('\n') < max_len:
        print_text(message)
        reply(sender, "Zpráva úspěšně přijata.")
    else:
        reply(sender, "Zpráva byla moc dlouhá.")

def handle_image(data, sender, sticker=False):
    image_url = data['attachments'][0]['payload']['url']
    print(image_url)
    response = requests.get(image_url, stream=True)
    image = Image.open(BytesIO(response.content))
    image = image.convert('LA')
    image.thumbnail(size, Image.ANTIALIAS)
    im_filename = sender + "_image.png"
    image.save(im_filename, "png")
    print_image(im_filename)
    os.remove(im_filename)
    if sticker:
        reply(sender, "Sticker byl uspesne prijat")
    else:
        reply(sender, "Obrazek byl uspesne prijat")

if __name__ == '__main__':
    app.run(debug=False)
