from re import finditer
from time import time
from datetime import datetime, timedelta
from plumbum import local
from plumbum.cmd import cut, sort, uniq, mkdir, rm, s3cmd, gunzip
from requests import get


# https://baatoot.atlassian.net/browse/OPS-904#comment-18715
checks = {
    1: 1000,
    2: 1,
    3: 8000,
    4: 1,
    5: 50
}

tables = ('adx', 'dbm')

temp = '/tmp'
date = datetime.now() - timedelta(hours=1)
s3date = date.strftime('year=%Y/month=%m/day=%d/hour=%H')


def log(message):
    print '{}: {}'.format(str(datetime.now()), message)


def send_notification(message):
    params = {
        'token': 'xoxp-13148407399-15469243363-25501934804-70032ddf1a',
        'channel': '@vadim.moshinsky',
        'text': '{} Warning: {}'.format(':exclamation:', message),
        'username': 'Google Cookie Sync',
        'icon_emoji': ':cookie:'
    }
    request = get('https://slack.com/api/chat.postMessage', params)
    log('Notification sent. Status code: {}'.format(request.status_code))


def parse_table(name):
    log('Starting parsing for "{}" table.'.format(name))

    url = 's3://sva.s2-new.opendsp.com/user=man/table={}/{}/'.format(name, s3date)
    log('Using remote path: {}'.format(url))

    directory = '{}/{}'.format(temp, time())
    log('Using local path: {}'.format(directory))

    mkdir('-p', directory)
    log('Directory "{}" has been created.'.format(directory))

    log('Downloading logs.')
    print s3cmd('sync', url, directory)

    log('Unzipping logs.')
    print gunzip('-rv', directory)

    all_logs = local.path(directory) // 'man.{}.*.log'.format(name)
    log('Available logs:\n{}'.format('\n'.join(all_logs)))

    stdout = (cut['-f8', all_logs] | sort | uniq['-c'])()
    log('Status from log:\n{}'.format(stdout))

    errors = finditer(r'(?P<amount>\d+)\s+ERROR:\s+(?P<code>\d+)', stdout)

    log('Parsing lines.')
    for err in errors:
        code = int(err.group('code'))
        amount = int(err.group('amount'))

        allowed = checks[code]
        log('Code {} -> Amount {} | Allowed {}'.format(code, amount, allowed))

        if code in checks and amount > allowed:
            error = 'Date: {}. File: "man.{}.enr.log". Error Code {}: amount {} exceeded allowed {}.' \
                    ''.format(date.strftime('%Y/%m/%d'), name, code, amount, allowed)
            log(error)
            send_notification(error)
        else:
            log('Everything is ok.')

    log('Removing "{}" directory.'.format(directory))
    rm('-rf', directory)

    log('Done for "{}" table.'.format(name))

    print '\n'


print '=' * 60

for table in tables:
    parse_table(table)

print '=' * 60

print '\n\n'
