import os, requests, uuid, json
from PVE_s_MS_translator import PVE_s_MS_tranlatorClient

def main(param_in, param_out):
    subscription_key    =   '8bb213038f2f46718f44e7265265c526'

    print("main has been started!")

    print(param_in)
    print(param_out)

    MyTranslator = PVE_s_MS_tranlatorClient(subscription_key)

    params = [
                {'to' : "ru"},
                {'to' : "en"},
                {'to' : "it"}
            ]

 #  You can pass more than one object in body.
    body = [
                {'text' : "Рад стараться!"},
                {'text' : "I'm sorry! "},
                {'text' : param_in}
            ]

    response = MyTranslator.translate(params, body)

    param_out = json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))

    print(param_out)

    print((response[0])['translations'])

    for cur_response in response:
        for cur_translate in cur_response['translations']:
            print(cur_translate['to'] + ': ' + cur_translate['text'])

    return param_out