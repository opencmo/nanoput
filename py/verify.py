import sys
from devpay import VerifyProductSubscriptionByPid
from common import parse_creds

def main():
    cred_file = sys.argv[1]
    d = parse_creds(cred_file)
    akey = d['akey']
    skey = d['skey']
    pcode = d['pcode']

    pid = sys.argv[2]
    print 'Verifying with %s' % pid
    ver = VerifyProductSubscriptionByPid(pcode, akey, skey)
    result = ver.verify(pid)
    print 'Result: %s' % result
    
if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 3:
        print "Usage: %s <path-to-credential-ini> <persistent-id>" % sys.argv[0]
        sys.exit(1)
    main()

