from flask import Flask, request, Response, send_from_directory
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.messages.data_types.location import Location
from viberbot.api.messages import (
    TextMessage,
    ContactMessage,
    PictureMessage,
    VideoMessage,
    KeyboardMessage,
    LocationMessage
)
from viberbot.api.messages.data_types.contact import Contact
import json
import time
import logging
import sched
import threading

import logs_handler
from keyboards import *
import utilities
import texts
from user import User
import config
import viber_bot_functions

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def set_webhook(viber):
    viber.set_webhook(config.WEBHOOK)
    logger.info(f"Viber set webhook:{config.WEBHOOK}")

app = Flask(__name__)
viber = Api(BotConfiguration(
    name=config.BOT_NAME,
    avatar=config.AVATAR,
    auth_token=config.TOKEN
))




#@app.route('/buttons_images/<path:path>')
#def static_file(path):
#    #return app.send_static_file('buttons_images', path)
#    return send_from_directory('buttons_images', path)


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    viber_request_js = json.dumps(request.get_data().decode('utf8'))
    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    print("viber_request:", viber_request_js)
    if isinstance(viber_request, ViberMessageRequest):

        message = viber_request.message
        # chat_id = viber_request.chat_id
        user_id = viber_request.sender.id
        user_name = viber_request.sender.name
        # if isinstance(viber_request.message.contact, Contact):

        if isinstance(viber_request.message, ContactMessage):
            viber_bot_functions.contact_message(viber_request, user_id, viber)

        elif isinstance(viber_request.message, LocationMessage):
            viber_bot_functions.location_message(viber_request, user_id, viber, logger)

        elif isinstance(viber_request.message, TextMessage):
            viber_bot_functions.text_message(viber_request, user_id, viber, logger)

        else:
            # Skip handling photos
            # viber.send_messages(viber_request.sender.id, [
            #     TextMessage(text="Welcome to my bot again!", keyboard=MAIN_MENU_KEYBOARD, min_api_version=3)
            # ])
            pass

    elif isinstance(viber_request, ViberConversationStartedRequest) \
            or isinstance(viber_request, ViberSubscribedRequest):
        # or isinstance(viber_request, ViberUnsubscribedRequest):
        viber_bot_functions.viber_conversation_started_request(viber_request, viber)
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        logger.warning("Client unsubscribe from bot. {0}".format(viber_request))
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warning("Client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)





if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)
    app.run(host='0.0.0.0', port=8000, debug=True)



