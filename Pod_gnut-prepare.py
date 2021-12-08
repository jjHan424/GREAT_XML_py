#!/user/bin/python3
#-*- coding:utf-8 -*-

import os
import shutil
import ftplib
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
from sys import argv
from generate_xmlfile import *

cddis = "cddis.gsfc.nasa.gov"


oi_std = r"..\oi.log"


def get_sat(ics_filename,begin=0,end=0):
        

        txt=[]
        list_sat=""
        count = 0
        counttime = 0
        with open(ics_filename,"r") as ics_f:
                for temp_line in ics_f:                      
                        counttime =counttime +1
                        if(counttime == 5):
                                time_beg = temp_line
                        if(temp_line[:1] == "G"):
                                count = count + 1
                                list_sat = list_sat+temp_line[:3]+" "
                        txt.append(temp_line)
       
        return list_sat

def main_iter():

        #get days
        year = argv[1]
        doy = "{0:03}".format(int(argv[2]))  
        day1 = int(doy) + 1
        day2 = int(doy) + 2
        doy1 = "{0:03}".format(day1)
        doy2 = "{0:03}".format(day2)
        hour = "{0:02}".format(int(argv[3]))
        minute = "{0:02}".format(int(argv[4]))
        second = "{0:02}".format(int(argv[5]))
        seslen =  argv[6]  
        leo = argv[7] 
        yy = year[2:]      
        leo_upp = leo.upper()

        #os.chdir("C:\\Users\\qinyujie\\work\\脚本")
       
        
        if(leo == "swarm-a"):
                leoshort = "swaa"
        elif(leo == "swarm-b"):
                leoshort = "swab"
        elif(leo =="swarm-c"):
                leoshort = "swac"
        elif(leo == "jason-2"):
                leoshort = "jas2"
        elif(leo == "jason-3"):
                leoshort ="jas3"
        elif(leo == "grace-c"):
                leoshort = "grac"
        elif(leo == "grace-d"):
                leoshort ="grad"
        elif(leo == "grace-a"):
                leoshort = "graa"
        elif(leo == "grace-b"):
                leoshort ="grab"
        elif(leo == "tandem-x"):
                leoshort = "tadx"

        site_list_leo=[leoshort]
        site_list_long=[leo]
        obsdir = ""
        poddir = "" 
        attdir = ""
        grmdir = ""
        brddir = "/dat01/leitingting/hjj_data/"+year+"/prod/NAV/"
        dcbdir = ""

        
        workdir = "./"
        list_sat = "  G01 G02 G03 G05 G06 G07 G08 G09 G10 G11 G12 G13 G14 G15 G16 G17 G18 G19 G20 G21 G22 G23 G24 G25 G26 G27 G28 G29 G30 G31 G32"
        icsfile = "ics_"+"{0:03}".format(int(year))+"{0:03}".format(int(doy))+"_gps"
        if os.path.exists(icsfile):
                list_sat = get_sat(icsfile,list_sat)
                print(list_sat)
        else:
                print('no icsgps')

        
        update_preedit_xml("./gnut-preedit.xml",year,doy,hour,minute,second,seslen,list_sat,brddir)
        
   
if __name__ == "__main__":

        main_iter()
