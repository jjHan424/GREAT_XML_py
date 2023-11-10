import os
import shutil
import ftplib
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
import logging
import platform
from datetime import datetime
cur_platform = platform.system()
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/GREAT_XML_py")
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/GREAT_XML_py")
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday

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

#Change XML gen
def change_gen(xmlfile = "great2.1.xml",year = 2021,doy = 310, hour = 0, s_length = 86395, cur_sys = "GEC3", sampling = 30,site_list = ["XXXX","YYYY","ZZZZ"]):
    #Change beg and end
    change_gen_time(xmlfile,year,doy,hour,s_length)
    tree = et.parse(xmlfile)
    root = tree.getroot()
    gen = root.find("gen")
    #Change Sys
    gen_sys = gen.find("sys")
    sys_text = ""
    if ("G" in cur_sys):
        sys_text = "GPS"
    if ("E" in cur_sys):
        sys_text = sys_text + " GAL"
    if ("R" in cur_sys):
        sys_text = sys_text + " GLO"
    if ("C" in cur_sys):
        sys_text = sys_text + " BDS"
    sys_text = " " + sys_text + " "
    gen_sys.text = sys_text
    #Change Sampling
    gen.find("int").text = " {:>2} ".format(sampling)
    #Change Site
    gen_rec = gen.find("rec")
    gen_rec.text = ""
    for cur_site in site_list:
        gen_rec.text = gen_rec.text + " " + cur_site + " "
    #Change BDS Band for B2 or B3
    if ("C3" in cur_sys):
        root.find("bds").find("band").text = " 2 6 "
    if ("C2" in cur_sys):
        root.find("bds").find("band").text = " 2 7 "
    tree.write(xmlfile)

#Change XML ionogrid
def change_ionogrid(xmlfile = "great2.1.xml",area = "WUHAN",wgt_mode = "GRID",ref_bl = [12,13],space_bl = [0.5,0.5],count_bl = [3,4],rm_site_list = [""],ck_site_list = [""]):
    tree = et.parse(xmlfile)
    ionogrid = tree.getroot().find("ionogrid")
    ionogrid.find("Mask").text = area
    ionogrid.find("wgt_mode").text = wgt_mode
    ionogrid.find("RefLat").text = " {:.2f} ".format(ref_bl[0])
    ionogrid.find("RefLon").text = " {:.2f} ".format(ref_bl[1])
    ionogrid.find("SpaceLat").text = " {:.2f} ".format(space_bl[0])
    ionogrid.find("SpaceLon").text = " {:.2f} ".format(space_bl[1])
    ionogrid.find("CountLat").text = " {:>2d} ".format(count_bl[0])
    ionogrid.find("CountLon").text = " {:>2d} ".format(count_bl[1])
    ionogrid.find("rec_rm").text = ""
    for cur_site in rm_site_list:
        ionogrid.find("rec_rm").text = ionogrid.find("rec_rm").text + " " + cur_site + " "
    ionogrid.find("rec_chk").text = ""
    for cur_site in ck_site_list:
        ionogrid.find("rec_chk").text = ionogrid.find("rec_chk").text + " " + cur_site + " "
    tree.write(xmlfile)

#Change XML inputs aug
def change_inputs_aug(xmlfile = "great2.1.xml",aug_dir = "default",year = 2021, doy = 310, hour = 0, s_length = 86395, site_list = [""]):
    tree = et.parse(xmlfile)
    inputs_aug = tree.getroot().find("inputs").find("aug")
    day_length = 1
    hour_length = s_length / 3600
    while (hour_length >= 24):
        day_length = day_length + 1
        hour_length = hour_length - 24
    hour = hour + hour_length
    while (hour >= 24):
        day_length = day_length + 1
        hour = hour - 24
    count_day = 0
    inputs_aug.text = "\n"
    while (count_day < day_length):
        day = doy + count_day
        for cur_site in site_list:
            inputs_aug.text = inputs_aug.text + "     " + os.path.join(aug_dir,"{:0>4}{:0>3}".format(year,day),"server",cur_site+"-GEC.aug") + "\n"
        count_day = count_day + 1
    tree.write(xmlfile)

#Change XML outputs log
def change_outputs_log(xmlfile = "great2.1.xml",purpose = "ByHjj",mode = "TIME"):
    tree = et.parse(xmlfile)
    outputs_log = tree.getroot().find("outputs").find("log")
    cur_time = datetime.utcnow()
    if mode == "TIME":
        outputs_log.attrib["name"] = "{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}".format(purpose,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second)
    tree.write(xmlfile)
 
 #Change XML outputs aug

#Change XML outputs auggrid
def change_outputs_aug2grid(xmlfile = "great2.1.xml",area = "XXXX",rm_site_list= [""],ck_site_list = [""],cur_sys = "GEC",sampling = 5):
    tree = et.parse(xmlfile)
    outputs_aug = tree.getroot().find("outputs").find("aug")
    outputs_aug.text = "{}-R-".format(area)
    for cur_site in rm_site_list:
        outputs_aug.text = outputs_aug.text + cur_site + "-"
    outputs_aug.text = outputs_aug.text + "C-"
    for cur_site in ck_site_list:
        outputs_aug.text = outputs_aug.text + cur_site + "-"
    outputs_aug.text = outputs_aug.text[:-1]
    outputs_aug.text = os.path.join(outputs_aug.text,"$(rec)-{}-{:d}.aug".format(cur_sys,sampling))
    tree.write(xmlfile)
