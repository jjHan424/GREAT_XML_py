import os
import shutil
import ftplib
import sys
sys.path.insert(0,"D:\Tools\GREAT_XML_py")
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
# from generate_xmlfile import *
import logging
import shutil
import Iono_Aug2Grid as Aug2Grid
import Linux_Win_HJJ as Run
import subprocess

cur_plat_form = sys.platform
if "win" in cur_plat_form:
    file_dot = "\\"
else:
    file_dot = "/"
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
##----------SET 1----------##
XML_origin_path = r"E:\1Master_2\3-IUGG\Python_Test\great-Aug2Grid.xml"
work_dir = r"E:\1Master_2\3-IUGG\Python_Test"
software = r"/cache/hanjunjie/Software/GREAT/great2.1_grid230627/build_Linux/Bin"
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 9:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: area sampling year doy count mode system rec_chk\nWuHan 30 2021 310 1 CROSS GEC3 XXXX_XXXX_Cycle")
    sys.exit()
area = sys.argv[1] # "EPN_GER" "HongKong" "WuHan"
sampling = sys.argv[2] # "30" or "5"
year = sys.argv[3]
doy = sys.argv[4]
count = sys.argv[5]
mode = sys.argv[6]
cur_sys = sys.argv[7]
hour = 0
s_length = 86395
log_path = work_dir + "/" + area + "_" + sampling + "S" + "_" + year + "_" + doy + "_" + count + ".log"
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 3----------##
if area == "EPN_GER":
    aug_path = "/cache/hanjunjie/Project/B-IUGG/AUG_EPN_UPD_UC/YYYYDOY/server"
    site_list = ["TERS","IJMU","DENT","WSRT","KOS1","BRUX","DOUR","WARE","REDU","EIJS","TIT2","EUSK","DILL","DIEP","BADH","KLOP","FFMJ","KARL","HOBU","PTBB","GOET"]
    Mask = "EPN_GER"
    RefLon,RefLat = 3.4,53.36
    SpaceLon,SpaceLat = 1.5,1.5
    CountLon,CountLat = 6,4
elif area == "WuHan":
    aug_path = "/cache/hanjunjie/Project/B-IUGG/AUG_CHN_UPD_UC_" + sampling + "S/" + "/YYYYDOY/server"
    site_list = ["WHYJ","WHXZ","WHDS","WHSP","N028","N047","N068","XGXN","WUDA"]
    Mask = "WuHan"
    RefLon,RefLat = 113.2,31.8
    SpaceLon,SpaceLat = 0.5,0.5
    CountLon,CountLat = 6,5
elif area == "HongKong":
    aug_path = "/cache/hanjunjie/Project/B-IUGG/AUG_CHN_UPD_UC_" + sampling + "S/" + "/YYYYDOY/server"
    site_list = ["HKTK","T430","HKLT","HKKT","HKSS","HKWS","HKSL","HKST","HKKS","HKCL","HKSC","HKPC","HKNP","HKMW","HKLM","HKOH"]
    Mask = "EPN_GER"
    RefLon,RefLat = 113.8,22.6
    SpaceLon,SpaceLat = 0.1,0.1
    CountLon,CountLat = 6,5
else:
    logging.error(area + " is not available")

##----------START------------##
rec_rm = []
rec_chk = []
mode == "CROSS" ##其他功能未完善
if mode == "CROSS":
    rec_chk = ["CROSS"]
    rec_rm = sys.argv[8].split("_")
    if len(rec_rm) < 2 and rec_rm[0] == "Cycle":
        site_list_temp = site_list
        site_list_temp.append("Cycle")
        rec_rm = site_list_temp
    else:
        rec_rm = sys.argv[8].split("_")
elif mode == "GRID":
    if len(sys.argv) < 9:
        rec_chk,rec_rm = "",""
    elif len(sys.argv) < 10:
        rec_rm.append(sys.argv[8])
        rec_chk = [""]
    else:
        rec_rm.append(sys.argv[8])
        rec_chk.append(sys.argv[9])

year_int,doy_int,count_int = int(year),int(doy),int(count)
os.chdir(work_dir)
logging.info("\n\
             ##-------Start Aug2Grid in {}\n\
             ##-------From {}-{} Last {}\n\
             ##-------WorkDir is {}\n\
             ##-------Origin XML is {}\n\
             ##-------APP Dir is {}\n\
             ##-------Check site is {}\n\
             ##-------Remove site is is {}\n".format(area,year,doy,count,work_dir,XML_origin_path,software,rec_chk,rec_rm))
while count_int > 0:
    cur_dir = work_dir + file_dot + "{:0>4}".format(year_int) + "{:0>3}".format(doy_int)
    if os.path.exists(cur_dir):
        logging.warning("This workdir {} is exist".format(cur_dir))
    else:
        os.mkdir(cur_dir)
    os.chdir(cur_dir)
    cur_xml_name = "great-Aug2Grid-{}-{:0>4}-{:0>3}.xml".format(area,year_int,doy_int)
    shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
    cur_aug_path = aug_path.replace("YYYYDOY","{:0>4}{:0>3}".format(year_int,doy_int))
    if "Cycle" in rec_rm:
        for cur_site in rec_rm:
            if cur_site == "Cycle":
                break        
            Aug2Grid.change_gen(cur_xml_name,year_int,doy_int,hour,s_length,site_list,cur_sys)
            Aug2Grid.change_inp_Aug2Grid(cur_xml_name,cur_aug_path,site_list)
            Aug2Grid.change_out_Aug2Grid(cur_xml_name,area,[cur_site],rec_chk,sampling)
            Aug2Grid.change_ionogrid(cur_xml_name,area,RefLon,RefLat,SpaceLon,SpaceLat,CountLon,CountLat,[cur_site],rec_chk)
            logging.info(" Current Start:: year = {:0>4}, doy = {:0>3}, remove site = {},check site = {}".format(year_int,doy_int,[cur_site],rec_chk))
            cmd = software + "/GREAT_Aug2Grid" + " -x " + cur_xml_name + " > " + "Current.log"
            # subprocess.getoutput(cmd)
            Run.run_app(software,"GREAT_Aug2Grid",cur_xml_name,log_dir="./",log_name=cur_site+"-py.log")
            logging.info("Current Finish:: year = {:0>4}, doy = {:0>3}, remove site = {},check site = {}".format(year_int,doy_int,[cur_site],rec_chk))
    else:
        Aug2Grid.change_gen(cur_xml_name,year_int,doy_int,hour,s_length,site_list,cur_sys)
        Aug2Grid.change_inp_Aug2Grid(cur_xml_name,cur_aug_path,site_list)
        Aug2Grid.change_out_Aug2Grid(cur_xml_name,area,rec_rm,rec_chk,sampling)
        Aug2Grid.change_ionogrid(cur_xml_name,area,RefLon,RefLat,SpaceLon,SpaceLat,CountLon,CountLat,rec_rm,rec_chk)
        logging.info(" Current Start:: year = {:0>4}, doy = {:0>3}, remove site = {},check site = {}".format(year_int,doy_int,rec_rm,rec_chk))
        cmd = software + "/GREAT_Aug2Grid" + " -x " + cur_xml_name + " > " + "Current.log"
        # subprocess.getoutput(cmd)
        logging.info("Current Finish:: year = {:0>4}, doy = {:0>3}, remove site = {},check site = {}".format(year_int,doy_int,rec_rm,rec_chk))

    
    ##-----------Delete *.diff-----------##
    cur_dir_list = os.listdir(cur_dir)
    for cur_path_name in cur_dir_list:
        if cur_path_name[0:6] != "server":
            continue
        cur_path_dir_list = os.listdir(cur_dir + "/" + cur_path_name)
        for cur_file_delete in cur_path_dir_list:
            if cur_file_delete[len(cur_file_delete)-4:len(cur_file_delete)] == "diff":
                os.remove(cur_dir + "/" + cur_path_name + "/" + cur_file_delete)

    count_int = count_int - 1
    doy_int = doy_int + 1

    

        



