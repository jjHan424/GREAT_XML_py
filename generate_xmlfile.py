#-*- coding-f:utf-8 -*-

import PodBatch_win 
import xml.etree.ElementTree as et
from PodItera_Batch import doy2ymd
from PodItera_Batch import ymd2gpsweek
from PodItera_Batch import ymd2gpsweekday
from sys import argv

def att_panda2gnut(att_filename,satname,doy):

    att_header=[
    "%% Header of attitude data for LEO satellite\n",
    "% Satellite      SWARM-A\n",
    "% Start time     57754      0.0\n",
    "% End time       57756  86399.0\n",
    "% Time interval  1\n",
    "%% End of Header \n"
    ]

    txt=[]
    counttime = 0
    countint1 = 0
    countint2 = 0
    counthead = 0
    startflag = "%% Start"
    with open(att_filename,"r") as att_f:
            for temp_line in att_f:    
                    if(counttime == 0):
                            if(temp_line[3:9] == "Header"):
                                    return "is ok"                
                    counttime = counttime + 1
                    if(counthead == counttime - 1 ):
                        countint2 = 0
                    else:
                        countint2 = 1

                    if(startflag in temp_line):
                        print(temp_line)
                        time_beg = temp_line[28:]                           
                    if(temp_line[0] == " " and countint1 == 0):
                        timeintv1 = temp_line
                        print(temp_line)
                        countint1 = countint1 + 1
                        countint2 = 1
                        counthead = counttime
                    if(temp_line[0] == " " and countint2 == 0):
                        timeintv2 = temp_line
                        print(temp_line)
                        countint2 = 1
                    txt.append(temp_line)
    txt = txt[counthead:]
    #sat num
    att_header[0] =  "%% Header of attitude data for LEO satellite\n"
    att_header[1] = ["% Satellite     " +satname.upper() + "\n"]
    mjd_beg = time_beg.split()[0]
    sec_beg = time_beg.split()[1]
    mjd_end = time_beg.split()[2]
    sec_end = time_beg.split()[3]

  
    # intv1 = timeintv1.split()[1]
    # intv2 = timeintv2.split()[1]
    intv = 1.0


    att_header[2]=["% Start time    "+str(mjd_beg) + "   " + str(sec_beg) + "    \n"]
    att_header[3]=["% End time      "+str(mjd_end) + "   " + str(sec_end) + "    \n"]
    att_header[4]=["% Time interval "+str(intv)+"  \n"]
    att_header[5]=["%% End of Header \n" ] 

    txt[0:0] = att_header[:] 
    with open(att_filename,"w",newline="\n") as att_f:
            for temp_line in txt:
                    att_f.writelines(temp_line)

def change_time(filename,year,doy,hour,minute,second,sslength):
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    sslength = int(sslength)
    yyyy,mon,day = doy2ymd(int(year),int(doy))
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

    enddoy = int(doy) + countday
    yyyy,endmon,endday = doy2ymd(int(year),int(enddoy))
    year = "{0:04}".format(int(yyyy))
    end.text = year+"-"+"{0:02}".format(endmon)+"-"+"{0:02}".format(endday)+ " "+"{0:02}".format(counth)+":"+"{0:02}".format(countmin)+":"+"{0:02}".format(endtime)

    tree.write(filename)

def change_force(filename,site_list_long,dra,cust,atmosphere):
    
    tree = et.parse(filename)
    root = tree.getroot()
    force = root.find("force_model")
    for i in force.iter("atmosphere"):
        if ( "model" in i.attrib):
            i.attrib["model"] = atmosphere
        i.text = dra

    for i in force.iter("customer"):
        i.text = cust

    tree.write(filename)

def change_obs_rec(filename,year,doy,site_list_leo,obsdir): 
    
    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()
    gen = root.find("gen")

    rinexo_str ="\n"
    recleo_str = "\n"
    count = 0
    for leo in site_list_leo:
        recleo_str += "       " + leo
        rinexo_str += "       " + obsdir + leo + doy + "0." + year[2:] + "o" + "\n       " + obsdir + leo + doy1 + "0." + year[2:] + "o" + "\n       " + obsdir + leo + doy2 + "0." + year[2:] + "o"
        count += 1
        if (count == 10):
            recleo_str += "\n"
            rinexo_str += "\n"
            count = 0
		
    rinexo_str+="\n"
    recleo_str+="\n"
    for i in gen.iter("rec"):
        if ( "type" in i.attrib and i.attrib["type"] == "leo"):
            rec_leo = i
            rec_leo.text = recleo_str
    inputs = root.find("inputs")
    rinexo = inputs.find("rinexo")
    rinexo.text = rinexo_str
    tree.write(filename)



def change_inp_nav_3day(filename,year,doy,key,navdir):
    yy = year[2:]  
    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    brd = inputs.find("rinexn")
    if key == "brdc":
        brd1 = navdir + key + doy + "0." + yy +"n\n   "
        brd2 = navdir + key + doy1 + "0." + yy +"n\n   "
        brd3 = navdir + key + doy2 + "0." + yy +"n\n   "
    elif key == "brdm":
        brd1 = navdir + key + doy + "0." + yy +"p\n   "
        brd2 = navdir + key + doy1 + "0." + yy +"p\n   "
        brd3 = navdir + key + doy2 + "0." + yy +"p\n   "

    brd.text = "\n   " + brd1 + brd2 + brd3   
    tree.write(filename)


def change_inp_att_3day(filename,year,doy,site_leo_long,attdir):

    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    attitude = inputs.find("attitude")
    attitude.text = "\n    "
    for i in site_leo_long:
        att1 = attdir +"att_"+year[2:]+doy+"_"+i+"\n    "
        att2 = attdir +"att_"+year[2:]+doy1+"_"+i+"\n    "
        att3 = attdir +"att_"+year[2:]+doy2+"_"+i+"\n    "
        attitude.text = attitude.text + att1 + att2 + att3 
    tree.write(filename)
    
def change_inp_acc_3day(filename,year,doy,site_leo_long,accdir):

    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    accelerometer = inputs.find("accelerometer")
    accelerometer.text = "\n    "
    for i in site_leo_long:
        acc1 = accdir +"acc_"+year[2:]+doy+"_"+i+"\n    "
        acc2 = accdir +"acc_"+year[2:]+doy1+"_"+i+"\n    "
        acc3 = accdir +"acc_"+year[2:]+doy2+"_"+i+"\n    "
        accelerometer.text = accelerometer.text + acc1 + acc2 + acc3 
    tree.write(filename)

def change_inp_kbr_3day(filename,year,doy,kbrdir):

    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy1 = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    attitude = inputs.find("kbr")
    yyyy1, mon1, day1 = doy2ymd(int(year), int(doy))
    kbr1 = kbrdir+"kbr_"+year+"{0:02}".format(mon1)+"{0:02}".format(day1)+"\n"

    yyyy2, mon2, day2 = doy2ymd(int(year), int(doy)+1)
    kbr2 =  kbrdir+"kbr_"+year+"{0:02}".format(mon2)+"{0:02}".format(day2)+"\n"

    yyyy3, mon3, day3 = doy2ymd(int(year), int(doy)+2)
    kbr3 =  kbrdir+"kbr_"+year+"{0:02}".format(mon3)+"{0:02}".format(day3)+"\n"
    attitude.text = "\n    "+kbr1+kbr2+kbr3
    tree.write(filename)
    
def change_inp_lri_3day(filename,year,doy,lridir):

    day1 = int(doy) + 1
    day2 = int(doy) + 2
    doy1 = "{0:03}".format(int(doy))
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    attitude = inputs.find("lri")
    yyyy1, mon1, day1 = doy2ymd(int(year), int(doy))
    lri1 = lridir+"lri_"+year+"{0:02}".format(mon1)+"{0:02}".format(day1)+"\n"

    yyyy2, mon2, day2 = doy2ymd(int(year), int(doy)+1)
    lri2 =  lridir+"lri_"+year+"{0:02}".format(mon2)+"{0:02}".format(day2)+"\n"

    yyyy3, mon3, day3 = doy2ymd(int(year), int(doy)+2)
    lri3 =  lridir+"lri_"+year+"{0:02}".format(mon3)+"{0:02}".format(day3)+"\n"
    attitude.text = "\n    "+lri1+lri2+lri3
    tree.write(filename)


def change_inp_pod_3day(filename,year,doy,podtyep,poddir):

    doy = "{0:03}".format(int(doy))
    yyyy,mon,day = doy2ymd(int(year),int(doy))
    tree = et.parse(filename)
    root = tree.getroot()

    week = ymd2gpsweekday(int(year),mon,day)
    week1 = ymd2gpsweekday(int(year),mon,day+1)
    week2 = ymd2gpsweekday(int(year),mon,day+2)
    gbm1 = poddir+podtyep + str(week)+".sp3\n   "
    gbm2 = poddir+podtyep + str(week1)+".sp3\n   "
    gbm3 = poddir+podtyep + str(week2)+".sp3\n   "
    inputs = root.find("inputs")
    sp3 = inputs.find("sp3")
    sp3.text = "\n   " + gbm1 + gbm2 + gbm3
    tree.write(filename)



def change_inp_dcb_3day(filename,year,doy,dcbdir):

    yyyy,mon,day = doy2ymd(int(year),int(doy))
    doy = "{0:03}".format(int(doy))
    tree = et.parse(filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    dcb = inputs.find("biabern")
    dcb.text = "\n    " + dcbdir + "P1C1" + year[2:] + "{0:02}".format(mon) + ".DCB\n    "
    dcb.text = dcb.text + dcbdir + "P2C2" + year[2:] + "{0:02}".format(mon) + "_RINEX.DCB  "
    tree.write(filename)

    

def change_inp_clk_3day(filename,year,doy,podtyep,clkdir):

    doy = "{0:03}".format(int(doy))
    yyyy,mon,day = doy2ymd(int(year),int(doy))
    tree = et.parse(filename)
    root = tree.getroot()

    week = ymd2gpsweekday(int(year),mon,day)
    week1 = ymd2gpsweekday(int(year),mon,day+1)
    week2 = ymd2gpsweekday(int(year),mon,day+2)
    clk1 = clkdir+podtyep + str(week)+".clk\n   "
    clk2 = clkdir+podtyep + str(week1)+".clk\n   "
    clk3 = clkdir+podtyep + str(week2)+".clk\n   "
    if(podtyep == "igs"):
        clk1 = clkdir+podtyep + str(week)+".clk_30s\n   "
        clk2 = clkdir+podtyep + str(week1)+".clk_30s\n   "
        clk3 = clkdir+podtyep + str(week2)+".clk_30s\n   "

    inputs = root.find("inputs")
    rinexc = inputs.find("rinexc")
    rinexc.text = "\n      " + clk1 + "   "  + clk2 + "   "  + clk3 + "   " + "rec_" + year + doy+ " \n"
    tree.write(filename)	 



def update_turbedit_xml(tb_filename,year,doy,hour,minute,second,sslength,site_list_leo,obsdir,brddir):
    
    hournew = "{0:02}".format(int(hour) - 1)
    sslengthnew = str(int(sslength) + 3600)
    tree = et.parse(tb_filename)
    root = tree.getroot()
    gen = root.find("gen")
    rec = gen.find("rec")

    sites = "\n"
    count = 0

    for leo in site_list_leo:
        sites += "       " + leo+ "  "
        count += 1
        if (count == 10):
            sites += "\n"
            count = 0
    rec.text = sites
    tree.write(tb_filename)
    change_time(tb_filename,year,doy,hournew,minute,second,sslengthnew)
    change_obs_rec(tb_filename,year,doy,site_list_leo,obsdir)
    change_inp_nav_3day(tb_filename,year,doy,"brdc",brddir)


def update_sp3orb_xml(sp3orb_filename,year,doy,hour,minute,second,sslength,site_leo_long,dra,cust,atmosphere):

    change_time(sp3orb_filename,year,doy,hour,minute,second,sslength)
    change_force(sp3orb_filename,site_leo_long,dra,cust,atmosphere)
    tree = et.parse(sp3orb_filename)
    root = tree.getroot()
    day1=int(doy)+1
    day2=int(doy)+2
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))

	#ics file
    inputs = root.find("inputs")
    kin = inputs.find("sp3")
    kin.text = "  "
    for i in site_leo_long:
        kin.text = kin.text + "  kin_" + "{0:04}".format(int(year)) + "{0:03}".format(int(doy)) + "_" + i + "  " 
    #leoshort="graa"
    #site_leo_short=["graa"]
    #sp3dir = "/workfs/yjqin/data/leo/"+leoshort+"/pod/"+year+"/"
#
    #inputs = root.find("inputs")
    #kindata = inputs.find("sp3")
    #kindata.text = "   "
    #for i in site_leo_short:
    #    kindata.text = kindata.text + sp3dir + i + doy + "0.sp3"+"  "+ sp3dir + i + doy1 + "0.sp3"+"  "+ sp3dir + i + doy2 + "0.sp3"
   
    sp3orb = root.find("sp3orb")
    leo = sp3orb.find("sat")
    leo.text = "  "
    for i in site_leo_long:
        leo.text = leo.text + i.upper() + "  "

      
    tree.write(sp3orb_filename)

def update_sp3orb2_xml(sp3orb_filename,year,doy,hour,minute,second,sslength,site_leo_long,site_leo_short,dra,cust,atmosphere,poddir):

    change_time(sp3orb_filename,year,doy,hour,minute,second,sslength)
    change_force(sp3orb_filename,site_leo_long,dra,cust,atmosphere)
    tree = et.parse(sp3orb_filename)
    root = tree.getroot()
    day1=int(doy)+1
    day2=int(doy)+2
    doy1 = "{0:03}".format(int(day1))
    doy2 = "{0:03}".format(int(day2))

	#ics file
    
    sp3dir = poddir
#
    inputs = root.find("inputs")
    kindata = inputs.find("sp3")
    kindata.text = "   "
    for i in site_leo_short:
        kindata.text = kindata.text + sp3dir + i + doy + "0.sp3"+"  "+ sp3dir + i + doy1 + "0.sp3"+"  "+ sp3dir + i + doy2 + "0.sp3"
   
    sp3orb = root.find("sp3orb")
    leo = sp3orb.find("sat")
    leo.text = "  "
    for i in site_leo_long:
        leo.text = leo.text + i.upper() + "  "

      
    tree.write(sp3orb_filename)


def update_preedit_xml(ed_filename,year,doy,hour,minute,second,sslength,site_sat,navdir):

    change_time(ed_filename,year,doy,hour,minute,second,sslength)
    change_inp_nav_3day(ed_filename,year,doy,"brdc",navdir)
    tree = et.parse(ed_filename)
    root = tree.getroot()
    gps = root.find("gps")
    sat = gps.find("sat")
    sat.text = "  " + site_sat +"  "
    outputs = root.find("outputs")
    ics_out = outputs.find("ics")
    ics_out.text = "ics_"+year+doy+"_gps"
    tree.write(ed_filename)


def update_sp3orbnav_xml(sp3orb_filename,year,doy,hour,minute,second,sslength,site_sat,poddir):

    change_time(sp3orb_filename,year,doy,hour,minute,second,sslength)
    change_inp_pod_3day(sp3orb_filename,year,doy,"grm",poddir)
    tree = et.parse(sp3orb_filename)
    root = tree.getroot()
    gps = root.find("sp3orb")
    sat = gps.find("sat")
    sat.text = "  " + site_sat +"  "
    tree.write(sp3orb_filename)

def update_leo_geometric(geo_filename,site_list_leo,site_leo_long,year,doy,hour,minute,second,sslength,attdir,obsdir,poddir,dcbdir,list_sat,clkdir):
    
    hournew = "{0:02}".format(int(hour) - 1)
    sslengthnew = str(int(sslength) + 3600)
    change_time(geo_filename,year,doy,hournew,minute,second,sslengthnew)
    change_obs_rec(geo_filename,year,doy,site_list_leo,obsdir)
    change_inp_att_3day(geo_filename,year,doy,site_leo_long,attdir)
    change_inp_pod_3day(geo_filename,year,doy,"grm",poddir)
    change_inp_clk_3day(geo_filename,year,doy,"grm",clkdir)
    change_inp_dcb_3day(geo_filename,year,doy,dcbdir)
  
   
    tree = et.parse(geo_filename)
    root = tree.getroot()
    inputs = root.find("inputs")
    kin = inputs.find("sp3")
    for i in site_leo_long:
        kin.text = kin.text +"kin_"+"{0:04}".format(int(year))+"{0:03}".format(int(doy))+"_"+i+ "  "

    outputs = root.find("outputs")
    kin_out = outputs.find("sp3")
    kin_out.text = "   "
    for i in site_leo_long:
        kin_out.text = kin_out.text +"kin_"+"{0:04}".format(int(year))+"{0:03}".format(int(doy))+"_"+i+ "  "

    recclk_out = outputs.find("recclk")
    recclk_out.text = "   rec_"+"{0:04}".format(int(year))+"{0:03}".format(int(doy))+ "  "

    gps = root.find("gps")
    sat = gps.find("sat")
    sat.text = list_sat
    
    tree.write(geo_filename)

	
def update_oileo_xml(oi_filename,year,doy,hour,minute,second,sslength,site_leo_long,dra,cust,atmosphere,attdir,accdir):

    change_time(oi_filename,year,doy,hour,minute,second,sslength)
    change_force(oi_filename,site_leo_long,dra,cust,atmosphere)
    change_inp_att_3day(oi_filename,year,doy,site_leo_long,attdir)
    change_inp_acc_3day(oi_filename,year,doy,site_leo_long,accdir)

    tree = et.parse(oi_filename)
    root = tree.getroot()
 
    leos = root.find("LEO")
    leosat = leos.find("sat")
    leosat.text = "  "
    for i in site_leo_long:
        leosat.text = leosat.text + "   " + i.upper() + "  "
  
    tree.write(oi_filename)


def update_leoorbxml(orb_filename,site_list_leo,site_leo_long,year,doy,hour,minute,second,sslength,list_sat,obsdir,clkdir,attdir,dcbdir,kbrdir,lridir):
    
    change_time(orb_filename,year,doy,hour,minute,second,sslength)
    change_obs_rec(orb_filename,year,doy,site_list_leo,obsdir)
    change_inp_att_3day(orb_filename,year,doy,site_leo_long,attdir)
    change_inp_clk_3day(orb_filename,year,doy,"grm",clkdir)
    change_inp_dcb_3day(orb_filename,year,doy,dcbdir)
    change_inp_kbr_3day(orb_filename,year,doy,kbrdir)
    change_inp_lri_3day(orb_filename,year,doy,lridir)

    tree = et.parse(orb_filename)
    root = tree.getroot()
	
    outputs = root.find("outputs")
    recclk_out = outputs.find("recclk")
    recclk_out.text = "   rec_" + year + doy + "  "

    gps = root.find("gps")
    sat = gps.find("sat")
    sat.text = list_sat

    leos = root.find("LEO")
    leosat = leos.find("sat")
    leosat.text = "   "
    for i in site_leo_long:
        leosat.text = leosat.text + i.upper()+ "  "

    tree.write(orb_filename)


def update_orbsp3_xml(orbsp3_filename,year,doy,hour,minute,second,sslength,site_leo_long,intvsecond,trs):

    change_time(orbsp3_filename,year,doy,hour,minute,second,sslength)
    
    tree = et.parse(orbsp3_filename)
    root = tree.getroot()
    orbsp3 = root.find("orbsp3")
    sat = orbsp3.find("sat")
    intv = orbsp3.find("intv")
    frame = orbsp3.find("frame")
    sat.text = "  "
    for i in site_leo_long:
        sat.text = sat.text + "   " + i.upper() + "  "
    intv.text = intvsecond
    frame.text = trs

    tree.write(orbsp3_filename)
    
    


def update_orbdifover_xml(orbdif_filename,year,doy,hour,minute,second,sslength,site_leo_long,site_leo_short):

    hour = int(hour)
    day1 = int(doy) + 1
    doy1 = "{0:03}".format(day1)
    change_time(orbdif_filename,year,doy1,hour,minute,second,sslength)
    tree = et.parse(orbdif_filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    kindata = inputs.find("kin")
    kindata.text = " leo-sp3 "
    
    leos = root.find("orbdifleo")
    leosat = leos.find("leo")
    leosat.text = "  "
    for i in site_leo_long:
        leosat.text =leosat.text + "   " + i.upper() + "  "
    
    tree.write(orbdif_filename)

def update_orbdif_xml(orbdif_filename,year,doy,hour,minute,second,sslength,site_leo_long,site_leo_short,sp3dir):
    
    
    change_time(orbdif_filename,year,doy,hour,minute,second,sslength)
    print(sp3dir)
    tree = et.parse(orbdif_filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    kindata = inputs.find("sp3")
    kindata.text = "   "
    for i in site_leo_short:
        kindata.text = kindata.text + sp3dir + i + doy + "0.sp3  "
   
    leos = root.find("orbdifleo")
    leosat = leos.find("leo")
    leosat.text = "  "
    for i in site_leo_long:
        leosat.text =leosat.text + "   " + i.upper() + "  "
  
    tree.write(orbdif_filename)

def update_orbdifK_xml(orbdif_filename,year,doy,hour,minute,second,sslength,site_leo_long,site_leo_short,sp3dir):
    
    
    change_time(orbdif_filename,year,doy,hour,minute,second,sslength)
    day = int(doy) - 1
    doy1 = "{0:03}".format(day)
    tree = et.parse(orbdif_filename)
    root = tree.getroot()

    inputs = root.find("inputs")
    kin = inputs.find("sp3")

    for i in site_leo_long:
        kin.text ="  kin_" + "{0:04}".format(int(year)) + "{0:03}".format(int(doy1)) + "_" + i + "  " 
    
   
    leos = root.find("orbdifleo")
    leosat = leos.find("leo")
    leosat.text = "  "
    for i in site_leo_long:
        leosat.text =leosat.text + "   " + i.upper() + "  "
  
    tree.write(orbdif_filename)



def update_ambchk(amb_filename,site_list_leo,year,doy,hour,minute,second,sslength,list_sat):
    
    
    change_time(amb_filename,year,doy,hour,minute,second,sslength)
    
    tree = et.parse(amb_filename)
    root = tree.getroot()
    gen = root.find("gen")
    rec = gen.find("rec")

    sites = "\n"
    count = 0

    for leo in site_list_leo:
        sites += "       " + leo+ "  "
        count += 1
        if (count == 10):
            sites += "\n"
            count = 0
    rec.text = sites
	#time 
    
    tree.write(amb_filename)


def update_ambfixml(amb_filename,site_list_leo,year,doy,hour,minute,second,sslength,list_sat,obsdir,dcbdir):
    
    
    change_time(amb_filename,year,doy,hour,minute,second,sslength)
    change_obs_rec(amb_filename,year,doy,site_list_leo,obsdir)
    change_inp_dcb_3day(amb_filename,year,doy,dcbdir)

    tree = et.parse(amb_filename)
    root = tree.getroot() 
    inputs = root.find("inputs")

    recover = inputs.find("recover")
    recover.text = "   resfile_temp_"+year+doy+ "  "


    gen = root.find("gen")
    rec = gen.find("rec")

    sites = "\n"
    count = 0

    for leo in site_list_leo:
        sites += "       " + leo+ "  "
        count += 1
        if (count == 10):
            sites += "\n"
            count = 0
    rec.text = sites


    tree.write(amb_filename)

def update_editresxml(editres_filename,site_list_leo,year,doy,hour,minute,second,sslength,short,jump,bad):
    
    tree = et.parse(editres_filename)
    root = tree.getroot()
 
    inputs = root.find("inputs")

    recover=inputs.find("recover")
    recover.text = "   resfile_temp_"+year+doy+ "  "
    sites = "\n"
    amb=inputs.find("ambflag")
    for leo in site_list_leo:
        sites += "  ./log_tb/"+leo+doy+"0."+year[2:]+"o.log"
    amb.text = sites


    editres=root.find("editres")
    shortstr=editres.find("short_elisp")
    shortstr.text=short

    jumpstr=editres.find("jump_elisp")
    jumpstr.text=jump

    badstr=editres.find("bad_elisp")
    badstr.text=bad

    tree.write(editres_filename)






def generate_Sitelistleo(sign,num):
    f=open('site_list_leo', 'w')
    for i in range(1,num+1):
        site_leos = " " + sign + "2" + "{0:02}".format(i) 
        f.write(site_leos+"\n")

    f.close()
	

def main():
    if (len(argv) < 3):
        print("argv is year doy")
        return 
    year = argv[1]
    doy = argv[2]
    site_list = []
    # read site list
    with open("site_list","r") as site_file:
        for i in site_file:
            site_list.append(i.strip())

   # read site leo
    site_list_leo = []
    with open("site_list_leo","r") as site_file:
        for i in site_file:
            site_list_leo.append(i.strip())

    
    #generate_Sitelistleo("P",60)
    #update_combineorbxml("gnut-orblsq.xml",site_list,site_list_leo,year,doy)
    #update_oileo_xml("gnut-oi_leo.xml",year,doy)
    #update_oixml("gnut-oi_nav.xml",year,doy)

if __name__ == "__main__":
    main()
    






