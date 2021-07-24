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
from flask_caching import Cache

from flask import Flask, request, abort, g

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
cache = Cache()
cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': '/tmp'})
# getting channel secret
#  This would be the preferred approach but it just doesn't work
#  CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
#  CHANNEL_TOKEN = os.getenv('LINE_CHANNEL_TOKEN')
def query(payload, url):
    global MODEL_API_TOKEN
    headers = {"Authorization": f"Bearer {MODEL_API_TOKEN}"}
    data = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=data)
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user = event.source.user_id
    g = cache.get("g")
    if g == None:
        g = {}
    if 'STATE' not in g:
        g["STATE"] = {}
    if 'Converse_state' not in g:
        g["Converse_state"] = {}
    if user not in g["STATE"]:
        g["STATE"][user] = 0
    message = event.message.text
    print(user, message, g["STATE"], g, flush=True)
    if message == "What can you do?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='I am willing to introduce my best friend Joshua You aka 游一心 to you. Besides, I can do some amazing tricks and you can check them in useful tools option.'))
    elif message == "Sentence Completion":
        g["STATE"][user] = 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please enter your input.'))
    elif message == "What skills does he have?":
        test_flex = json.load(open("./flex/pl.json", "r"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='As a student in computer science, Joshua You is good at lots of fields such as machine learning, data analysis, web development and so on.'))
        line_bot_api.push_message(user, TextSendMessage(text='I just list few programming languages that is often used by him below.'))
        ret_message = FlexSendMessage(alt_text='Programming Language', contents=test_flex)
        line_bot_api.push_message(user, ret_message)
        line_bot_api.push_message(user, TextSendMessage(text='There are many languages such as matlab, R, Shell Script that Joshua You can use.'))
    elif message == "Tell me more about python packages.":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Here I list some packages of python that Joshua You often use.'))
        test_flex = json.load(open("./flex/python.json", "r"))
        ret_message = FlexSendMessage(alt_text='Packages', contents=test_flex)
        line_bot_api.push_message(user, ret_message)
    elif message == "Tell me more about javascript frameworks.":
        test_flex = json.load(open("./flex/javascript.json", "r"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Here I list some frameworks of javascript that Joshua You often use.'))
        ret_message = FlexSendMessage(alt_text='Frameworks', contents=test_flex)
        line_bot_api.push_message(user, ret_message)
    elif message == "Who is he?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Joshua You and I are best friends ever and almost tell everything to each other. He is now a student in CSIE department of NTU. \nAlthough he start his life as a computer engineer since college, he work really hard to improve himself. Sometimes he stays at his computer all day long programming. He is good at algorithm, Unix/Linux-based system, Machine Learning and Web Design and usually show me about his works. I have to say that he is truly talented in such fields.'))
    elif message == "Tell me more about his education.":
        test_flex = json.load(open("./flex/education.json", "r"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Below is all I know about his education.'))
        ret_message = FlexSendMessage(alt_text='Education', contents=test_flex)
        line_bot_api.push_message(user, ret_message)
    elif message == "Show me his photos.": 
        line_bot_api.push_message(user, TextSendMessage(text="For his privacy, I cannot directly give you his photos. However, here is a link and I am sure all photos in it are what he would not complain about showing to others."))
        line_bot_api.push_message(user, TextSendMessage(text="https://drive.google.com/drive/folders/17LbboEPgmB33Qk2NI3vgmR8amg6OHLsw?usp=sharing"))
    elif message == "Does he take part in any projects?":
        test_flex = json.load(open("./flex/project.json", "r"))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Off course. Joshua You is a productive engineer.'))
        ret_message = FlexSendMessage(alt_text='Projects', contents=test_flex)
        line_bot_api.push_message(user, ret_message)
    elif message == "Tell me more about Joshua You.":
        ret_message = TextSendMessage(
                text='No problem! It is my pleasure to introduce my best friend. Which do you want to know?',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Who is he?", text="Who is he?")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Education", text="Tell me more about his education.")
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
    elif message == "Who are you?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I\'m Mr.Bong, a self-proclaimed comedian"))
    elif message == "I want to chat with your bot.":
        g["STATE"][user] = 2
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No problem. I have turned it on. Just start your conversion and say \"End Conversation\" when you want to end this conversation with the bot."))
    elif message == "What tools do you have?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="There are two tools developed by me and Joshua You using Machine Learning and web design techniques."))
        line_bot_api.push_message(user, TextSendMessage(text="1. Sentence Completion\nYou can input an uncomplete sentence and our bot will output a complete sentence after yours automatically."))
        line_bot_api.push_message(user, TextSendMessage(text="2. Chat Bot\nWe establish a chat bot online and you can try to chat with it. It will be funny!"))
        line_bot_api.push_message(user, TextSendMessage(
                text='Which one do you want to use?',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Sentence Completion", text="Sentence Completion")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Chat Bot", text="I want to chat with your bot.")
                        )
                    ])
        ))
    elif message == "Show me some useful tools.":
        ret_message = TextSendMessage(
                text='These tools are my exclusive treasure, which one you want to use.',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Introduction", text="What tools do you have?")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Sentence Completion", text="Sentence Completion")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Chat Bot", text="I want to chat with your bot.")
                        )
                    ])
        )
        line_bot_api.reply_message(event.reply_token, ret_message)
    else:
        if message == "End Conversation" and g["STATE"][user] == 2:
            g["STATE"][user] = 0
            del g["Converse_state"][user]
            line_bot_api.push_message(user, TextSendMessage(text="The conversation is ended and the bot is turned off."))
        elif g["STATE"][user] == 2:
            global DIALO_API_URL
            if user not in g["Converse_state"]:
                g["Converse_state"][user] = {"past_user_inputs": [], "generated_responses":[]}
            g["Converse_state"][user]["text"] = message
            data = query(g["Converse_state"][user], DIALO_API_URL) 
            line_bot_api.push_message(user, TextSendMessage(text=data["generated_text"]))
            '''
            g["Converse_state"][user]["past_user_inputs"].append(message)
            g["Converse_state"][user]["generated_responses"].append(data["generated_text"])
            g["Converse_state"][user]["past_user_inputs"] = g["Converse_state"][user]["past_user_inputs"][-2:]
            g["Converse_state"][user]["generated_responses"] = g["Converse_state"][user]["generated_responses"][-2:]
            '''
        elif g["STATE"][user] == 1:
            global MODEL_API_URL
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please wait for a second.'))
            data = query({"inputs": message}, MODEL_API_URL)
            print(data, flush=True)
            line_bot_api.push_message(user, TextSendMessage(text="Here is the result of sentence completion."))
            line_bot_api.push_message(user, TextSendMessage(text=data[0]["generated_text"].split("\n")[0]))
            g["STATE"][user] = 0
        else:
            ret_message = TextSendMessage(
                    text='Hello, How you doin\'?',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="Who are you?", text="Who are you?")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="Joshua You", text="Tell me more about Joshua You.")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="Useful Tools", text="Show me some useful tools.")
                            )
                        ])
            )
            line_bot_api.reply_message(event.reply_token, ret_message)
    cache.set("g", g)

