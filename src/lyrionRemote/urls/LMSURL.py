#!/usr/bin/env python3
import logging
import os
import random
import tomllib
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_URLS = {
    'Radio1': 'http://opml.radiotime.com/Tune.ashx?id=s25111&formats=aac,ogg,mp3&partnerId=16&serial=a44d9baf7190744ec4fa880f24a9fdba',
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
        ['playlist', 'loadalbum', 'Blues', 'John Lee Hooker', '*']
    ],
    'Soul': [
        'http://open.qobuz.com/playlist/9396203',
        'http://open.qobuz.com/playlist/1327732',
        ['playlist', 'play', 'Soul']
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
        ['playlist', 'play', 'Jazz']
    ],
    'Incomming': 'https://open.qobuz.com/playlist/21711341',
    'Audio Test': [
        'https://open.qobuz.com/playlist/12407647',
        'https://open.qobuz.com/playlist/12308506',
        'https://open.qobuz.com/playlist/9944942'
    ],
    'Hits': 'http://open.qobuz.com/playlist/6361506'
}


def _config_path():
    config_path = Path(os.getenv('LYRION_REMOTE_CONFIG', '/config/lyrion-remote/config.toml'))
    if not config_path.is_file():
        config_path = Path.home() / '.config' / 'lyrion-remote' / 'config.toml'
    return config_path


def _urls_config_path():
    env_path = os.getenv('LYRION_REMOTE_URLS_CONFIG')
    if env_path:
        path = Path(env_path)
        if path.is_file():
            return path
    config_path = _config_path()
    urls_path = config_path.parent / 'urls.conf'
    if urls_path.is_file():
        return urls_path
    return Path.home() / '.config' / 'lyrion-remote' / 'urls.conf'


def _append_entry(urls, name, value):
    if name not in urls:
        urls[name] = value
        return
    existing = urls[name]
    if isinstance(existing, list):
        existing.append(value)
    else:
        urls[name] = [existing, value]


def _load_urls():
    urls = DEFAULT_URLS.copy()
    config_path = _config_path()
    settings = {}

    if config_path.is_file():
        try:
            with open(config_path, mode='rb') as fp:
                settings = tomllib.load(fp)
        except Exception as exc:
            logger.warning('Failed to load LMS URL config at %s: %s', config_path, exc)
    else:
        logger.debug('No config.toml present at %s; continuing with defaults', config_path)

    extra_urls = settings.get('urls', {})
    if isinstance(extra_urls, dict):
        for name, value in extra_urls.items():
            _append_entry(urls, name, value)

    for entry in settings.get('url_entries', []):
        if not isinstance(entry, dict):
            continue
        name = entry.get('name')
        value = entry.get('value')
        if name and value is not None:
            _append_entry(urls, name, value)

    urls_path = _urls_config_path()
    if urls_path.is_file():
        try:
            with open(urls_path, mode='rb') as fp:
                urls_settings = tomllib.load(fp)
            extra_urls = urls_settings.get('urls', {})
            if isinstance(extra_urls, dict):
                for name, value in extra_urls.items():
                    _append_entry(urls, name, value)
            for entry in urls_settings.get('url_entries', []):
                if not isinstance(entry, dict):
                    continue
                name = entry.get('name')
                value = entry.get('value')
                if name and value is not None:
                    _append_entry(urls, name, value)
        except Exception as exc:
            logger.warning('Failed to load urls.conf at %s: %s', urls_path, exc)
    else:
        logger.debug('No urls.conf found at %s', urls_path)

    return urls




class CaseInsensitiveDict:
    """Lightweight mapping that provides case-insensitive lookups
    while preserving original key casing for iteration and display.
    """
    def __init__(self, mapping=None):
        self._data = {}
        self._index = {}
        if mapping:
            for k, v in mapping.items():
                self._data[k] = v
                self._index[k.lower()] = k

    def __contains__(self, key):
        if key is None:
            return False
        return key in self._data or key.lower() in self._index

    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        orig = self._index.get(key.lower())
        if orig is None:
            raise KeyError(key)
        return self._data[orig]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"CaseInsensitiveDict({self._data!r})"


URL = CaseInsensitiveDict(_load_urls())


class Saraswati:
    def __init__(self):
        self.urls = URL

    def test(self):
        print('Hello')

    def get_url(self, key):
        if key not in self.urls:
            raise KeyError(f'URL collection "{key}" not found')
        url = self.urls[key]
        if isinstance(url, list):
            url = random.choice(url)
        return url


if __name__ == '__main__':
    sara = Saraswati()
    url = sara.get_url('Blues')
    print(url)
