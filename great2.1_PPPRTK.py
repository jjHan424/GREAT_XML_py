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

def change_gen(xml_file,year,doy,hour,s_length,site,sys,site_aug,mode):
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
    gen_rover = gen.find("rover")
    gen_rover.text = ""
    for i in range(len(site)):
        gen_rover.text = gen_rover.text + " " + site[i] + " "
    if mode == "Aug":
        for i in range(len(site_aug)):
            gen_rec.text = gen_rec.text + " " + site_aug[i] + " "
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


def change_out_PPPRTK(xml_file,site,mode):
    tree = et.parse(xml_file)
    root = tree.getroot()
    outputs = root.find("outputs")
    
    server_dir = " client"+"-"+site[0]+"-"+mode
    outputs.find("log").attrib["name"] = server_dir.split(" ")[1]
    save_dir = outputs.find("log").attrib["name"]
    if (not os.path.exists(save_dir)):
        os.mkdir(save_dir)
    server_dir = server_dir+"/"
    outputs.find("ppp").text = server_dir + "$(rec)-GEC.ppp "
    outputs.find("flt").text = server_dir + "$(rec)-GEC.flt "
    outputs.find("enu").text = server_dir + "$(rec)-GEC.enu "
    outputs.find("aug").text = server_dir + "$(rec)-GEC-I.aug  "
    outputs.find("kml").text = server_dir + "$(rec)-GEC.kml  "
    tree.write(xml_file)

def change_ionogrid(xml_file,Coef_a,Coef_b,mode):
    tree = et.parse(xml_file)
    root_ionogrid = tree.getroot().find("ionogrid")
    root_npp = tree.getroot().find("npp")
    if (mode == "Aug"):
        root_npp.find("correct_obs").text = " YES "
        root_npp.find("grid_aug").text = " NO "
    if (mode == "Grid_Chk"):
        root_ionogrid.find("isWgt").text = " CHKSITE "
        root_npp.find("correct_obs").text = " NO "
        root_npp.find("grid_aug").text = " YES "
    if (mode == "Grid_Ele"):
        root_ionogrid.find("isWgt").text = " EleWgt "
        root_npp.find("correct_obs").text = " NO "
        root_npp.find("grid_aug").text = " YES "
        for sys in Coef_a.keys():
            root_ionogrid.find("a_Wgt").attrib[sys] = "{:05f}".format(Coef_a[sys])
            root_ionogrid.find("b_Wgt").attrib[sys] = "{:05f}".format(Coef_b[sys])
    if (mode == "Grid"):
        root_ionogrid.find("isWgt").text = " Grid "
        root_npp.find("correct_obs").text = " NO "
        root_npp.find("grid_aug").text = " YES "
        
    tree.write(xml_file)

def change_inp_PPPRTK(xml_file,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,augdir,year,doy,hour,s_length,upddir,site_aug,mode):
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
    inp_upd = inputs.find("upd")
    if mode == "Aug":
        inp_aug = inputs.find("aug")
        inputs.find("aug_grid").text = ""
    else:
        inp_aug = inputs.find("aug_grid")
        inputs.find("aug").text = ""
    
    cur_day = 0
    obs_text,sp3_text,clk_text,dcb_text,eph_text,upd_text,aug_text = "","","","","","",""
    yyyy = "{0:04}".format(year)
    if site[0][0:2] == "HK":
        area = "HongKong"
    else:
        area = "WuHan2"
    while (cur_day < day_length):
        day = doy + cur_day
        #change obs
        obs_text = obs_text + "\n"
        for cur_site in site_list:
            if area == "WuHan2":
                obs_text = obs_text + "        " + obsdir  + "{0:03}/".format(day) + cur_site.upper() + "{0:03}".format(day) + "0." + yyyy[2:] + "o\n"
            if area == "HongKong":
                obs_text = obs_text + "        " + obsdir  + "{0:03}/".format(day) + cur_site.lower() + "{0:03}".format(day) + "0." + yyyy[2:] + "o\n"
        #change nav
        eph_text = eph_text + "  " + ephdir + eph_name +  "{0:03}".format(day) + "0." + yyyy[2:] + "n"
        #change upd
        upd_text = upd_text + "\n  " + upddir + "upd_nl_" + yyyy + "{0:03}".format(day) + "_GEC\n"
        upd_text = upd_text + "  " + upddir + "upd_wl_" + yyyy + "{0:03}".format(day) + "_GEC\n"
        #change sp3
        y_temp,mon,day = doy2ymd(int(year),int(day))
        week = ymd2gpsweekday(int(year),mon,day)
        sp3_text = sp3_text + "  " + sp3dir + sp3_name + str(week) + ".sp3"
        #change clk
        clk_text = clk_text + "  " + clkdir + clk_name + str(week) + ".clk"
        #change aug
        aug_text = aug_text + "\n"
        if mode == "Aug":
            for cur_site in site_aug:
                aug_text = aug_text + "        " + augdir  + cur_site.upper() + "-GEC.aug\n"
        else:
            aug_text = aug_text + "        " + augdir + "server-" + area + "-R-NONE-C-" + site[0] + "/" + "GREAT-GEC-5.grid"
        cur_day = cur_day + 1
    
    inp_obs.text = obs_text + "   "
    inp_eph.text = eph_text + "  "
    inp_sp3.text = sp3_text + "  "
    inp_clk.text = clk_text + "  "
    inp_upd.text = upd_text + "  "
    inp_aug.text = aug_text + "    "
    root.find("outputs").find("log").attrib["name"] = "client-"+site[0]+"-"+mode
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
    site = [argv[6]]
    mode = argv[7]
    xmlfile = argv[8]
    #路径的设置
    obsdir = "/cache/hanjunjie/Data/"+year+"/OBS/"
    sp3dir = "/cache/hanjunjie/Data/"+year+"/SP3/"
    clkdir = "/cache/hanjunjie/Data/"+year+"/CLK/"
    ephdir = "/cache/hanjunjie/Data/"+year+"/NAV/"
    dcbdir = "/home/hanjunjie/data/IONO/"+year+"/DCB/"
    upddir = "/cache/hanjunjie/Project/A-Paper-1/UPD/UPD_WithoutDCB/"
    if mode == "Aug":
        augdir = "/cache/hanjunjie/Project/A-Paper-1/AUG_ELE/"+year+"{0:03}".format(doy)+"/server/"
    else:
        augdir = "/cache/hanjunjie/Project/A-Paper-1/Ele_Wgt/"+year+"{0:03}".format(doy)+"/"
    #机构设置
    sp3_name = "gfz"
    clk_name = "gfz"
    eph_name = "brdm"
    dcb_name = "CAS"
    #区域设置
    if (site[0]=="WUDA"):
        site_aug = ["XGXN","WHXZ","WHSP"]
    if (site[0]=="WHYJ"):
        site_aug = ["N068","XGXN","WHXZ"]
    if (site[0]=="N028"):
        site_aug = ["XGXN","WUDA","WHSP"]
    if (site[0]=="HKSC"):
        site_aug = ["HKST","HKPC","HKOH"]
    if (site[0]=="HKMW"):
        site_aug = ["HKPC","HKNP","HKLM"]
    if (site[0]=="HKTK"):
        site_aug = ["T430","HKSS","HKWS"]
    
    #多测站处理
    
    change_gen(xmlfile,int(year),doy,hour,s_length,site,sys_GNSS,site_aug,mode)
    change_inp_PPPRTK(xmlfile,obsdir,site,sp3dir,sp3_name,clkdir,clk_name,ephdir,eph_name,augdir,int(year),doy,hour,s_length,upddir,site_aug,mode)
    
    # change_inp_Aug2Grid(xmlfile,augdir,site)
    change_out_PPPRTK(xmlfile,site,mode)
    Coef_a,Coef_b = {},{}
    Coef_a["G"] = 0.002
    Coef_b["G"] = 0.015
    Coef_a["E"] = 0.002
    Coef_b["E"] = 0.015
    Coef_a["C"] = 0.002
    Coef_b["C"] = 0.015
    change_ionogrid(xmlfile,Coef_a,Coef_b,mode)
if __name__ == "__main__":
        main_iter()