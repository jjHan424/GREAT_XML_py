'''
Author: Han Junjie
Date: 2021-12-08 13:39:09
LastEditTime: 2021-12-19 14:29:01
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /GREAT_xml_py/Iono_great-ipppre.py
'''
import os
import shutil
import ftplib
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
from sys import argv
from generate_xmlfile import *

from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday

cddis = "cddis.gsfc.nasa.gov"


oi_std = r"..\oi.log"

def change_gen(xml_file,year,doy,hour,s_length,site,sys):
    #change time
    change_gen_time(xml_file,year,doy,hour,s_length)
    tree = et.parse(xml_file)
    root = tree.getroot()
    gen = root.find("gen")
    #change sys
    gen_sys = gen.find("sys")
    sys_text = ""
    if ("G" in sys):
        sys_text = "GPS"
    if ("E" in sys):
        sys_text = sys_text + " GAL"
    if ("R" in sys):
        sys_text = sys_text + " GLO"
    if ("C" in sys):
        sys_text = sys_text + " BDS"
    sys_text = " " + sys_text + " "
    gen_sys.text = sys_text
    #change site
    gen_rec = gen.find("rec")
    gen_rec.text = "\n"
    i = 0
    for cur_site in site:
        gen_rec.text = gen_rec.text + " " + cur_site + " "
        i = i+1
        if (i%6==0):
            gen_rec.text = gen_rec.text + "\n"
    if (i%6 != 0):
        gen_rec.text = gen_rec.text + "\n   "
    tree.write(xml_file)

def change_gen_time(xml_file,year,doy,hour,s_length):
    tree = et.parse(xml_file)
    root = tree.getroot()
    gen = root.find("gen")
    #change time
    beg = gen.find("beg")
    end = gen.find("end")
    yyyy,mon,day = doy2ymd(year,doy)
    min = 0
    sec = 0
    beg.text = " {0:04}".format(int(yyyy)) + "-" + "{0:02}".format(int(mon)) + "-" + "{0:02}".format(int(day)) + " " + "{0:02}".format(int(hour)) + ":{0:02}".format(min) + ":{0:02} ".format(sec)
    hour_length = int(s_length / 3600)
    sec_length = s_length - hour_length * 3600
    while (hour_length >= 24):
        day = day + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        hour = hour - 24
        day = day + 1
    while (sec_length >= 3600):
        hour = hour + 1
        sec_length = sec_length - 3600
    while (sec_length >= 60):
        min = min + 1
        sec_length = sec_length - 60
    sec = sec + sec_length
    end.text = " {0:04}".format(int(yyyy)) + "-" + "{0:02}".format(int(mon)) + "-" + "{0:02}".format(int(day)) + " " + "{0:02}".format(int(hour)) + ":{0:02}".format(min) + ":{0:02} ".format(sec)
    tree.write(xml_file)


def change_inp_PPP(xml_file,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,year,doy,hour,s_length,upddir,area):
    tree = et.parse(xml_file)
    root = tree.getroot()
    inputs = root.find("inputs")
    day_length = s_length // 86400 + 1
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    site_list = site
    inp_obs = inputs.find("rinexo")
    inp_sp3 = inputs.find("sp3")
    inp_clk = inputs.find("rinexc")
    inp_eph = inputs.find("rinexn")
    cur_day = 0
    obs_text,sp3_text,clk_text,dcb_text,eph_text,upd_text = "","","","","",""
    yyyy = "{0:04}".format(year)
    while (cur_day < day_length):
        day = doy + cur_day
        #change obs
        obs_text = obs_text + "\n"
        i=0
        for cur_site in site_list:
            if area == "WuHan":
                obs_text = obs_text + "  " + obsdir  + "{0:03}/".format(day) + cur_site.upper() + "{0:03}".format(day) + "0." + yyyy[2:] + "o"
            if area == "HongKong":
                obs_text = obs_text + "  " + obsdir  + "{0:03}/".format(day) + "5S/" + cur_site.lower() + "{0:03}".format(day) + "0." + yyyy[2:] + "o"
            i = i+1
            if (i%6==0):
                obs_text = obs_text + "\n"
        if (i%6 != 0):
            obs_text = obs_text + "\n"
        #change nav
        eph_text = eph_text + "  " + ephdir + eph_name +  "{0:03}".format(day) + "0." + yyyy[2:] + "n"
        #change sp3
        y_temp,mon,day = doy2ymd(int(year),int(day))
        week = ymd2gpsweekday(int(year),mon,day)
        sp3_text = sp3_text + "  " + sp3dir + sp3_name + str(week) + ".sp3"
        #change clk
        clk_text = clk_text + "  " + clkdir + clk_name + str(week) + ".clk"
        
        cur_day = cur_day + 1
    
    inp_obs.text = obs_text + "   "
    inp_eph.text = eph_text + "  "
    inp_sp3.text = sp3_text + "  "
    inp_clk.text = clk_text + "  "
    
    tree.write(xml_file)

def change_inp_PL(xml_file,obsdir,site,ephdir,eph_name,year,doy,hour,s_length):
    tree = et.parse(xml_file)
    root = tree.getroot()
    inputs = root.find("inputs")
    day_length = s_length // 86400 + 1
    site_list = site.split(" ")
    hour_length = s_length / 3600
    day_length = 1
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    inp_obs = inputs.find("rinexo")
    inp_eph = inputs.find("rinexn")
    cur_day = 0
    obs_text,sp3_text,clk_text,dcb_text,eph_text = "","","","",""
    yyyy = "{0:04}".format(year)
    while (cur_day < day_length):
        day = doy + cur_day
        #change obs
        obs_text = obs_text + "\n"
        for cur_site in site_list:
            obs_text = obs_text + "        " + obsdir  + "{0:03}/".format(day) + cur_site.lower() + "{0:03}".format(day) + "0." + yyyy[2:] + "o"
        #change nav
        eph_text = eph_text + "  " + ephdir + eph_name +  "{0:03}".format(day) + "0." + yyyy[2:] + "n"
        cur_day = cur_day + 1
    
    inp_obs.text = obs_text + "\n        "
    inp_eph.text = eph_text + "  "
    tree.write(xml_file)

def change_out_PPP(xml_file,year,doy,hour,s_length,type):
    tree = et.parse(xml_file)
    root = tree.getroot()
    outputs = root.find("outputs")
    if (type == "PPP"):
        mode = "Float" 
    if (type == "PPPAR"):
        mode = "Fixed"
    if (type == "PPPSION"):
        mode = "SION"
    if (type == "PPPSIONAR"):
        mode = "SIONAR"

    #change flt
    out_temp = outputs.find("flt")
    out_temp.text = "  " + "flt/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".flt"

    #change enu
    out_temp = outputs.find("enu")
    out_temp.text = "  " + "enu/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".enu"

    #change recover
    out_temp = outputs.find("recover")
    out_temp.text = "  " + "res/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".res"

    #change ipp
    out_temp = outputs.find("ipp")
    out_temp.text = "  " + "IPP_PPP/$(rec)$(doy)_" + mode + ".$(yy)IPP"

    tree.write(xml_file)

def main_iter():
    #参数的传递
    year = argv[1]
    doy = int(argv[2])
    hour = int(argv[3])
    minute = 0
    sec = 0
    s_length = int(argv[4])
    sys_GNSS = argv[5]
    area = argv[6]
    xmlfile = argv[7]
    #路径的设置
    #CHN
    # site = "1012 1022 1140 3026 2KJ1 A010 C004 D002 D007 D017 D018 E033 F094 H035 H038 H053 H055 H068 H074 H139 I092 J003 K042 K057 K059 K070 K101 K110 M175 M192 N004 N062 N010 N032 N028 N047 N068 O038 P053 S028 T023 T044 U029 V092 W038 X046 Y065 CQKZ CZDZ FYFN NCAY NYNZ SXXA WHDS WHSP WHXK WHXZ WHYJ XGXN XXFH YYJK"
    #EPN
    site = "TRO1 VARS HETT OVE6 ROM2 OST6 OLK2 PYHA LEK6 METG LOV6 IRBE NOR7 SPT7 VAIN HAS6 RANT REDZ LAMA HELG GELL LDB2 GOML GOET BRTS LEIJ WARE INVR ARIS TLL1 SNEO WTZZ AUBG BUTE BACA MIKL POLV COMO EGLT SWAS MARS ZADA AJAC SCOA ACOR ALME MMET ORID IZMI NICO SAVU SUN6 MNSK TER2 SMLA IJMU DYNG DEVA MALL MAH1 LODZ ZYWI AUTN ENTZ VILL"
    # site = "0320 0340 0455 5993 0630 0710 0715 0800 HUID MIYI PIDI PUGE PZHA YANB YANY YUME"
    #GER
    # site = "TERS  IJMU  DELF  VLIS  DENT  WSRT  KOS1  BRUX  DOUR  WARE  REDU  EIJS  TIT2  EUSK  DILL  DIEP  BADH  KLOP  FFMJ  KARL  HOBU  PTBB  GOET"
    site_list = site.split(" ")
    if area=="WuHan":
        obsdir = "/cache/hanjunjie/Data/"+year+"/OBS_EPN/"
        # obsdir = "/cache/hanjunjie/Data/"+year+"/OBS/"
        sp3dir = "/cache/hanjunjie/Data/"+year+"/SP3/"
        clkdir = "/cache/hanjunjie/Data/"+year+"/CLK/"
        ephdir = "/cache/hanjunjie/Data/"+year+"/NAV/"
        # dcbdir = "/home/hanjunjie/data/IONO/"+year+"/DCB/"
        upddir = "/cache/hanjunjie/Project/A-Paper-1/UPD/UPD_WithoutDCB/"
    #机构设置
    sp3_name = "gfz"
    clk_name = "gfz"
    eph_name = "brdm"
    # dcb_name = "CAS"

    change_gen(xmlfile,int(year),doy,hour,s_length,site_list,sys_GNSS)

    change_inp_PPP(xmlfile,obsdir,site_list,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,int(year),doy,hour,s_length,upddir,area)
    # change_out_PPP(xmlfile,int(year),doy,hour,s_length,type)
if __name__ == "__main__":
        main_iter()