#-*- coding:utf-8 -*-

import os
import shutil
import ftplib
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as et
from sys import argv

cddis = "cddis.gsfc.nasa.gov"
cf_stdfile = r"D:\gnss-data\orblsq-data\cf"
file_table_std = r"D:\gnss-data\orblsq-data\file_table"
xml_std = r"D:\gnss-data\orblsq-data\gnut-orblsq.xml"
snx_std = r"D:\gnss-data\orblsq-data\igs17P1930.snx"
jpl_std = r"D:\gnss-data\orblsq-data\jpleph_de405"
oi_std = r"..\oi.log"

def copyfile(srcfile,destfile):
    """
    srcfile: source file name(string)
    destfile: destination file name(string)
    """
    if (not os.path.exists(srcfile)):
        print(srcfile+"is not exist!")
    else:
        if (os.path.exists(destfile)):
                os.remove(destfile)
        shutil.copyfile(srcfile,destfile)
        print(srcfile+ "-->" + destfile)

def movefiles(files,directory):
    """
    files: needed moving files
    directory: destination directory
    """
    for file in files:
        if (not os.path.exists(file)):
                continue
        shutil.move(file,directory)

def ics_panda2gnut(ics_filename,doy,begin=0,end=0):
        """
        """
        ics_header=[
        "## Header Of Initial Control State Of Satellite\n",
        "%Satellite        = GNS  L    G  30\n",
        "%PRN  = G01 G02 G05 G06 G07 G08 G09 G10 ++ \n",
        "%PRN  = G11 G12 G13 G14 G15 G16 G17 G18 G19 G20 ++\n",
        "%PRN  = G21 G22 G23 G24 G25 G26 G27 G28 G29 G30 G31 G32 ++\n",
        "%Time  = GPS  57761  0.000  57762  0.000\n",
        "## End Of Header      \n"
        ]

        if (begin==0):
                begin = 57754
        if (end ==0):
                end = 57755
        ics_header[-2] = ics_header[-2].replace("57761",str(begin+int(doy)-1))
        ics_header[-2] = ics_header[-2].replace("57762",str(end+int(doy)-1))
        txt=[]
        with open(ics_filename,"r") as ics_f:
                for temp_line in ics_f:
                        txt.append(temp_line)
        txt = txt[2:]
        txt[0:0] = ics_header[:] 
        with open(ics_filename,"w",newline="\n") as ics_f:
                for temp_line in txt:
                        temp_line = temp_line.replace("D+","e+")
                        temp_line = temp_line.replace("D-","e-")
                        ics_f.writelines(temp_line)

def ics_gnut2panda(ics_filename,doy):
        """
        """
        panda_header=[
        "PANDA ICS-file, created by presrif\n",
        "Ref.Time :    57754        0.000  GPST      \n"
        ]
        panda_header[1] = panda_header[1].replace("57754",str(57754+int(doy)-1))
        txt=[]
        with open(ics_filename,"r") as ics_f:
                flag = False
                for temp_line in ics_f:
                        if(not flag and temp_line[:3]=="G01" ):
                                flag = True
                        if (flag):
                                txt.append(temp_line)
        
        txt[0:0] = panda_header[:]
        with open(ics_filename,"w",newline="\n") as ics_f:
                for temp_line in txt:
                        ics_f.writelines(temp_line)



def icsleo_panda2gnut(ics_filename,doy,begin=0,end=0):
        """
        """
        ics_header=[
        "## Header Of Initial Control State Of Satellite\n",
        "%Satellite        = LEO  60\n",
        "%PRN = P201 P202 P203 P204 P205 P206 P207 P208 P209 P210 ++\n",
        "%PRN = P211 P212 P213 P214 P215 P216 P217 P218 P219 P220 ++\n",
		"%PRN = P221 P222 P223 P224 P225 P226 P227 P228 P229 P230 ++\n",
		"%PRN = P231 P231 P233 P234 P235 P236 P237 P238 P239 P240 ++\n",
		"%PRN = P241 P242 P243 P244 P245 P246 P247 P248 P249 P250 ++\n",
		"%PRN = P251 P252 P253 P254 P255 P256 P257 P258 P259 P260 ++\n",
        "%Time  = GPS  58119  0.000  58120  0.000\n",
        "## End Of Header      \n"
        ]

        if (begin==0):
                begin = 57754
        if (end ==0):
                end = 57755
        ics_header[-2] = ics_header[-2].replace("58119",str(begin+int(doy)-1))
        ics_header[-2] = ics_header[-2].replace("58120",str(end+int(doy)-1))
        txt=[]
        with open(ics_filename,"r") as ics_f:
                for temp_line in ics_f:
                        txt.append(temp_line)
        txt = txt[2:]
        txt[0:0] = ics_header[:] 
        with open(ics_filename,"w",newline="\n") as ics_f:
                for temp_line in txt:
                        temp_line = temp_line.replace("D+","e+")
                        temp_line = temp_line.replace("D-","e-")
                        ics_f.writelines(temp_line)

def icsleo_gnut2panda(ics_filename,doy):
        """
        """
        panda_header=[
        "PANDA ICS-file, created by sp3orb\n",
        "Ref.Time :    57754        0.000  GPST      \n"
        ]
        panda_header[1] = panda_header[1].replace("57754",str(57754+int(doy)-1))
        txt=[]
        with open(ics_filename,"r") as ics_f:
                flag = False
                for temp_line in ics_f:
                        if(not flag and temp_line[:3]=="P201" ):
                                flag = True
                        if (flag):
                                txt.append(temp_line)
        
        txt[0:0] = panda_header[:]
        with open(ics_filename,"w",newline="\n") as ics_f:
                for temp_line in txt:
                        ics_f.writelines(temp_line)
						

def oi_panda2gnut(oi_filename,doy):
        """
        oi_filename:panda oi file name[string]
        doy:day of year[int]
        """
        oi_header=[
        "Sat Group: GPS",
        "Sat Type: G ",
        "Sat List: 30",
        "  G01  G02  G05  G06  G07  G08  G09  G10  G11  G12",
        "  G13  G14  G15  G16  G17  G18  G19  G20  G21  G22",
        "  G23  G24  G25  G26  G27  G28  G29  G30  G31  G32",
        "Intege Control: true  11  60  300",
        "Nequ: 36",
        "Nepo: 298",
        "Beg Time: 57760 84900",
        "End Time: 57762 1500",
        "Ref Time: 57761 0",
        "END OF HEAD"]
        oi_header[-4]= oi_header[-4].replace("57760",str(57753+int(doy)-1))
        oi_header[-3]= oi_header[-3].replace("57762",str(57755+int(doy)-1))
        oi_header[-2]= oi_header[-2].replace("57761",str(57754+int(doy)-1))
        txt=[]
        for header in oi_header:
                txt.append(header+"\n")
        with open(oi_filename,"r") as oi_f:
                flag = False
                for temp_line in oi_f:
                        if (not flag and temp_line[0]=="*"):
                                flag = True
                        if flag:
                                txt.append(temp_line)
        txt=txt[:-2]
        txt.append("END OF FILE")
        with open(oi_filename,"w",newline="\n") as oi_f:
                for temp_line in txt:
                        oi_f.writelines(temp_line)

def update_orbxml(orb_filename,site_list,year,doy):
    """
    """
   # DOMTree = xml.dom.minidom.parse("orb_filename")
   # collection = DOMTree.documentElement
   # config = collection.getElementsByTagName("config")[0]
   # gen = config.getElementsByTagName("gen")[0]
   # beg = gen.getElementsByTagName("beg")[0]
   # end = gen.getElementsByTagName("end")[0]
   # rec = gen.getElementsByTagName("rec")[0]
   # input_file = config.getElementsByTagName("inputs")[0]
   # rinexo = input_file.getElementsByTagName("rinexo")[0]
    tree = et.parse(orb_filename)
    root = tree.getroot()
    gen = root.find("gen")
    beg = gen.find("beg")
    end = gen.find("end")
    rec = gen.find("rec") 
    par = root.find("parameters")
    rec_str ="\n"
    rinexo_str ="\n"
    count = 0
    for site in site_list:
        new_Sitepar = et.Element("STA",{"sigCLK":"9000","sigPOS":"0.1_0.1_0.1","sigZTD":"0.201"})
        new_Sitepar.set("ID",site.upper())
        new_Sitepar.tail ="\n	   "
        par.append(new_Sitepar)
        rec_str +=site.upper() +" "
        rinexo_str += site+doy+"0."+year[2:]+"o"+" "
        count +=1
        if (count ==10):
            rec_str+="\n"
            rinexo_str += "\n"
            count=0
    rec_str+="\n"
    rinexo_str+="\n"
    rec.text = rec_str
    beg.text = year+"-"+"01"+"-"+doy[1:]+ " 00:00:00"
    end.text = year+"-"+"01"+"-"+doy[1:]+" 23:55:00"

    inputs = root.find("inputs")
    rinexo = inputs.find("rinexo")
    rinexo.text = rinexo_str
    rinexc = inputs.find("rinexc")
    rinexc.text = "clk_"+year+doy+" "+"rec_"+year+doy
    ics = inputs.find("ics")
    ics.text = "ics_"+year+doy

    tree.write(orb_filename)

    
gnut_orb="gnut-orblsq"
panda_oi="oi"
panda_prepare = "prepare"

def main():

        #get days
        dir = os.getcwd()
        dir = dir.split("\\")
        dir =dir[-1]
        year = dir[:4] 
        doy = dir[4:7] 
        gps_day = year+doy
        result_files=[]

        #save file
        if (os.path.exists("./save")):
                shutil.rmtree("./save")
        os.mkdir("./save")
        icsfile = "ics_" + gps_day
        clkfile = "clk_" + gps_day
        recfile = "rec_" + gps_day
        result_files.clear()
        result_files.append(icsfile)
        result_files.append(clkfile)
        result_files.append(recfile)
        movefiles(result_files,"./save")
        if (os.path.exists("./log")):
                shutil.rmtree("./log_tb")
                shutil.move("./log","./log_tb")

        ##panda prepare
        preapare_cmd ="cf -time "+ year+ " " + doy +" 00 00 86400 -intv 300 -list site_list -rnxo -scan -snx igs17P1930.snx -sysids G -orb brd -clk brd" 
        copyfile(snx_std,"./igs17P1930.snx")
        copyfile(cf_stdfile,"./cf")
        copyfile(file_table_std,"./file_table")
        print("begin prepare")
        os.system(panda_prepare+" " + preapare_cmd)

        #save ics clk file
        shutil.copyfile(icsfile,"ics_initial")
        shutil.copyfile(clkfile,"clk_initial")

        # run oi 
        print("begin oi")
        copyfile(jpl_std,"./jpleph_de405")
        oi_cmd = panda_oi+ " cf_net " + icsfile  +  " > oi.log"
        os.system(oi_cmd)

        # change oi.log icsfile
        oi_panda2gnut("oi.log",doy)

        ## generate gnut-orblsq xml
        copyfile(xml_std,"./gnut-orblsq.xml")
        site_list = []
        with open("site_list","r") as site_f:
                for site in site_f:
                        site_list.append(site.strip())
        update_orbxml("./gnut-orblsq.xml",site_list,year,doy)

        # run gnut-orblsq
        ics_panda2gnut(icsfile,doy)
        print("prepare finish!")
        return
        #return 
       
        orb_cmd = gnut_orb + " -x ./gnut-orblsq.xml > test.log"
        print("being orb!!")
        os.system(orb_cmd)

        # save 1
        copyfile(icsfile,"ics_gnut1")
        copyfile(clkfile,"clk_gnut1")
        copyfile(recfile,"rec_gnut1")
        copyfile("orb_resfile","orb_resfile_1")

        ## oi orb 2
        ics_gnut2panda(icsfile,doy)
        #copyfile(icsfile+"TEST",icsfile)
        print("begin oi 2!")
        os.system(oi_cmd)
        oi_panda2gnut("oi.log",doy)
        ics_panda2gnut(icsfile,doy)
        print("begin orb 2!")
        os.system(orb_cmd)

        #save 2
        copyfile(icsfile,"ics_gnut2")
        copyfile(clkfile,"clk_gnut2")
        copyfile(recfile,"rec_gnut2")
        copyfile("orb_resfile","orb_resfile_2")

        # twice is enough
        #return
        # oi orb 3
        ics_gnut2panda(icsfile+"TEST",doy)
        copyfile(icsfile+"TEST",icsfile)
        print("begin oi 3!")
        os.system(oi_cmd)
        oi_panda2gnut("oi.log",doy)
        ics_panda2gnut(icsfile,doy)
        print("begin orb 3!")
        os.system(orb_cmd)

        # save 3
        copyfile(icsfile,"ics_gnut3")
        copyfile(clkfile,"clk_gnut3")
        copyfile(recfile,"rec_gnut3")
        copyfile("orb_resfile","orb_resfile_3")




if __name__ == "__main__":
        dir_base="D:\gnss-data\orblsq-data"
        dir = dir_base+r"\\"+argv[1]
        if (len(argv) >2):
                gnut_orb = argv[2]
        os.chdir(dir)
        print(os.getcwd())
        #site_list = []
        #copyfile(xml_std,"./gnut-orblsq.xml")
        #with open("site_list","r") as site_f:
        #        for site in site_f:
        #                site_list.append(site.strip())
        #update_orbxml("./gnut-orblsq.xml",site_list,"2017","008")
        main()
