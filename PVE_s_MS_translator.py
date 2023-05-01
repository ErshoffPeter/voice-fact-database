# -*- coding: utf-8 -*-

# This simple app uses the '/translate' resource to translate text from
# one language to another.

# This sample runs on Python 2.7.x and Python 3.x.
# You may need to install requests and uuid.
# Run: pip install requests uuid

import os, requests, uuid, json


class PVE_s_MS_tranlatorClient:
    def __init__(self, subscription_key_in, endpoint_in = 'https://api.cognitive.microsofttranslator.com'):
        # If you encounter any issues with the base_url or path, make sure
        # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
        self.subscription_key = subscription_key_in
        self.endpoint  = endpoint_in
        self.path = '/translate?api-version=3.0'

        self.headers = {
                        'Ocp-Apim-Subscription-Key': self.subscription_key,
                        'Ocp-Apim-Subscription-Region': 'canadacentral',
                        'Content-type': 'application/json',
                        'X-ClientTraceId': str(uuid.uuid4())
                        }
#        params = '&to=ru&to=en&to=it'
    def translate(self, params_in, body_in):
        params = ''
        for cur_param in params_in:
            for cur_key, cur_value in cur_param.items() :
                params = params + '&' + cur_key + '=' + cur_value
        constructed_url = self.endpoint + self.path + params

        print("logging(constructed_url)")
        print(constructed_url)

        print("self.headers")
        print(self.headers)

        #   constructed_url = "https://www.google.ru"

        self.request = requests.post(constructed_url, headers=self.headers, json=body_in)

        print("logging(self.request)")
        print(self.request)

        return self.request.json()


####################################################################################
#MyTranslator = PVE_s_MS_tranlatorClient(subscription_key)

#params = [
#            {'to' : "ru"},
#            {'to' : "en"},
#            {'to' : "it"}
#        ]

# You can pass more than one object in body.
#body = [
#            {'text' : "Рад стараться!"},
#            {'text' : "I'm sorry! "}
#        ]

#response = MyTranslator.translate(params, body)

#print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

#print((response[0])['translations'])

#for cur_response in response:
#    for cur_translate in cur_response['translations']:
#        print(cur_translate['to'] + ': ' + cur_translate['text'])
