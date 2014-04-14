import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import parse_creds

def main():
    cred_file = sys.argv[1]
    d = parse_creds(cred_file)
    conn = S3Connection(d['akey'], d['skey'])
    utoken = '{UserToken}AAkHVXNlclRrblauSqKup6ZY+akojCziRrowIZ2X+X+EVKPi7IMw6qBdleAn/FFPKwIPqVrmRGUAAufFZERPhMuNoIqJME2mrEMb/RrelRTFnVPoGZbtVSKwBLQZmTFiq5S1BlVonZk0TbiJO/SzAGvtm5+lesUy4ZxVF+dbNQCJlNqKWZU+f7fwOQrwbEH3dqpbFb3/xj1N+rUazBaN1VWE5h09HcD4FVmWcpQjX6ofvfafbBf++xVbezhsdod7B1VHocwyzeFdI73CSdgZTR31m1R7Fl9BxFB3kNurZanhin/YkpiC/ZbBrMBV2KQX+qvD2SGh1erCy6qZnfitPhq/1F24chnbP5IsYaHja+AVPcS688xB0YbWy93qQ15M2nGMI8vlpOLH5IPVpw4iMMlg2Ac3URkggNiCQGce4rlrObx5kx5A6Nw6'
    dpheaders = { 'x-amz-security-token': utoken }
    bucket = conn.get_bucket('support_adotube_com', headers=dpheaders)
    k = Key(bucket)
    k.key='year=2013/month=05/day=07/hour=10/ip-10-196-59-104.expo.txt'
    k.set_contents_from_filename('/opt/enr/log/ado.expo.enr.log', headers=dpheaders)
    
    
if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 2:
        print "Usage: %s <path-to-credential-ini>" % sys.argv[0]
        sys.exit(1)
    main()

