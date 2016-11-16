# app.py

####= Chatitron Application File
##============================================================================##

## @source https://docs.python.org/2/library/os.html
import os
## @source https://docs.python.org/2/library/sys.html
import sys
## @source https://docs.python.org/2/library/json.html
import json

## @source https://pypi.python.org/pypi/requests/2.12.0
import requests

## @source https://pypi.python.org/pypi/Flask/0.11.1
from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET'])
## Handles connection verification
def verify():
    ## @source https://developers.facebook.com/docs/graph-api/webhooks
    ## Check the validity of the callback server
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        ## Check the validation token
        if not request.args.get('hub.verify_token') == os.environ['VERIFY_TOKEN']:
            ## Acknowledge that the validation failed, if it did
            return 'Failed validation.  Make sure the validation tokens match.', 403
        return request.args['hub.challenge'], 200

    ## Acknowledge that the request to the server succeeded, if it did
    return 'Holla!  Server is running!', 200


## @source https://developers.facebook.com/docs/messenger-platform/product-overview/setup#subscribe_app
## All callbacks for Messenger are POSTs sent to the same webhook
@app.route('/', methods=['POST'])
## Handles messages received
def webhook():

    data = request.get_json()
    ## Adds incoming messages to the log
    log(data)

    if data['object'] == 'page':

        for entry in data['entry']:
            for messaging_event in entry['messaging']:

                ## If a message is received...
                if messaging_event.get('message'):
                    ## ID of the sender
                    sender_id = messaging_event['sender']['id']

                    ## ID of the recipient (Chatinator Facebook page)
                    recipient_id = messaging_event['recipient']['id']

                    ## The message text
                    message_text = messaging_event['message']['text']

                    ## Default chatbot response
                    send_message(sender_id, 'Can you dig it?  I can!')

                ## Confirmation: Delivery
                if messaging_event.get('delivery'):
                    pass

                ## Confirmation: Optin
                if messaging_event.get('optin'):
                    pass

                ## Confirmation: Postback selected
                if messaging_event.get('postback'):
                    pass

    return 'Boo-Ya!  Callback server validity is all good!', 200


## Handles messages sent
def send_message(recipient_id, message_text):

    log("Message being sent to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    url = 'https://graph.facebook.com/v2.6/me/messages'

    params = {
        'access_token': os.environ['PAGE_ACCESS_TOKEN']
    }

    headers = {
        'Content-Type': 'application/json'
    }

    data = json.dumps({
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    })

    req = requests.post(url, params=params, headers=headers, data=data)

    if req.status_code != 200:
        log(req.status_code)
        log(req.text)


## Heroku STDOUT logging
def log(message):
    if type(message) is not str:
        message = str(message)
    print message
    ## Write everything in the buffer to the terminal
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
