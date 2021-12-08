import PodBatch_win 
import xml.etree.ElementTree as et
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday
from sys import argv

def change_time(filename,year,doy,hour,minute,second,sslength):
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    sslength = int(sslength)
    yyyy,mon,day = doy2ymd(int(year),int(doy)+1)
    year = "{0:04}".format(int(yyyy))  

    doy = "{0:03}".format(int(doy))

    tree = et.parse(filename)
    root = tree.getroot()
    gen = root.find("gen")
    beg = gen.find("beg")
    end = gen.find("end")

    beg.text = year+"-"+"{0:02}".format(mon)+"-"+"{0:02}".format(day)+ " "+"{0:02}".format(hour)+":"+"{0:02}".format(minute)+":"+"{0:02}".format(second)
    endtime = int(hour)*3600+int(minute)*60+int(second)+int(sslength)
    countday = 0
    counth = 0
    countmin = 0
    while(endtime >= 86400):
        countday = countday + 1
        endtime = endtime -86400
    while(endtime >= 3600):
        counth = counth + 1
        endtime = endtime -3600
    while(endtime >= 60):
        countmin = countmin + 1
        endtime = endtime -60

    enddoy = int(doy) + countday + 1
    yyyy,endmon,endday = doy2ymd(int(year),int(enddoy))
    year = "{0:04}".format(int(yyyy))
    end.text = year+"-"+"{0:02}".format(endmon)+"-"+"{0:02}".format(endday)+ " "+"{0:02}".format(counth)+":"+"{0:02}".format(countmin)+":"+"{0:02}".format(endtime)

    tree.write(filename)

def change_inp_lri(filename,year,doy,lridir):
    doy = int(doy)+1
    doy = "{0:03}".format(int(doy))
    yyyy,mon,day = doy2ymd(int(year),int(doy))
    tree = et.parse(filename)
    root = tree.getroot();
    inputs = root.find("inputs")
    lriinp = inputs.find("lri")
    lriinp.text = lridir+"lri_"+year+"{0:02}".format(mon)+"{0:02}".format(day)
    tree.write(filename)

def change_inp_orb(filename,year,doy,Cdir,Ddir):
    doy = "{0:03}".format(int(doy))
    tree = et.parse(filename)
    root = tree.getroot();
    inputs = root.find("inputs")
    orbinp = inputs.find("orb")
    orbinp.text = Cdir+doy+"/"+"orb_leo"+"     "+Ddir+doy+"/"+"orb_leo"
    tree.write(filename)

def change_out_lri(filename,year,doy):
    doy = "{0:03}".format(int(doy))
    yyyy,mon,day = doy2ymd(int(year),int(doy))
    tree = et.parse(filename)
    root = tree.getroot()
    outputs = root.find("outputs")
    omcout = outputs.find("lriomc")
    omcout.text = "lri_omc_"+year+"{0:02}".format(mon)+"{0:02}".format(day)
    tree.write(filename)

def update_lricmp_xml(filename,year,doy,hour,minute,second,sslength):
    lridir = "/dat01/leitingting/hjj_data/"+year+"/leo/grace-fo/leolri/"
    orbCdir = "/dat01/leitingting/proc/grac/2020/"
    orbDdir = "/dat01/leitingting/proc/grad/2020/"
    change_time(filename,year,doy,hour,minute,second,sslength)
    change_inp_lri(filename,year,doy,lridir)
    change_inp_orb(filename,year,doy,orbCdir,orbDdir)
    change_out_lri(filename,year,doy)
    

def main_iter():
    year = argv[1]
    doy = "{0:03}".format(int(argv[2]))
    hour = "{0:02}".format(int(argv[3]))
    minute = "{0:02}".format(int(argv[4]))
    second = "{0:02}".format(int(argv[5]))
    seslen =  argv[6]  
    leo = argv[7] 
    yy = year[2:]
    
    update_lricmp_xml("./gnut-lri.xml",year,doy,hour,minute,second,seslen)
if __name__  == "__main__":
    main_iter()
