# -*- coding: utf-8 -*-
import os
from config import *
if os.getenv("DEV") is not None:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='./.env')

import sys
import json
import time
import requests

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# getting channel secret
#  This would be the preferred approach but it just doesn't work
#  CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
#  CHANNEL_TOKEN = os.getenv('LINE_CHANNEL_TOKEN')
def query(payload):
    global MODEL_API_URL
    global MODEL_API_TOKEN
    headers = {"Authorization": f"Bearer {MODEL_API_TOKEN}"}
    data = json.dumps(payload)
    response = requests.request("POST", MODEL_API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


if CHANNEL_SECRET is None:
    print("LINE_CHANNEL_SECRET may be undefined.")
    sys.exit(1)
if CHANNEL_TOKEN is None:
    print("LINE_CHANNEL_TOKEN may be undefined")
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


STATE = {}
DEPARTMENT = {}
# state: 0(init), 1(diagnosis), 2(hospital), 3(covid-19), 4(knowledge), 5(knowledge_disease)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user = event.source.user_id
    if user not in STATE:
        STATE[user] = 0
    message = event.message.text
    if STATE[user] == 1:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please wait for a second.'))
        data = query({"inputs": message})
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=data[0]["generated_text"]))
    elif message == "What can you do?":
        pass
    elif message == "gpt2test":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please enter your input.'))
        STATE[user] = 1
    elif message == "What skills does he have?":
        STATE[user] = 0
        test_flex = json.load(open("./flex/pl.json", "r"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='As a student in computer science, Joshua You is good at lots of fields such as machine learning, data analysis, web development and so on.'))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='I just show some programming language that is often used by him below.'))
        ret_message = FlexSendMessage(alt_text='Programming Language', contents=test_flex)
        line_bot_api.reply_message(event.reply_token, ret_message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='I just list few here and there are many languages such matlab, R, Shell Script that Joshua You can use.'))
    elif message == "Tell me more about python packages.":
        pass
    elif message == "Tell me more about javascript frameworks.":
        pass
    elif message == "Who is he?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Joshua You. He is my best friend'))
    elif message == "Tell me about his education.":
        pass
    elif message == "Show me his photos.":
        pass 
    elif message == "Does he take part in any projects?":
        pass
    else:
        STATE[user] = 0
        ret_message = TextSendMessage(
                text='Still want to know more about Joshua You? No problem! It is my pleasure to introduce my best friend and I am always here for you.',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Who is he?", text="Who is he?")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Education", text="Tell more about his education.")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Skills", text="What skills does he have?")
                        ),
                        QuickReplyButton(     
                            action=MessageAction(label="Photos", text="Show me his photos.")
                        ),
                        QuickReplyButton(     
                            action=MessageAction(label="Projects", text="Does he take part in any projects?")
                        )
                    ])
        )
        line_bot_api.reply_message(event.reply_token, ret_message)

