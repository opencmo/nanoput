import sys
from devpay import ActivateHostedProduct
from common import parse_creds

def main():
    cred_file = sys.argv[1]
    d = parse_creds(cred_file)
    akey = d['akey']
    skey = d['skey']
    ptoken = d['ptoken']

    atoken = sys.argv[2]
    print 'Activating with %s' % atoken
    ahp = ActivateHostedProduct(ptoken, akey, skey)
    (utoken, pid) = ahp.activate(atoken)
    print 'User token: %s' % utoken
    print 'Persistent ID: %s' % pid
   
    
if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 3:
        print "Usage: %s <path-to-credential-ini> <activation-token>" % sys.argv[0]
        sys.exit(1)
    main()

