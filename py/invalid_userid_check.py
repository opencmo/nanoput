from datetime import datetime, timedelta
from plumbum.cmd import grep, wc
from requests import get


def log(message):
    print '{}: {}'.format(str(datetime.now()), message)


def send_notification(message):
    params = {
        'token': 'xoxp-13148407399-15469243363-25501934804-70032ddf1a',
        'channel': '@vadim.moshinsky',
        'text': '{} Warning: {}'.format(':exclamation:', message),
        'username': 'UserID Guard',
        'icon_emoji': ':shield:'
    }
    request = get('https://slack.com/api/chat.postMessage', params)
    log('Notification sent. Status code: {}'.format(request.status_code))


def parse_log():
    date = datetime.now() - timedelta(days=1)
    date = date.strftime('%Y/%m/%d')
    folder = '/opt/enr/log'
    filename = 'error.log'
    pattern = '^{}.*client sent invalid userid cookie'.format(date)
    logfile = '{}/{}'.format(folder, filename)

    log('Starting grepping pattern "{}" in file "{}".'.format(pattern, logfile))

    stdout = (grep[pattern, logfile] | wc['-l'])()
    stdout = stdout.strip()

    log('Grep finished. Result: {}'.format(stdout))

    amount = int(stdout)
    allowed = 5000
    if amount > allowed:
        error = 'Date: {}. Invalid userid cookies amount {} exceeded allowed {}.' \
                ''.format(date, amount, allowed)
        log(error)
        send_notification(error)
    else:
        log('Everything is ok.')

    log('Done.')


print '=' * 60

parse_log()

print '=' * 60

print '\n\n'
