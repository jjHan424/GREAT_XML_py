#-*- coding:utf-8 -*-

import os
import ftplib
import shutil
import PodBatch_win as Pod
from sys import argv

#decompress program
winRAR = "winRAR X -Y"
cddis = "cddis.gsfc.nasa.gov"
site_list_std =r"D:\gnss-data\orblsq-data\site_list"
def rnxo_download(site_list,path,year,doy):
    """
    site_list:[list] needed site list
    """
    with ftplib.FTP(cddis) as myftp:
        print(myftp.login())
        print(myftp.cwd(path))
        idx = 0
        while idx < len(site_list):
            site = site_list[idx]
            idx+=1
            file_name = site+doy+"0."+year[2:]+"o"
            if (os.path.exists(file_name)):
                print(file_name+" exist!")
                continue
            file_name+=".Z"
            try:
                with open("./data/"+file_name,"wb") as myfile:
                    myftp.retrbinary("RETR "+file_name,myfile.write)
                    print("Download "+file_name+" finish!!!")
                os.system(winRAR+" ./data/"+file_name)
            except (ftplib.all_errors) as e:
                print(e," Dowanload"+file_name+" fail!!")
                site_list.remove(site)
                idx -= 1
    print("Download Finish!!")
    


def download_main():
    dir = os.getcwd()
    dir = dir.split("\\")
    dir = dir[-1]
    year = dir[:4]
    doy =dir[4:7]
    rnxo_data_path = "/pub/gps/data/daily"+"/"+year+"/"+doy+"/"+year[2:]+"o"

   ## get site_list
    site_list=[]
    Pod.copyfile(site_list_std,"./site_list")
    with open("site_list","r") as sitelist_file:
        for temp_line in sitelist_file:
           site_list.append(temp_line.strip()) 
    print("get site list")

    if not os.path.exists("./data"):
        os.mkdir("./data")

    rnxo_download(site_list,rnxo_data_path,year,doy)

    #update site_list
    with open("site_list","w",newline="\n") as sitelist_file:
        for site in site_list:
            sitelist_file.writelines(" "+site+"\n")
    print("update site list file!")
 

if __name__ == "__main__": 
    dir_base =r"D:\gnss-data\orblsq-data"
    os.chdir(dir_base)
    dir = dir_base +"\\"+argv[1]
    #dir = dir_base + r"\2017003_3d"
    if (os.path.exists(dir)):
        os.chdir(dir)
        print(os.getcwd())
        download_main()
       






