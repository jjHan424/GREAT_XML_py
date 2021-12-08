#-*- coding:utf-8 -*-

#import unlzw
import math
import os
import ftplib
import xml.etree.ElementTree as et
from sys import argv
from PodBatch_win import copyfile
from PodBatch_win import ics_panda2gnut
from RnxoDownload import *

monthdays = [0,31,28,31,30,31,30,31,31,30,31,30,31]

def usage():
    print ("usage of argv")
    print ("argv:year doy ")
    return

def leapyear(year):
    if (year % 4 == 0):
        return 1
    if (year % 400 == 0):
        return 1
    if (year % 100 == 0 ):
        return 0
    return 0

def doy2ymd(year,doy):
    day = doy
    mon = 0
    if(doy>365):
        if(leapyear(year) != 1):
            year = year + 1
            day = day - 365	
    for i in range(13):
        monthday = monthdays[i]
        if ( i == 2 and leapyear(year) == 1):
            monthday += 1
        if day > monthday :
            day -= monthday 
        else:
            mon = i
            break

    return (year,mon,day)
        

def ymd2doy(year,mon,day):
    doy = day 
    for i in range(1,mon):
        doy += monthdays[i]
    if (mon > 2):
        doy += leapyear(year)
    return doy

def ymd2gpsweek(year,mon,day):

    mjd =  0.0
    if (mon <2):
        mon += 12
        year -=1
    mjd = 365.25*year - 365.25*year % 1.0 - 679006.0
    mjd += math.floor(30.6001*(mon+1))+2.0 - math.floor(year/100.0) + math.floor(year / 400) + day
    return int((mjd -44244.0)/7.0)

def ymd2gpsweekday(year,mon,day):

    mjd =  0.0
    if (mon <=2):
        mon += 12
        year -=1
    mjd = 365.25*year - 365.25*year % 1.0 - 679006.0
    mjd += math.floor(30.6001*(mon+1))+2.0 - math.floor(year/100.0) + math.floor(year / 400) + day
    week=int((mjd -44244.0)/7.0)
    d=mjd-44244-week*7
    return int(week*10+d)

class pod_nav:
    def __init__(self,max_iter=3):
        self.year = 2019 
        self.month = 1 
        self.day  = 1 
        self.doy = 1
        self.gpsweek = 2000
        self.sys_path = r"D:\gnss-data\orblsq-data\sys"
        self.directory = os.getcwd()
        self.pod_program = r'C:\Users\郑鸿杰\Desktop\gnut\trunk\build\Bin\RelWithDebInfo\great_itera_podnav'
        self.prepare= 'prepare'
        self.site_list = []
        self.max_iter = max_iter
        self.resfile = "orb_resfile"
        self.obsfile_path = ''

    def set_time(self,year,mon,day):
        self.year = year
        self.month = mon
        self.day = day
        self.doy = ymd2doy(self.year,self.month,self.day)
        self.gpsweek = ymd2gpsweek(self.year,self.month,self.day)
        self.str_prefix = str(self.year)+"{0:03}".format(self.doy)
        self.recclkfile = "rec_"+self.str_prefix
        self.satclkfile = "clk_"+self.str_prefix

    def set_doy(self,year,doy):
        self.year = year
        self.doy = doy
        self.month,self.day = doy2ymd(year,doy)
        self.gpsweek = ymd2gpsweek(self.year,self.month,self.day)
        self.str_prefix = str(self.year)+"{0:03}".format(self.doy)
        self.recclkfile = "rec_"+self.str_prefix
        self.satclkfile = "clk_"+self.str_prefix


    def check_file(self):

        return False 

    def copy_sysfile(self):
        copyfile(self.sys_path+r"/oceanload",self.directory+r"/oceanload")
        copyfile(self.sys_path+r"/poleut1",self.directory+r"/poleut1")
        copyfile(self.sys_path+r"/jpleph_de405_win",self.directory+r"/jpleph_de405_win")
        copyfile(self.sys_path+r"/jpleph_de405_win",self.directory+r"/jpleph_de405")
        copyfile(self.sys_path+r"/igs_absolute_08.atx",self.directory+r"/igs_absolute_08.atx")
        copyfile(self.sys_path+r"/sat_parameters_new",self.directory+r"/sat_parameters_new")
        copyfile(self.sys_path+r"/ocean_tide",self.directory+r"/ocean_tide")
        copyfile(self.sys_path+r"/leap_seconds",self.directory+r"/leap_seconds")
        copyfile(self.sys_path+r"/EGM",self.directory+r"/EGM")
        copyfile(self.sys_path+r"/gnut-orblsq.xml",self.directory+r"/gnut-orblsq.xml")
        copyfile(self.sys_path+r"/gnut-oi.xml",self.directory+r"/gnut-oi.xml")  
        return

    def get_sitelist(self):
        if ( not os.path.exists("site_list")):
            return
        with open("site_list","r") as site_f:
                for site in site_f:
                        self.site_list.append(site.strip())

    def generator_oixml(self):
        tree = et.parse("gnut-oi.xml")
        root = tree.getroot()
        gen = root.find("gen")
        beg = gen.find("beg")
        end = gen.find("end")
        beg.text = str(self.year)+"-"+"{0:02}".format(self.month)+"-"+"{0:02}".format(self.day)+" 00:00:00"
        end.text = str(self.year)+"-"+"{0:02}".format(self.month)+"-"+"{0:02}".format(self.day)+" 23:55:00"

        inputs = root.find("inputs")
        ics = inputs.find("ics")
        ics.text = "ics_"+str(self.year)+"{0:03}".format(self.doy)

        outputs = root.find("outputs")
        orb = outputs.find("ORB")
        orb.text = "orb_"+str(self.year)+"{0:03}".format(self.doy)

        tree.write("gnut-oi.xml")
        return
    


    def gnerator_xmlfile(self):
        tree = et.parse("gnut-orblsq.xml")
        root = tree.getroot()
        gen = root.find("gen")
        beg = gen.find("beg")
        end = gen.find("end")
        rec = gen.find("rec") 
        par = root.find("parameters")
        rec_str ="\n"
        rinexo_str ="\n"
        count = 0
        for site in self.site_list:
            new_Sitepar = et.Element("STA",{"sigCLK":"9000","sigPOS":"0.1_0.1_0.1","sigZTD":"0.201"})
            new_Sitepar.set("ID",site.upper())
            new_Sitepar.tail ="\n	   "
            par.append(new_Sitepar)
            rec_str +=site.upper() +" "
            rinexo_str += site+"{0:03}".format(self.doy)+"0."+str(self.year)[2:]+"o"+" "
            count +=1
            if (count ==10):
                rec_str+="\n"
                rinexo_str += "\n"
                count=0
        rec_str+="\n"
        rinexo_str+="\n"
        rec.text = rec_str
        beg.text = str(self.year)+"-"+"{0:02}".format(self.month)+"-"+"{0:02}".format(self.day)+" 00:00:00"
        end.text = str(self.year)+"-"+"{0:02}".format(self.month)+"-"+"{0:02}".format(self.day)+" 23:55:00"

        inputs = root.find("inputs")
        rinexo = inputs.find("rinexo")
        rinexo.text = rinexo_str
        rinexc = inputs.find("rinexc")
        rinexc.text = "clk_"+str(self.year)+"{0:03}".format(self.doy)+" "+"rec_"+str(self.year)+"{0:03}".format(self.doy)
        ics = inputs.find("ics")
        ics.text = "ics_"+str(self.year)+"{0:03}".format(self.doy)
        self.icsfile = ics.text
        snx = inputs.find("sinex")
        snx.text = self.snxfile
        orb = inputs.find("orb")
        orb.text = "orb_"+str(self.year)+"{0:03}".format(self.doy)
        dcb = inputs.find("biabern")
        dcb_prefix = str(self.year)[2:]+"{0:02}".format(self.month)+".DCB"
        dcb.text = " P1C1" + dcb_prefix + " P1P2"+dcb_prefix + " P2C2"+dcb_prefix


        tree.write("gnut-orblsq.xml")
        return
    
    def download_snxfile(self):
        file_name = "igs" + str(self.year)[2:]+"P"+str(self.gpsweek)+".snx.Z"
        self.snxfile = file_name[:-2]
        if (os.path.exists(self.snxfile)):
            print(self.snxfile+"snx file is existed!")
            return
        print("Begin ftp download snx file")
        with ftplib.FTP(cddis) as myftp:
            print(myftp.login())
            path = r"/pub/gps/products/" + str(self.gpsweek)
            print(myftp.cwd(path))
            try:
                with open(file_name,"wb") as myfile:
                    myftp.retrbinary("RETR "+file_name,myfile.write)
                    print("Download " + file_name+ "finish!!")
                
                # here use unlzw to uncompress .Z file
                with open(file_name,"rb") as myfile, open(self.snxfile,"wb") as snxfile:
                    buffer = myfile.read()
                    #snxfile.write(unlzw.unlzw(buffer))
                    
                #os.system(winRAR+" "+file_name)
            except (ftplib.all_errors) as e:
                print(e," Download"+file_name+" fail")
        return

    def copy_obsfile(self):
        if (os.path.exists(self.obsfile_path)):
            for dirs,folders,files in os.walk(self.obsfile_path):
                for obsfile in files:
                    if (obsfile[-1] != 'o'):
                        continue
                    copyfile(self.obsfile_path+"/"+obsfile,self.directory+"/"+obsfile)
        
    

    def prepare_icsfile(self):
        preapare_cmd ="cf -time "+ str(self.year)+ " " + "{0:03}".format(self.doy) + " 00 00 86400 -intv 300 -list site_list -rnxo -scan -snx "+self.snxfile+" -sysids G -orb brd -clk brd" 
        copyfile(self.sys_path+"/file_table",self.directory+"/file_table")
        copyfile(self.sys_path+"/RECEIVER.txt",self.directory+"/RECEIVER.txt")

        self.copy_obsfile()
           #os.removedirs(path)
                 
        print("begin prepare")
        os.system(self.prepare+" " + preapare_cmd)
        
        ics_panda2gnut(self.icsfile,self.doy,58119,58120)
        return


    def run_oi_podnav(self):

        oi_cmd = "great_oi" +" -x gnut-oi.xml" 
        os.system(oi_cmd)
        orb_cmd = "great_podlsq"+ " -x gnut-orblsq.xml" 
        os.system(orb_cmd)
        return

    def bakup_file(self,count):
        """
        bakcup resfile clkfile icsfile
        """
        copyfile("orb_resfile","orbresfile_"+str(count))
        copyfile(self.icsfile,"ics_"+str(count))
        copyfile(self.satclkfile,"satclk_"+str(count))
        copyfile(self.recclkfile,"recclk_"+str(count))
        return

def Win_Main():
    if (len(argv)  < 3):
        usage()
        return
     # test
    Pod = pod_nav(1)
    Pod.obsfile_path = Pod.directory+"/"+"{0:03}".format(Pod.doy)
    if (len(argv) == 4):
        Pod.set_time(int(argv[1]),int(argv[2]),int(argv[3]))
    if (len(argv) == 3):
        Pod.set_doy(int(argv[1]),int(argv[2]))
    os.chdir(r"D:\gnss-data\orblsq-data\\"+Pod.str_prefix+"_3d")
    Pod.directory = os.getcwd()
    print("now directory is "+Pod.directory)

    Pod.copy_sysfile()
    Pod.get_sitelist()
    Pod.download_snxfile()
    Pod.gnerator_xmlfile()
    Pod.prepare_icsfile()
    #ics_panda2gnut(Pod.icsfile,Pod.doy,58119,58120)
    Pod.generator_oixml()

    Pod.bakup_file(0)
    for iter in range(Pod.max_iter): 
        Pod.run_oi_podnav()
        Pod.bakup_file(iter+1)

    print("finish")
    return

def Linux_Main():
    if (len(argv) < 3):
        usage()
        return
    Pod = pod_nav(3)
    Pod.prepare='presrif'
    
    if (len(argv) == 3):
        Pod.set_doy(int(argv[1]),int(argv[2]))
    if (len(argv) == 4):
        Pod.set_time(int(argv[1]),int(argv[2]),int(argv[3]))

    os.chdir(r"/workfs/hjzheng/projects/pod_gal_qzs/pod_ecom/"+Pod.str_prefix+"_3d")
    Pod.directory = os.getcwd()
    Pod.sys_path = r"/project/hjzheng/sys"
    Pod.obsfile_path="/workfs/hjzheng/GNSS/pod_gal_qzs/obs/2018/"+"{0:03}".format(Pod.doy)
    Pod.copy_sysfile()
    ## jpleph_de405 need Linux
    copyfile(Pod.sys_path+r"/jpleph_de405",Pod.directory+r"/jpleph_de405")
    Pod.get_sitelist()

    #copy snx file
    #Pod.download_snxfile()
    Pod.snxfile = "igs" + str(Pod.year)[2:]+"P"+str(Pod.gpsweek)+".snx"
    copyfile(Pod.sys_path+"/"+Pod.snxfile,"./"+Pod.snxfile)
    Pod.gnerator_xmlfile()
    Pod.prepare_icsfile()
    #ics_panda2gnut(Pod.icsfile,Pod.doy,58119,58120)
    Pod.generator_oixml()

    Pod.bakup_file(0)
    for iter in range(Pod.max_iter): 
        Pod.run_oi_podnav()
        Pod.bakup_file(iter+1)

    print("finish")
    return






if __name__ == "__main__":
    Win_Main()
    #Linux_Main()

    #os.chdir("D:\gnss-data\orblsq-data\sys")
    #Pod = pod_nav(3)
    #for i in range(200):
    #   Pod.set_doy(2018,i+1)
    #   Pod.download_snxfile()
        
    



