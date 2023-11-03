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
import subprocess

def run_app(app_dir,app_name,xml_path,log_dir="./",log_name="./py.log"):
    cmd_log = os.path.join(log_dir, log_name)
    app_log = os.path.join("./", app_name + ".app_log")
    app_bin = os.path.join(app_dir, app_name)

    cmd = app_bin + " -x " + xml_path
    tmp = " "

    cmd_pearl = cmd + tmp
    cmd = cmd + tmp + " > " + cmd_log
    logging.info("cmd is : " + cmd_pearl)
    try:
        result = subprocess.getstatusoutput(cmd)
    except OSError:
        logging.error("run failed for throw except.")
        sys.exit()

def mkdir(dir):
    if os.path.exists(dir):
        logging.warning("This workdir {} is exist".format(dir))
    else:
        os.mkdir(dir)