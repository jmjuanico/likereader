import sys
import urllib, hashlib, httplib

GRAVATAR_DOMAIN = 'gravatar.com'
GRAVATAR_PATH = '/avatar/'

def main():
    email = 'joey.juanico@gmail.com' # sys.argv[1]
    hash = hashlib.md5(email).hexdigest()
    print email + ' = ' + hash

    query = urllib.urlencode({
        'gravatar_id': hash,
        's': 1, # Smallest size available
        'default': '/' # Causes a re-direct when the gravatar is missing
    })
    full_path = '%s?%s' % (GRAVATAR_PATH, query)
    print full_path

    # Create connection and test for 302 redirect
    conn = httplib.HTTPConnection(GRAVATAR_DOMAIN)
    conn.request('HEAD', full_path)
    response = conn.getresponse()
    print response.getheaders()
    print response.status

    if response.status == 302:
        print 'No gravatar :('
    else:
        print 'Gravatar found :)'

if __name__ == '__main__':
    main()


