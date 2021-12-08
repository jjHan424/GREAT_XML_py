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
        hournew = "{0:02}".format(int(hour) - 1)
        seslennew = str(int(seslen)+3600)

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
        obsdir = "/dat01/leitingting/hjj_data/"+year+"/leo/grace-fo/leoobs/"
        poddir = "/dat01/leitingting/hjj_data/"+year+"/leo/grace-fo/leosp3/"
        attdir = "/dat01/leitingting/hjj_data/"+year+"/leo/grace-fo/leoatt/"
        grmdir = "/dat01/leitingting/hjj_data/"+year+"/prod/SP3/"
        clkdir = "/dat01/leitingting/hjj_data/"+year+"/prod/CLK/"
        dcbdir = "/dat01/leitingting/hjj_data/"+year+"/prod/DCB/"
        brddir = "/dat01/leitingting/hjj_data/"+year+"/prod/NAV/"


        attfile1 = attdir+"att_"+yy+doy+"_"+leo
        attfile2 = attdir+"att_"+yy+doy1+"_"+leo
        attfile3 = attdir+"att_"+yy+doy2+"_"+leo
        att_panda2gnut(attfile1,leo,doy)
        att_panda2gnut(attfile2,leo,doy1)
        att_panda2gnut(attfile3,leo,doy2)
        
        drag = " DRAG_c:90 "
        customer = "EMP_Sc1:90 EMP_Cc1:90 EMP_Sa1:90 EMP_Ca1:90"
        atmos = "DTM94"
        workdir = "./"
        list_sat = "  G01 G02 G03 G05 G06 G07 G08 G09 G10 G11 G12 G13 G14 G15 G16 G17 G18 G19 G20 G21 G22 G23 G24 G25 G26 G27 G28 G29 G30 G31 G32"
        icsfile = "ics_"+"{0:03}".format(int(year))+"{0:03}".format(int(doy))+"_gps"
        list_sat2 = list_sat
        if os.path.exists(icsfile):
                list_sat2 = get_sat(icsfile,list_sat2)
                print(list_sat2)
        else:
                print('no icsgps')

        if(len(list_sat2)>0):
                list_sat=list_sat2
        print(list_sat)
        update_preedit_xml("./gnut-preedit.xml",year,doy,hour,minute,second,seslen,list_sat,brddir)
        update_turbedit_xml("./gnut-tb.xml",year,doy,hour,minute,second,seslen,site_list_leo,obsdir,brddir)
        update_sp3orb_xml("./gnut-sp3orb.xml",year,doy,hour,minute,second,seslen,site_list_long,drag,customer,atmos)
        update_sp3orb2_xml("./gnut-sp3orb2.xml",year,doy,hour,minute,second,seslen,site_list_long,site_list_leo,drag,customer,atmos,poddir)
        update_sp3orbnav_xml("./gnut-sp3orbnav.xml",year,doy,hournew,minute,second,seslennew,list_sat,grmdir)
        update_leo_geometric("./gnut-ppp.xml",site_list_leo,site_list_long,year,doy,hour,minute,second,seslen,attdir,obsdir,grmdir,dcbdir,list_sat,clkdir)
        update_leo_geometric("./gnut-ppp2.xml",site_list_leo,site_list_long,year,doy,hour,minute,second,seslen,attdir,obsdir,grmdir,dcbdir,list_sat,clkdir)
        update_oileo_xml("./gnut-oi_leo.xml",year,doy,hour,minute,second,seslen,site_list_long,drag,customer,atmos,attdir)
        update_leoorbxml("./gnut-orblsqleo.xml",site_list_leo,site_list_long,year,doy,hour,minute,second,seslen,list_sat,obsdir,clkdir,attdir,dcbdir)
        update_leoorbxml("./gnut-orblsqleo_ambcon.xml",site_list_leo,site_list_long,year,doy,hour,minute,second,seslen,list_sat,obsdir,clkdir,attdir,dcbdir)
        update_orbdif_xml("./gnut-orbfitD.xml",year,doy1,"0","0","0","86400",site_list_long,site_list_leo,poddir)
        update_orbdifK_xml("./gnut-orbfitK.xml",year,doy1,"0","0","0","86400",site_list_long,site_list_leo,poddir)
        update_editresxml("./gnut-editres1.xml",leoshort,year,doy,hour,minute,second,seslen,"120","100","100")
        update_editresxml("./gnut-editres2.xml",leoshort,year,doy,hour,minute,second,seslen,"120","80","80")      
        update_ambfixml("./gnut-ambfix.xml",site_list_leo,year,doy,hour,minute,second,seslen,list_sat,obsdir,dcbdir)
        update_ambchk("./gnut-ambchk.xml",site_list_leo,year,doy,hour,minute,second,seslen,list_sat)

   
if __name__ == "__main__":

        main_iter()
