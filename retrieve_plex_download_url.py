#!/usr/bin/env python
'''
Retrieves the latests Plex Media Server PlexPass downlaod URL for Debian 64-bit.
'''
import json
import os
import re
import sys
import ssl
try:
    import mechanize
except ImportError:
    sys.stderr.write('You need to install the "Mechanize" Python package.\n')
    sys.exit(1)

__author__ = 'Werner Beroux <werner@beroux.com>'


class PutRequest(mechanize.Request):
    def get_method(self):
        return 'PUT'


def retrieve_latest_download_url(login, password):
    # Ignore SSL certificate errors (for some versions of SSL only).
    if hasattr(ssl, '_create_default_https_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    
    browser = mechanize.Browser()
    
    # Ignore robots by default
    browser.set_handle_robots(False)

    # Change language to English.
    browser.open(
        PutRequest('https://plex.tv/language',
        data=json.dumps({'locale': 'en'}),
        headers={'Content-Type': 'application/json'}))

    if login and password:
        sys.stderr.write('Retrieving the latest Plex release for PlexPass Premium users...\n')

        browser.open('https://plex.tv/users/sign_in')
        browser.select_form(nr=0)
        browser['user[login]'] = login
        browser['user[password]'] = password
        browser.submit()

        browser.open('https://plex.tv/downloads?channel=plexpass')
    else:
        sys.stderr.write('Retrieving latest public Plex release...\n')
        browser.open('https://plex.tv/downloads')

    links = [link for link in browser.links() if '.deb' in link.url and re.match(r'64[ -]?[Bb]its?', link.text)]
    assert len(links) == 1
    link = links[0]
    return link.absolute_url


if __name__ == '__main__':
    login = os.environ.get('PLEXPASS_LOGIN')
    password = os.environ.get('PLEXPASS_PASSWORD')
    if bool(login) != bool(password):
        sys.stderr.write('To get the latest release for Plex Pass users, you must provide "PLEXPASS_LOGIN" and "PLEXPASS_PASSWORD" environment variables.\n')
        sys.exit(1)
    print(retrieve_latest_download_url(login, password))
