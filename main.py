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

from flask import Flask, request, abort, g

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config['SESSION_TYPE'] = 'filesystem'
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


# state: 0(init), 1(diagnosis), 2(hospital), 3(covid-19), 4(knowledge), 5(knowledge_disease)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user = event.source.user_id
    print(g, flush=True)
    if 'STATE' not in g:
        g.STATE = {}
    if 'Converse_state' not in g:
        g.Converse_state = {}
    if user not in g.STATE:
        g.STATE[user] = 0
    message = event.message.text
    print(user, message, g.STATE, g, flush=True)
    if message == "What can you do?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='I am willing to introduce my best friend Joshua You aka 游一心 to you. Besides, I can do some amazing tricks and you can check them in useful tools option.'))
    elif message == "Sentence Completion":
        g.STATE[user] = 1
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
    elif message == "Tell me more about javascript frameworks.":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Here I list some frameworks of javascript that Joshua You often use.'))
    elif message == "Who is he?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Joshua You and I are best friends ever and almost tell everything to each other. He is now a student in CSIE department of NTU. Although he start his life as a computer engineer since college, he work really hard to improve himself. Sometimes he stays at his computer all day long programming. He is good at algorithm, Unix/Linux-based system, Machine Learning and Web Design and usually show me about his works. I have to say that he is truly talented in such fields.'))
    elif message == "Tell me about his education.":
        pass
    elif message == "Show me his photos.":
        pass 
    elif message == "Does he take part in any projects?":
        pass
    elif message == "Tell me more about Joshua You.":
        ret_message = TextSendMessage(
                text='No problem! It is my pleasure to introduce my best friend. Which do you want to know?',
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
    elif message == "Who are you?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I\'m Mr.Bong, a self-proclaimed comedian"))
    elif message == "I want to chat with your bot.":
        g.STATE[user] = 2
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No problem. I have turned it on. Just start your conversion and say \"End Conversation\" when you want to end this conversation with the bot."))
    elif message == "What tools do you have?":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I\'m Mr.Bong, a self-proclaimed comedian"))
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
        if message == "End Conversation" and g.STATE[user] == 2:
            g.STATE[user] = 0
            del g.Converse_state[user]
            return
        elif g.STATE[user] == 2:
            global DIALO_API_URL
            if user not in g.Converse_state:
                g.Converse_state[user] = {"past_user_inputs": [], "generated_responses":[]}
            g.Converse_state[user]["text"] = message
            data = query(g.Converse_state[user], DIALO_API_URL) 
            line_bot_api.push_message(user, TextSendMessage(text=data["generated_text"]))
            g.Converse_state[user]["past_user_inputs"].append(message)
            g.Converse_state[user]["generated_responses"].append(data["generated_text"])
            return
        elif g.STATE[user] == 1:
            global MODEL_API_URL
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Please wait for a second.'))
            data = query({"inputs": message}, MODEL_API_URL)
            print(data, flush=True)
            line_bot_api.push_message(user, TextSendMessage(text="Here is the result of sentence completion."))
            line_bot_api.push_message(user, TextSendMessage(text=data[0]["generated_text"].replace("\n", "")))
            g.STATE[user] = 0
            return
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

