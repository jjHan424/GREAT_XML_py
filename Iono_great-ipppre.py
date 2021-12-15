'''
Author: Han Junjie
Date: 2021-12-08 13:39:09
LastEditTime: 2021-12-15 15:27:17
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
    gen_rec.text = " " + site + " "
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
    while (s_length >= 86400):
        day = day + 1
        s_length = s_length - 86400
    while (s_length >= 3600):
        hour = hour + 1
        s_length = s_length - 3600
    while (s_length >= 60):
        min = min + 1
        s_length = s_length - 60
    sec = sec + s_length
    end.text = " {0:04}".format(int(yyyy)) + "-" + "{0:02}".format(int(mon)) + "-" + "{0:02}".format(int(day)) + " " + "{0:02}".format(int(hour)) + ":{0:02}".format(min) + ":{0:02} ".format(sec)
    tree.write(xml_file)


def change_inp_PPP(xml_file,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,dcbdir,dcb_name,year,doy,hour,s_length,upddir,type):
    tree = et.parse(xml_file)
    root = tree.getroot()
    inputs = root.find("inputs")
    day_length = s_length // 86400 + 1
    site_list = site.split(" ")
    
    inp_obs = inputs.find("rinexo")
    inp_sp3 = inputs.find("sp3")
    inp_clk = inputs.find("rinexc")
    inp_dcb = inputs.find("bias")
    inp_eph = inputs.find("rinexn")
    if (type == "PPPAR"):
            inp_upd = inputs.find("upd")
    cur_day = 0
    obs_text,sp3_text,clk_text,dcb_text,eph_text,upd_text = "","","","","",""
    yyyy = "{0:04}".format(year)
    while (cur_day < day_length):
        day = doy + cur_day
        #change obs
        obs_text = obs_text + "\n"
        for cur_site in site_list:
            obs_text = obs_text + "        " + obsdir  + "{0:03}/".format(day) + cur_site.lower() + "{0:03}".format(day) + "0." + yyyy[2:] + "o"
        #change nav
        eph_text = eph_text + "  " + ephdir + eph_name +  "{0:03}".format(day) + "0." + yyyy[2:] + "n"
        #change sp3
        y_temp,mon,day = doy2ymd(int(year),int(day))
        week = ymd2gpsweekday(int(year),mon,day)
        sp3_text = sp3_text + "  " + sp3dir + sp3_name + str(week) + ".sp3"
        #change clk
        clk_text = clk_text + "  " + clkdir + clk_name + str(week) + ".clk"
        #change dcb
        dcb_text = dcb_text + "  " + dcbdir + dcb_name + str(week) + ".BIA"
        cur_day = cur_day + 1
        #change upd
        if (type == "PPPAR"):
            upd_text = upd_text + "  " + upddir + "upd_nl_" + yyyy + "{0:03}".format(day) + "_GREC"
            upd_text = upd_text + "  " + upddir + "upd_wl_" + yyyy + "{0:03}".format(day) + "_GREC"
    
    inp_obs.text = obs_text + "\n        "
    inp_eph.text = eph_text + "  "
    inp_sp3.text = sp3_text + "  "
    inp_clk.text = clk_text + "  "
    inp_dcb.text = dcb_text + "  "
    if (type == "PPPAR"):
        inp_upd.text = upd_text + "  "
    tree.write(xml_file)

def change_inp_PL(xml_file,obsdir,site,ephdir,eph_name,year,doy,hour,s_length):
    tree = et.parse(xml_file)
    root = tree.getroot()
    inputs = root.find("inputs")
    day_length = s_length // 86400 + 1
    site_list = site.split(" ")
    
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
    else: 
        if (type == "PPPAR"):
            mode = "Fixed"

    #change flt
    out_temp = outputs.find("flt")
    out_temp.text = "  " + "flt/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".flt"

    #change enu
    out_temp = outputs.find("enu")
    out_temp.text = "  " + "enu/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".enu"

    #change recover
    out_temp = outputs.find("recover")
    out_temp.text = "  " + "res/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".res"

    #change recover
    out_temp = outputs.find("recover")
    out_temp.text = "  " + "res/PPP_$(rec)_" + "{0:04}".format(year) + "{0:03}_".format(doy) + mode + ".res"

    tree.write(xml_file)

def main_iter():
    #参数的传递
    year = argv[1]
    doy = int(argv[2])
    hour = int(argv[3])
    minute = 0
    sec = 0
    s_length = int(argv[4])
    site = argv[5]
    type = argv[6]
    sys_GNSS = argv[7]
    sys_Computer = argv[8]
    xmlfile = argv[9]
    #路径的设置
    obsdir = "/home/hanjunjie/data/IONO/"+year+"/OBS/"
    sp3dir = "/home/hanjunjie/data/IONO/"+year+"/SP3/"
    clkdir = "/home/hanjunjie/data/IONO/"+year+"/CLK/"
    ephdir = "/home/hanjunjie/data/IONO/"+year+"/NAV/"
    dcbdir = "/home/hanjunjie/data/IONO/"+year+"/DCB/"
    upddir = "/home/hanjunjie/data/IONO/"+year+"/UPD/"
    if (sys_Computer == "Win"):
        obsdir = ".\\data\\"
        sp3dir = ".\\data\\"
        clkdir = ".\\data\\"
        ephdir = ".\\data\\"
        dcbdir = ".\\data\\"
        upddir = ".\\data\\"
    #机构设置
    sp3_name = "cod"
    clk_name = "cod"
    eph_name = "brdm"
    dcb_name = "CAS"
    change_gen(xmlfile,int(year),doy,hour,s_length,site,sys_GNSS)
    
    if ("PPP" in type):
        change_inp_PPP(xmlfile,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,dcbdir,dcb_name,int(year),doy,hour,s_length,upddir,type)
        change_out_PPP(xmlfile,int(year),doy,hour,s_length,type)
    if (type == "PL"):
        change_inp_PL(xmlfile,obsdir,site,ephdir,eph_name,int(year),doy,hour,s_length)
if __name__ == "__main__":
        main_iter()