import os
import pymongo
import datetime
from PVE_s_MS_translator import PVE_s_MS_tranlatorClient

from translation import translate, is_like_russian
from utils import replace_dotted_keys

INTRO_TEXT = 'Привет! Вы находитесь в приватном навыке "Ёрш-Полиглот". ' \
    'Скажите, какое слово вы хотите перевести и с какого на какой язык - например "дельфин на английский".' \
    'Чтобы выйти, скажите "Хватит".'

subscription_key = os.environ.get('subscription_key')

MyTranslator = PVE_s_MS_tranlatorClient(subscription_key)

# If you want to store logs, please connect a mongodb cluster.
# You can get a free one on https://cloud.mongodb.com.
MONGODB_URI = os.environ.get('MONGODB_URI')
db = None
logs_collection = None

log1={"start":  datetime.datetime.now()}

print(log1)

if MONGODB_URI is not None:
    # w=0 means fast non-blocking write
    client = pymongo.MongoClient(MONGODB_URI, w=0)
    db = client.get_default_database()
#    logs_collection = db.get_collection('logs')
    logs_collection = db.logs
    logs_collection.insert_one(log1)

def do_translate(form, translate_state):
    api_req = {
        'text': form['slots'].get('phrase', {}).get('value'),
        'lang_from': form['slots'].get('from', {}).get('value'),
        'lang_to': form['slots'].get('to', {}).get('value'),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    translate_state.update(api_req)
    if 'text' not in translate_state:
        return 'Не поняла, какой текст нужно перевести', translate_state
    if is_like_russian(translate_state['text']) and 'lang_to' not in translate_state:
        return 'На какой язык нужно перевести?', translate_state
    if not is_like_russian(translate_state['text']) and 'lang_from' not in translate_state:
        return 'С какого языка нужно перевести?', translate_state
        
    if 'text' in translate_state :
        cur_text        =   translate_state.get('text')
    else:
        cur_text        =   None

    if 'lang_to' in translate_state :
        cur_lang_to     =   translate_state.get('lang_to')
    else:
        cur_lang_to     =   None
    
    if 'lang_from' in translate_state :
        cur_lang_from   =   translate_state.get('lang_from')
    else:
        cur_lang_from   =   None

    tran_error, tran_result = MyTranslator.translate(cur_text, cur_lang_to, cur_lang_from)
    
    text = tran_error or tran_result

    return text, translate_state

def do_fact(form, translate_state):
    api_req = {
        'text': form['slots'].get('object', {}).get('value'),
        'connector': form['slots'].get('connector', {}).get('value'),
        'description': form['slots'].get('description', {}).get('value'),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    translate_state.update(api_req)
    if 'text' not in translate_state:
        return 'Не поняла, какой объект факта', translate_state
    
    fact_name           =   form['slots'].get('object', {}).get('value')
    fact_description    =   form['slots'].get('description', {}).get('value')
    fact_connector      =   form['slots'].get('connector', {}).get('value')

    text = f'Получен факт "{fact_name}" с описанием "{fact_description}"  (соединитель: "{fact_connector}").'

    return text, translate_state


def do_age(form, translate_state):
  
    fact_name           =   form['slots'].get('object', {}).get('value')
    age                 =   form['slots'].get('age', {}).get('value')
    metric_period       =   form['slots'].get('metric_period', {}).get('value')

    api_req = {
        'text': fact_name,
        'age': age,
        'metric_period': metric_period,
    }
    api_req = {k: v for k, v in api_req.items() if v}
    translate_state.update(api_req)
    if 'text' not in translate_state:
        return 'Не поняла, какой объект факта (возраст)', translate_state

    text = f'Получен факт "{fact_name}" с возрастом "{age}"  "{metric_period}".'

    return text, translate_state

def do_address(form, translate_state):
  
    fact_name           =   form['slots'].get('object', {}).get('value')
    fact_retainer       =   form['slots'].get('retainer', {}).get('value')
    fact_address        =   form['slots'].get('address', {}).get('value')

    api_req = {
        'text': fact_name,
        'retainer': fact_retainer,
        'address': fact_address
    }
    api_req = {k: v for k, v in api_req.items() if v}
    translate_state.update(api_req)
    if 'text' not in translate_state:
        return 'Не поняла, какой объект факта (с адресом)', translate_state

    text = f'Получен факт "{fact_name}" с адресом "{fact_address}"  (соединитель: "{fact_retainer}").'

    return text, translate_state

def handler(event, context):
    utterance = event.get('request', {}).get('original_utterance')

    if logs_collection is not None and utterance != 'ping':
        logs_collection.insert_one(event)

    translate_state = event.get('state', {}).get('session', {}).get('translate', {})
    last_phrase = event.get('state', {}).get('session', {}).get('last_phrase')
    intents = event.get('request', {}).get('nlu', {}).get('intents', {})
    command = event.get('request', {}).get('command')

    text = INTRO_TEXT
    end_session = 'false'

    translate_full  =   intents.get('translate_full')
    facts           =   intents.get('facts')
    ages            =   intents.get('ages')
    addresses       =   intents.get('addresses')

    if intents.get('exit'):
        text = 'Приятно было попереводить для вас! ' \
               'Чтобы вернуться в навык, скажите "Запусти навык Ёрш-Полиглот". До свидания!'
        end_session = 'true'
    elif intents.get('help'):
        text = INTRO_TEXT
    elif intents.get('repeat'):
        if last_phrase:
            text = last_phrase
        else:
            text = 'Ох, я забыл, что нужно повторить. Попросите меня лучше что-нибудь перевести.'
    elif translate_full:
        text, translate_state = do_translate(translate_full, translate_state)
    elif addresses:
        text, translate_state = do_address(addresses, translate_state)
    elif ages:
        text, translate_state = do_age(ages, translate_state)
    elif facts:
        text, translate_state = do_fact(facts, translate_state)
    elif command:
        text =  'Не понял вас. ' \
                'Напоминаю, что как минимум надо сказать какое слово и на какой язык надо перевести - например "дельфин на английский". ' \
                'Чтобы выйти из навыка "Ёрш-Полиглот", скажите "Хватит".'

    response = {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': end_session
        },
        'session_state': {'translate': translate_state, 'last_phrase': text}
    }

    if logs_collection is not None and utterance != 'ping':
        logs_collection.insert_one({
            'request': replace_dotted_keys(event),
            'response': response,
            'time': datetime.datetime.now(),
            'app_id': event['session'].get('application', {}).get('application_id'),
            'utterance': utterance,
            'response_text': response['response']['text'],
        })

    return response