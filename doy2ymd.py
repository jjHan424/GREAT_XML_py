#-*- coding-f:utf-8 -*-

import PodBatch_win 
import xml.etree.ElementTree as et
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday
from sys import argv
import sys

def main():
    year = argv[1]
    doy = argv[2]
    yyyy,mon,day = doy2ymd(int(year),int(doy))
    week = ymd2gpsweekday(int(year),mon,day)
    print(yyyy,mon,day)
    
    #generate_Sitelistleo("P",60)
    #update_combineorbxml("gnut-orblsq.xml",site_list,site_list_leo,year,doy)
    #update_oileo_xml("gnut-oi_leo.xml",year,doy)
    #update_oixml("gnut-oi_nav.xml",year,doy)

if __name__ == "__main__":
    main()
