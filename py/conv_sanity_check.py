#!/opt/enr/virtupy/bin/python

import sys
import datetime

convs = {}

def main():
    f = open(sys.argv[1])
    for l in f:
        fields = l.split("\t")
        camp = fields[21]
        if camp not in convs:
            convs[camp] = {}
        cookie_str = fields[23]
        conv_time = fields[3]
        conv_time = conv_time.split("T")[0]

        if cookie_str == '-':
            continue
        cookies = cookie_str.split('; ')
        for c in cookies:
            if c.endswith("=="):
                # print "Skipping %s" % c
                continue
            try:
                (cn,cv) = c.split("=")
            except:
                print "Error on: %s" % c
                continue
            if cn == "odsp":
                # This is our cookie, skip
                continue
            elif cn == "AWSELB":
                # This is AWS ELB cookie, skip
                continue
            elif cn.startswith("sc"):
                # Ask @GG about this but ignore for now 
                continue
            elif cn.startswith("_man_crt") or cn.startswith("odsp2"):
                # We were young and needed the money.
                # I still do.
                continue
            elif cn.startswith("_sm_au"):
                # Nobody knows
                continue
            else:
                if cn.startswith("its") or cn.startswith("cts"):
                    # Impression (or click) was given by this targeting strategy
                    # tsId = cn[3:]
                    # ts = int(cv)/1000
                    if camp not in convs:
                        convs[camp] = {}
                    cur_camp_dict = convs[camp]
                    cv_time = conv_time
                    if cv_time not in cur_camp_dict:
                        # Screw the attribution to the TS in this script
                        cur_camp_dict[cv_time] = 1
                    else:
                        cur_camp_dict[cv_time] += 1
    for conv_camp in convs:
        sys.stdout.write("%s" % conv_camp)
        for dt in convs[conv_camp]:
            print "\t%s\t%s" % (dt, convs[conv_camp][dt])
            


if __name__ == "__main__":
    main()
    


    
