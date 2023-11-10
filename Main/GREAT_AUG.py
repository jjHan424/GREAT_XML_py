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
import Linux_Win_HJJ as Run
cur_platform = platform.system()
fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
if (cur_platform == "Darwin"):
    sys.path.insert(0,"/Users/hanjunjie/tools/GREAT_XML_py")
    XML_origin_path = r"/Users/hanjunjie/tools/GREAT_XML_py/XML/great-Aug2Grid.xml"
else:
    sys.path.insert(0,"/cache/hanjunjie/Software/Tools/GREAT_XML_py")
    XML_origin_path = r"/cache/hanjunjie/Software/Tools/GREAT_XML_py/XML/great-Aug2Grid.xml"
import great2_generate_xml as gen_xml
PURPOSE = "AUG2GRID"

##----------Python Log----------##
cur_time = datetime.utcnow()
log_path = os.path.join("./","{}-{:0>4d}{:0>2d}{:0>2d}-{:0>2d}:{:0>2d}:{:0>2d}.pylog".format(PURPOSE,cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second))
logging.basicConfig(level=logging.DEBUG,filename=log_path,filemode="w",format=fmt)
##----------SET 1----------##
work_dir = r"/Users/hanjunjie/Master_3/XML_py_test"
software = r"/cache/hanjunjie/Software/GREAT/great2.1_grid230627/build_Linux/Bin"
##----------SET 2 (ARGV)----------##
if len(sys.argv) < 12:
    logging.error("Not Enough argv! Please Check")
    logging.error("USAGE: year doy hour s_length system sampling count area grid_mode rm_site ck_site\
                  \2021 310 2 79195 GEC3 30 1 EPN_GER ChkSite XXXX_XXXX XXXX_XXXX")
    sys.exit()
#GEN
year = sys.argv[1]
doy = sys.argv[2]
hour = sys.argv[3]
s_length = sys.argv[4]
cur_sys = sys.argv[5]
sampling = sys.argv[6] # "30" or "5"
count = sys.argv[7]
#NPP
area = sys.argv[8]
grid_mode = sys.argv[9]
rm_site = sys.argv[10]
ck_site = sys.argv[11]
#site list generate
rm_site_list,ck_site_list = [],[]
site_temp = rm_site.split("_")
for cur_site in site_temp:
    if cur_site != "NONE":
        rm_site_list.append(cur_site)
site_temp = ck_site.split("_")
for cur_site in site_temp:
    if cur_site != "NONE":
        ck_site_list.append(cur_site)
if grid_mode.upper() == "CHKCROSS":
    ck_site_list = ["CROSS"]


# SET AREA
if area == "EPN_GER":
    aug_path = "/cache/hanjunjie/Project/B-IUGG/AUG_EPN_UPD_UC/server"
    site_list = ["TERS","IJMU","DENT","WSRT","KOS1","BRUX","DOUR","WARE","REDU","EIJS","TIT2","EUSK","DILL","DIEP","BADH","KLOP","FFMJ","KARL","HOBU","PTBB","GOET"]
    Mask = "EPN_GER"
    RefLon,RefLat = 3.4,53.36
    SpaceLon,SpaceLat = 1.5,1.5
    CountLon,CountLat = 6,4
else:
    sys.exit()

count_int,doy_int,year_int = int(count),int(doy),int(year)
logging.info("##--START ALL--##")
while count_int > 0:
    #Check and Make Dir
    os.chdir(work_dir)
    cur_dir = os.path.join(work_dir,"{:0>4}".format(year_int) + "{:0>3}".format(doy_int))
    if os.path.exists(cur_dir):
        logging.warning("This workdir {} is exist".format(cur_dir))
    else:
        os.mkdir(cur_dir)
    os.chdir(cur_dir)
    logging.info("START Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    #Copy XML File
    cur_xml_name = "great-Aug2Grid-{}-{:0>4}-{:0>3}.xml".format(area,year_int,doy_int)
    shutil.copy(XML_origin_path,"{}".format(cur_xml_name))
    #Change Gen
    gen_xml.change_gen(cur_xml_name,year_int,doy_int,int(hour),int(s_length),cur_sys,int(sampling),site_list)
    #Change ionogrid
    gen_xml.change_ionogrid(cur_xml_name,area,grid_mode,[RefLat,RefLon],[SpaceLat,SpaceLon],[CountLat,CountLon],rm_site_list,ck_site_list)
    #Change input aug
    gen_xml.change_inputs_aug(cur_xml_name,aug_path,year_int,doy_int,int(hour),int(s_length),site_list)
    #Change outputs auggrid
    gen_xml.change_outputs_aug2grid(cur_xml_name,area,rm_site_list,ck_site_list,cur_sys,int(sampling))
    #Change outputs log
    gen_xml.change_outputs_log(cur_xml_name,PURPOSE)
    logging.info("END Generate XML {:0>4}-{:0>3}".format(year_int,doy_int))
    logging.info("Start Process {} {:0>4}-{:0>3}".format(PURPOSE,year_int,doy_int))
    #Start the Programe
    Run.run_app(software,"GREAT_Aug2Grid",cur_xml_name,log_dir="./",log_name=cur_site+"-app.log")
    doy_int = doy_int + 1
    count_int = count_int - 1

logging.info("##--NORMAL END--##")