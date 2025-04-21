#!/usr/bin/env python3
import random
URL = {
        'Radio1':  'http://opml.radiotime.com/Tune.ashx?id=s25111&formats=aac,ogg,mp3&partnerId=16&serial=a44d9baf7190744ec4fa880f24a9fdba',
        'Krautrock': 'http://open.qobuz.com/playlist/1208967',
        'Dance': 'http://open.qobuz.com/playlist/2722317',
        'Electro': [
            'http://open.qobuz.com/playlist/5742963',
            'http://open.qobuz.com/playlist/2561228'
            ],
        'Dark 80': 'http://open.qobuz.com/playlist/2683409',
        'Ambient': 'http://open.qobuz.com/playlist/21001567',
        'Blues': [
            'https://open.qobuz.com/playlist/20093731',
            ["playlist","loadalbum","Blues","John Lee Hooker","*"]
            ],
        'Soul': [
            'http://open.qobuz.com/playlist/9396203',
            'http://open.qobuz.com/playlist/1327732',
            ["playlist","play","Soul"]
            ],
        'Jazz': [
            'http://open.qobuz.com/playlist/1020353',
            'https://open.qobuz.com/playlist/9698201',
            'https://open.qobuz.com/playlist/3484206',
            'https://open.qobuz.com/playlist/9163705',
            'https://open.qobuz.com/playlist/5692098',
            'https://open.qobuz.com/playlist/2561220',
            'http://open.qobuz.com/playlist/1621653',
            'http://open.qobuz.com/playlist/1621653',
            ["playlist","play","Jazz"]
            ],
        'Incomming': 'https://open.qobuz.com/playlist/21711341',
        'Audio Test': [
            'https://open.qobuz.com/playlist/12407647',
            'https://open.qobuz.com/playlist/12308506',
            'https://open.qobuz.com/playlist/9944942'
            ],
        'Hits': 'http://open.qobuz.com/playlist/6361506'
        }


class Saraswati:
    def __init__(self):
        self.urls = URL

    def test(self):
        print("Hello")

    def get_url(self, key):
        url = URL[key]
        if type(url) == list:
            url = random.choice(url)
        return url

if __name__ == '__main__':
    sara = Saraswati()
    url = sara.get_url('Blues')
    print(url)
