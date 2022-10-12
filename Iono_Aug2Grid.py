'''
Author: Han Junjie
Date: 2022-10-12 13:39:09
LastEditTime: 2022-10-12 13:39:09
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
    gen_rec.text = ""
    for i in range(len(site)):
        gen_rec.text = gen_rec.text + " " + site[i] + " "
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


def change_inp_PPP(xml_file,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,dcbdir,dcb_name,year,doy,hour,s_length,upddir,type):
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
    site_list = site.split(" ")   
    inp_obs = inputs.find("rinexo")
    inp_sp3 = inputs.find("sp3")
    inp_clk = inputs.find("rinexc")
    inp_dcb = inputs.find("bias")
    inp_eph = inputs.find("rinexn")
    if ("AR" in type):
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
        if ("AR" in type):
            upd_text = upd_text + "  " + upddir + "upd_nl_" + yyyy + "{0:03}".format(day) + "_GREC"
            upd_text = upd_text + "  " + upddir + "upd_wl_" + yyyy + "{0:03}".format(day) + "_GREC"
    
    inp_obs.text = obs_text + "\n        "
    inp_eph.text = eph_text + "  "
    inp_sp3.text = sp3_text + "  "
    inp_clk.text = clk_text + "  "
    inp_dcb.text = dcb_text + "  "
    if ("AR" in type):
        inp_upd.text = upd_text + "  "
    tree.write(xml_file)

def change_inp_Aug2Grid(xml_file,augdir,site):
    tree = et.parse(xml_file)
    root = tree.getroot()
    inputs = root.find("inputs")
    inp_aug = inputs.find("aug")
    aug_text= ""
    
    for cur_site in site:
        aug_text = aug_text + "\n"
        aug_text = aug_text + "      " + augdir + cur_site + "-GEC.aug"
    inp_aug.text = aug_text + "\n   "
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
def change_out_Aug2Grid(xml_file,area,rec_rm,rec_chk):
    tree = et.parse(xml_file)
    root = tree.getroot()
    outputs = root.find("outputs")
    
    server_dir = " server"+"-"+area+"-R"
    for cur_site in rec_rm:
        server_dir = server_dir + "-" + cur_site
    server_dir = server_dir +"-C"
    for cur_site in rec_chk:
        server_dir = server_dir + "-" + cur_site
    outputs.find("log").attrib["name"] = server_dir.split(" ")[1]
    save_dir = outputs.find("log").attrib["name"]
    if (not os.path.exists(save_dir)):
        os.mkdir(save_dir)
    server_dir = server_dir+"/"
    outputs.find("ppp").text = server_dir + "$(rec)-GEC-AR.ppp "
    outputs.find("flt").text = server_dir + "$(rec)-GEC-AR.flt "
    outputs.find("enu").text = server_dir + "$(rec)-GEC-AR.enu "
    outputs.find("aug").text = server_dir + "$(rec)-GEC-5.aug  "
    tree.write(xml_file)

def change_ionogrid(xml_file,area,rec_rm_list,rec_chk_list):
    tree = et.parse(xml_file)
    root = tree.getroot().find("ionogrid")
    root.find("Mask").text = " "  + area +" "
    if (area == "WuHan"):  
        root.find("RefLon").text = "     "  + "{:3.2f}".format(112.6) +"     "
        root.find("RefLat").text = "     "  + "{:3.2f}".format(31.8) +"      "
        root.find("SpaceLon").text = "   "  + "{:.2f}".format(0.5) +"       "
        root.find("SpaceLat").text = "   "  + "{:.2f}".format(0.5) +"       "
        root.find("CountLon").text = "   "  + "{:2d}".format(7) +"         "
        root.find("CountLat").text = "   "  + "{:2d}".format(6) +"         "
        root.find("bias_baseline").text = "  "  + "{:.2f}".format(150) +"     "
        root.find("maxdis_wgt").text = "     "  + "{:.2f}".format(100) +"     "
    if (area == "HongKong"):  
        root.find("RefLon").text = "     "  + "{:3.2f}".format(113.8) +"     "
        root.find("RefLat").text = "     "  + "{:3.2f}".format(22.6) +"      "
        root.find("SpaceLon").text = "   "  + "{:.2f}".format(0.1) +"       "
        root.find("SpaceLat").text = "   "  + "{:.2f}".format(0.1) +"       "
        root.find("CountLon").text = "   "  + "{:2d}".format(6) +"         "
        root.find("CountLat").text = "   "  + "{:2d}".format(5) +"         "
        root.find("bias_baseline").text = "  "  + "{:.2f}".format(50) +"     "
        root.find("maxdis_wgt").text = "     "  + "{:.2f}".format(30) +"     "
    root.find("rec_rm").text = " "
    for cur_site in rec_rm_list:
        if (cur_site == "NONE"):
            continue
        root.find("rec_rm").text = root.find("rec_rm").text + cur_site + " "
    # root.find("rec_rm").text = root.find("rec_rm").text + " "
    root.find("rec_chk").text = " "
    for cur_site in rec_chk_list:
        if (cur_site == "NONE"):
            continue
        root.find("rec_chk").text = root.find("rec_chk").text + cur_site + " "
    # root.find("rec_chk").text = root.find("rec_chk").text + " "
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
    rec_rm = argv[7]
    rec_chk = argv[8]
    xmlfile = argv[9]
    #路径的设置
    obsdir = "/home/hanjunjie/data/IONO/"+year+"/OBS/"
    sp3dir = "/home/hanjunjie/data/IONO/"+year+"/SP3/"
    clkdir = "/home/hanjunjie/data/IONO/"+year+"/CLK/"
    ephdir = "/home/hanjunjie/data/IONO/"+year+"/NAV/"
    dcbdir = "/home/hanjunjie/data/IONO/"+year+"/DCB/"
    upddir = "/home/hanjunjie/data/IONO/"+year+"/UPD/"
    augdir = "/home/hanjunjie/Project/A-Paper-1/AUG_ELE/"+year+"{0:03}".format(doy)+"/server/"
    #机构设置
    sp3_name = "cod"
    clk_name = "cod"
    eph_name = "brdm"
    dcb_name = "CAS"
    #区域设置
    if (area=="WuHan"):
        site = ["WHYJ","WHXZ","WHDS","WHSP","N004","N010","N028","N047","N062","N068","XGXN","WUDA","N032","E033"]
    if (area=="HongKong"):
        site = ["HKTK","T430","HKLT","HKKT","HKSS","HKWS","HKSL","HKST","HKKS","HKCL","HKSC","HKPC","HKNP","HKMW","HKLM","HKOH"]
    #多测站处理
    rec_rm_list = rec_rm.split(",")
    rec_chk_list = rec_chk.split(",")
    change_gen(xmlfile,int(year),doy,hour,s_length,site,sys_GNSS)
    change_inp_Aug2Grid(xmlfile,augdir,site)
    change_out_Aug2Grid(xmlfile,area,rec_rm_list,rec_chk_list)
    change_ionogrid(xmlfile,area,rec_rm_list,rec_chk_list)
if __name__ == "__main__":
        main_iter()