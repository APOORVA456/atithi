import logging

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from chatbot.middleware.firebaseHelper import firebaseHelper
from chatbot.middleware.remainderHelper import remainderHelper

from mindmeld.components import NaturalLanguageProcessor
from mindmeld.components.dialogue import Conversation
from mindmeld import configure_logs

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from twilio.rest import Client

import atexit
import time


class WhatsappBotServer:

    def __init__(self, name, app_path, nlp=None):
        """
        Args:
            name (str): The name of the server.
            app_path (str): The path of the MindMeld application.
            nlp (NaturalLanguageProcessor): MindMeld NLP component, will try to load from app path
              if None.
        """
        self.firebase = firebaseHelper()
        self.app = Flask(name)
        if not nlp:
            self.nlp = NaturalLanguageProcessor(app_path)
            self.nlp.load()
        else:
            self.nlp = nlp
        self.conv = Conversation(nlp=self.nlp, app_path=app_path)
        self.logger = logging.getLogger(__name__)

        @self.app.route("/", methods=["POST"])
        def handle_message():  # pylint: disable=unused-variable
            # print(request.values)
            # Getting number from which message came
            id = request.values.get('From', '')
            id = id.split('+')[1]
            # print(request.values) #uncomment this to dif deeper
            exist = self.firebase.existID(id)
            if not exist:
                result = self.firebase.createID(id)

            incoming_msg = request.values.get('Body', '').lower()
            print(incoming_msg)
            location = {
                'Latitude': request.values.get('Latitude', ''),
                'Longitude': request.values.get('Longitude', '')
            }
            if request.values.get('Latitude', '') and request.values.get('Longitude', ''):
                result = self.firebase.setCurrLocation(location, id)
                resp = MessagingResponse()
                msg = resp.message()
                params = dict(dynamic_resource=dict(id=id))
                incoming_msg = "lat long is set"
                response_text = self.conv.say(incoming_msg, params=params)[0]
                msg.body(response_text)
                return str(resp)
            else:
                resp = MessagingResponse()
                msg = resp.message()
                # Used to send dynamic id of the user making query
                params = dict(dynamic_resource=dict(id=id))
                try:
                    response_text = self.conv.say(incoming_msg, params=params)[0]
                    messages = response_text.split("~")
                    print(messages)
                    for msgs in messages:
                        sendMessage(msgs, id)
                    #msg.body(response_text)
                except IndexError:
                    msg.body("Didn't understand. sorry")
            return str(resp)

        def sendMessage(msg, number):
            print("Sending message..")
            TWILIO_AUTH_TOKEN = 'e0e696089a9a6a65774500c37edcb963'
            TWILIO_ACCOUNT_SID = 'AC589b234a1d386d213e4434b0f148f1f0'
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # Change the from whatsapp number with your twilio account number
            client.messages.create(body=msg, from_="whatsapp:+14155238886", to="whatsapp:+"+str(number))
            print("Sending to", number)

    def run(self, host="localhost", port=7150):
        self.app.run(host=host, port=port)

    def start_remainder(self):
        remainder_service = remainderHelper(self.firebase)
        remainder_service.start(self.firebase.getReminders())


if __name__ == '__main__':
    app = Flask(__name__)
    configure_logs()
    server = WhatsappBotServer(name='whatsapp', app_path='./chatbot')

    # create schedule for printing time
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=server.start_remainder,
        trigger=IntervalTrigger(seconds=1*60),
        id='send_remainders',
        name='send remainder every minute',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    port_number = 8080
    print('Running server on port {}...'.format(port_number))
    server.run(host='localhost', port=port_number)
