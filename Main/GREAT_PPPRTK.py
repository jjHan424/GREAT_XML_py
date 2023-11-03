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
import great2_PPPRTK_virtual as PPPRTK
import subprocess
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"

##----------SET 1----------##
XML_origin_path = r"D:\Tools\GREAT_XML_py\XML\great2.1_PPPRTK_3600.xml"
work_dir = r"E:\1Master_2\3-IUGG\Python_Test"
software = r"/cache/hanjunjie/Software/GREAT/great2.1_grid230627/build_Linux/Bin"
hour = 0
s_length = 86395
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 9:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: area sampling year doy count mode system rec_chk\nWuHan 30 2021 310 1 CROSS GEC3 XXXX_XXXX_Cycle")
    sys.exit()
area = sys.argv[1] # "EPN_GER" "HongKong" "WuHan"
rec_site = sys.argv[2].split("_")
sampling = sys.argv[3] # "30" or "5"
year = sys.argv[4]
doy = sys.argv[5]
count = sys.argv[6]
mode = sys.argv[7]
cur_sys = sys.argv[8]
p_Ion = float(sys.argv[9])
p_Trp = float(sys.argv[10])
hour = 0
s_length = 86395
log_path = work_dir + "/" + area + "_" + mode + "{:0>2}-{:0>2}".format(int(p_Ion*10),int(p_Trp*10)) + "_" + sampling + "S" + "_" + year + "_" + doy + "_" + count + ".log"
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 3 (File Path)----------##
if "All" in rec_site:
    if area == "EPN_GER":
        rec_site = ["TERS","IJMU","DENT","WSRT","KOS1","BRUX","DOUR","WARE","REDU","EIJS","TIT2","EUSK","DILL","DIEP","BADH","KLOP","FFMJ","KARL","HOBU","PTBB","GOET"]
    elif area == "WuHan":
        rec_site = ["WHYJ","WHXZ","WHDS","WHSP","N028","N047","N068","XGXN","WUDA"]
    elif area == "HongKong":
        rec_site = ["HKTK","T430","HKLT","HKKT","HKSS","HKWS","HKSL","HKST","HKKS","HKCL","HKSC","HKPC","HKNP","HKMW","HKLM","HKOH"]
    else:
        logging.error("{} is not available".format(area))

if area == "EPN_GER":
    obsdir = "/cache/hanjunjie/Data/YYYY/OBS_EPN"
    upddir = "/cache/hanjunjie/Project/B-IUGG/UPD_Europe_RAW_ALL_30S/UPD_WithoutDCB"
else:
    if sampling == "1":
        obsdir = "/cache/hanjunjie/Data_1s/YYYY/OBS"
    else:
        obsdir = "/cache/hanjunjie/Data/YYYY/OBS"
    if area == "HongKong":
        upddir = "/cache/hanjunjie/Project/B-IUGG/UPD_CHN_RAW_ALL_BDS2_30S/UPD_WithoutDCB"
    if area == "WuHan":
        upddir = "/cache/hanjunjie/Project/B-IUGG/UPD_CHN_RAW_ALL_BDS3_30S/UPD_WithoutDCB"
sp3dir = "/cache/hanjunjie/Data/YYYY/SP3"
clkdir = "/cache/hanjunjie/Data/YYYY/CLK"
ephdir = "/cache/hanjunjie/Data/YYYY/NAV"
augdir = "/cache/hanjunjie/Project/B-IUGG/Aug2Grid/YYYYDOY"

#待完成
dcbdir = "/home/hanjunjie/data/IONO/"+year+"/DCB/"
rotidir = "/cache/hanjunjie/Project/A-Paper-1/ROTI/"
if mode == "Aug":
    augdir = "/cache/hanjunjie/Project/A-Paper-1/AUG_ELE/YYYYDOY/server/"
else:
    augdir = "/cache/hanjunjie/Project/B-IUGG/Aug2Grid/YYYYDOY"
#机构设置
sp3_name = "gfz"
clk_name = "gfz"
eph_name = "brdm"
dcb_name = "CAS"

year_int,doy_int,count_int = int(year),int(doy),int(count)
os.chdir(work_dir)
while count_int > 0:
    cur_dir = os.path.join(work_dir,"{:0>4}".format(year_int) + "{:0>3}".format(doy_int))
    Run.mkdir(cur_dir)
    os.chdir(cur_dir)
    Run.mkdir("{:0>4}{:0>3}_PPP".format(year_int,doy_int))
    Run.mkdir("{:0>4}{:0>3}_FLT".format(year_int,doy_int))
    Run.mkdir("{:0>4}{:0>3}_ENU".format(year_int,doy_int))
    Run.mkdir("{:0>4}{:0>3}_KML".format(year_int,doy_int))
    Run.mkdir("{:0>4}{:0>3}_AUG".format(year_int,doy_int))
    cur_obsdir = obsdir.replace("YYYY","{:0>4}".format(year_int))
    cur_sp3dir = sp3dir.replace("YYYY","{:0>4}".format(year_int))
    cur_clkdir = clkdir.replace("YYYY","{:0>4}".format(year_int))
    cur_ephdir = ephdir.replace("YYYY","{:0>4}".format(year_int))
    cur_augdir = augdir.replace("YYYYDOY","{:0>4}{:0>3}".format(year_int,doy_int))
    for cur_site in rec_site:
        cur_xml_file = "great2.1_PPPRTK-{}-{:0>4}-{:0>3}.xml".format(cur_site,year_int,doy_int)
        shutil.copy(XML_origin_path,cur_xml_file)
        PPPRTK.change_gen(cur_xml_file,year_int,doy_int,hour,s_length,[cur_site],cur_sys,sampling,[""],mode)
        PPPRTK.change_inp_Basic(cur_xml_file,area,cur_obsdir,[cur_site],cur_sp3dir,sp3_name,cur_clkdir,clk_name,cur_ephdir,eph_name,year_int,doy_int,hour,s_length,mode)
        PPPRTK.change_inp_UPD(cur_xml_file,year_int,doy_int,hour,s_length,upddir)
        PPPRTK.change_inp_AugGrid(cur_xml_file,area,cur_site,"30",cur_augdir,year_int,doy_int,hour,s_length,[""],mode)
        PPPRTK.change_inp_model(cur_xml_file,cur_sys)
        PPPRTK.change_out_PPPRTK_New(cur_xml_file,year_int,doy_int,mode,cur_site,p_Ion,p_Trp)
        
    count_int = count_int - 1
    doy_int = doy_int + 1
