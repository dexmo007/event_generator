#!/usr/bin/python3
import random
import sys
from datetime import datetime
from datetime import timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from faker import Faker

# config
PROBABILITY_RECIPIENT = 100  # 5
BULK_SIZE = 10000
DEBUG = True

fake = Faker()


def generate_kep():
    return fake.ean13()


def generate_iso():
    return '[)>0815' + fake.ean13()


ID_GENERATORS = [generate_kep, generate_iso]


def generate_id():
    return ID_GENERATORS[random.randrange(len(ID_GENERATORS))]()


def generate_ts():
    #ts = fake.date_time_this_year()
    ts = datetime.now() + timedelta(days=1)
    return datetime.strftime(ts, '%Y-%m-%d %H:%M:%S.%f')[:-3]


def generate_info():
    prefix_phrase = fake.words(random.randint(2, 5))
    suffix_phrase = fake.words(random.randint(2, 5))
    return " ".join(prefix_phrase + [generate_id()] + suffix_phrase)


def generate_event():
    event = {
        "shipment": generate_id(),
        "parcel": generate_id(),
        "info": generate_info(),
        "timestamp": generate_ts()
    }
    if fake.boolean(chance_of_getting_true=PROBABILITY_RECIPIENT):
        event['recipient'] = fake.name()
    return event


n = int(sys.argv[1])
index_name = sys.argv[2]

print(f'Generating {n} events to index "{index_name}"')


es = Elasticsearch(hosts=["localhost:9200"])


def bulk_insert(_actions):
    if DEBUG:
        for a in actions:
            print(a)
    else:
        bulk(es, _actions, index=index_name, raise_on_error=True)


actions = []

for i in range(n):
    actions.append({'_index': index_name, '_type': 'events',
                    '_source': generate_event()})
    if len(actions) >= BULK_SIZE:
        bulk_insert(actions)
        print(f'{i/n*100}%')
        actions = []

if actions:
    bulk_insert(actions)
print('100%')
