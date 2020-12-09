"""
 Copyright (C) 2020 Dabble Lab - All Rights Reserved
 You may use, distribute and modify this code under the
 terms and conditions defined in file 'LICENSE.txt', which
 is part of this source code package.
 
 For additional copyright information please
 visit : http://dabblelab.com/copyright
 """

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import SkillBuilder

import logging
import json
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


#Handlers

class GetRemoteDatahandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return( is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("GetRemoteDataIntent")(handler_input))
    
    def handle(self,handler_input):
        speech_output = "This is the default message without API call."
        data = requests.get("http://api.open-notify.org/astros.json")
        data = json.loads(data.text)
        speech_output = "There are currently {} astronauts in space.".format(len(data["people"]))
        
        i= 0
        while(i<len(data["people"])):
            if(i==0):
                name = data["people"][i]['name']
                speech_output = "{} Their names are: {}, ".format(speech_output,name)
                i+=1
            elif(i==len(data["people"])-1):
                name = data["people"][i]['name']
                speech_output = "{} and {}.".format(speech_output,name)
                i+=1
            else:
                name = data["people"][i]['name']
                speech_output = "{} {},".format(speech_output,name)
                i+=1
        return (
            handler_input.response_builder
                .speak(speech_output)
                .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        speech_output = "This is the cancel message."
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        speech_output = "This is the help response."
        reprompt = "This is the help reprompt."
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

# This function handles utterances that can't be matched to any other intent handler.
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        
        speech_output = "This is the fallback response."
        reprompt = "This is the fallback reprompt."
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )


class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# This function handles syntax or routing errors. If you receive an error stating the request
# handler is not found, you have not implemented a handler for the intent or included
# it in the skill builder below
class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        speech_output = "Sorry, I couldn't do what you asked. Please try again."
        reprompt = "What would you like to do?"
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))


sb = SkillBuilder()
sb.add_request_handler(GetRemoteDatahandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
