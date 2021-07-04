'''
import datetime

date_time_str = '1970-05-19'

d = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

def age(person):
    today = datetime.date.today()
    years = today.year - person.year
    if today.month < person.month or (today.month == person.month and today.day < person.day):
        years -= 1
    return years

print(age(d))
'''

import sys
import os
import random
import cv2
import time
import numpy as np

sys.path.insert(0, os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')
import pepper_cmd
from pepper_cmd import *

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print ("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

# Set MODIM_IP to connnect to remote MODIM server

import ws_client
from ws_client import *


def scan_QRcode():
    import cv2
    import numpy as np
    import random
    import io
    import csv

    print("Stiamo dentro lo scanner!")

    ID = random.randint(1,4)
    image_name = "qrcode"+str(ID)+".png"

    inputImage = cv2.imread(image_name)
    
    qrDecoder = cv2.QRCodeDetector()
    
    # Detect and decode the qrcode
    data,bbox,rectifiedImage = qrDecoder.detectAndDecode(inputImage)

    if len(data)>0:
        print("Decoded Data : {}".format(data))
        data = data.split(", ")

        # prima bisogna leggere il file e vedere se gia presente
        csvFile = csv.reader(open('HRI_DB_patients.csv'))
        lines = list(csvFile)
        patientFound = False     
        ID_list = []   
        for i in range(len(lines)):
            if (i > 0): 
                if (lines[i][1] == data[0] and lines[i][2] == data[1] and lines[i][3] == data[2]):
                    patientFound = i
                ID_list.append(int(lines[i][0]))
        
        if (patientFound == False):
            print ("Nuovo paziente.")
            line = [str(ID),data[0],data[1],data[2],'1']
            lines.append(line)
            # Ci salviamo anche l'ID su global_vars:
            reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
            lines_glob = list(reader)
            lines_glob[1][0] = str(ID)
            writer_glob = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w'))
            writer_glob.writerows(lines_glob)
        else:
            print ("Paziente trovato!")
            lines[patientFound][4] = str(int(lines[patientFound][4])+1)
            # Ci salviamo anche l'ID su global_vars:
            reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
            lines_glob = list(reader)
            lines_glob[1][0] = str(patientFound)
            writer_glob = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w'))
            writer_glob.writerows(lines_glob)

        #writer = csv.writer(open('HRI_DB_patients.csv','w'))
        #writer.writerows(lines)

        # Sort .csv file 
        ID_list = sorted(ID_list)
        lines_new = []
        lines_new.append(lines[0])
        for elem in ID_list:
            for j in range(len(lines)):
                if (lines[j][0] == str(elem)):
                    lines_new.append(lines[j])
        
        writer = csv.writer(open('HRI_DB_patients.csv','w'))
        writer.writerows(lines_new)        
    else:
        print("QR Code not detected")


def welcome():
    import csv

    im.init()
    a = im.ask('welcome', timeout=1)

    q = ('language')
    a = im.ask(q, timeout=3)
    
    if(a == 'italiano'):
        im.setProfile(['*', '*', 'it', '*'])
        lang = 'italiano'
    elif(a == 'english'):
        im.setProfile(['*', '*', 'en', '*'])
        lang = 'english'

    reader_glob = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
    lines_glob = list(reader_glob)
    lines_glob[1][2] = lang

    if( (a=='italiano') or (a=='english')):
        im.execute(a)
        
        q = 'menu'
        a = im.ask(q)
        
        if(a == 'book'):
            #cf_required = True
            q = ('book')
            a = im.ask(q)
            q = ('codice_fisc')
            a = im.ask(q)
            # Ci salviamo il tipo di operazione da effettuare
            lines_glob[1][1] = 'book'
            
        elif(a == 'examination'):
            #cf_required = True
            q = ('examination')
            a = im.ask(q)
            q = ('codice_fisc')
            a = im.ask(q)
            # Ci salviamo il tipo di operazione da effettuare
            lines_glob[1][1] = 'examination'

        elif(a == 'info'):
            q = ('info')
            a = im.ask(q)
        
        if (a!='timeout'):
            im.execute('wait_answer')

        writer_glob = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w'))
        writer_glob.writerows(lines_glob)

        im.init()

    elif(a == 'timeout'):
        q = 'wait_answer'
        im.execute(q)

    im.init()

def book_visit():
    import csv
    import datetime

    im.init()

    today = datetime.date.today()

    reader_glob = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
    lines_glob = list(reader_glob)
    ID_patient = lines_glob[1][0]

    lang = lines_glob[1][2]
    if(lang == 'italiano'):
        im.setProfile(['*', '*', 'it', '*'])
    elif(lang == 'english'):
        im.setProfile(['*', '*', 'en', '*'])
    
    q = ('choose_date')
    a1 = im.ask(q)

    if (a1 == 'next_week'):
        date = today + datetime.timedelta(days=7)

    elif (a1 == 'next_month'):
        date = today + datetime.timedelta(days=30)
    
    q = ('choose_department')
    a2 = im.ask(q)
    if (a2 == 'cardiology'):
        dep = 'cardiology'
    elif (a2 == 'orthopedics'):
        dep = 'orthopedics'
    im.ask('visit_booked')
    
    reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv'))
    lines = list(reader)
    line = [ID_patient, date.strftime("%Y-%m-%d"), dep]
    lines.append(line)
    writer = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv','w'))
    writer.writerows(lines)

    im.init()


def check_examination():
    import csv
    import datetime

    im.init()

    today = datetime.date.today()

    reader_glob = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
    lines_glob = list(reader_glob)
    ID_patient = lines_glob[1][0]

    lang = lines_glob[1][2]
    if(lang == 'italiano'):
        im.setProfile(['*', '*', 'it', '*'])
    elif(lang == 'english'):
        im.setProfile(['*', '*', 'en', '*'])
    
    reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv'))
    lines = list(reader)

    visitFound = False

    for i in range(len(lines)):
        if (lines[i][0] == ID_patient):
            date = datetime.datetime.strptime(lines[i][1], '%Y-%m-%d')
            if(date.year == today.year and date.month == today.month and date.day == today.day):
                visitFound = i
                
                q = ('visit_confirmed_'+lines[i][2])
                a = im.ask(q)
    
    if(visitFound == False):
        q = ('no_visit')
        a = im.ask(q)

    new_lines = []
    new_lines.append(lines[0])
    for j in range(1,len(lines)):
        if (j != visitFound):
            new_lines.append(lines[j])

    writer = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv','w'))
    writer.writerows(new_lines)

    im.init()


if __name__ == "__main__":
    begin()

    import cv2
    import csv

    mws = ModimWSClient()

    # local execution
    mws.setDemoPathAuto(__file__)
    # remote execution
    # mws.setDemoPath('<ABSOLUTE_DEMO_PATH_ON_REMOTE_SERVER>')

    mws.run_interaction(welcome)

    # Controlliamo se c'e' un'operazione da effettuare 
    # e quindi se dobbiamo scansionare un CF - qrcode
    reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
    lines_glob = list(reader)
    print('Global vars before: ', lines_glob)
    if (lines_glob[1][1] == 'book' or lines_glob[1][1] == 'examination'):
        mws.run_interaction(scan_QRcode)
    
    if (lines_glob[1][1] == 'book'):
        mws.run_interaction(book_visit)
    elif (lines_glob[1][1] == 'examination'):
        mws.run_interaction(check_examination)

    # Resettiamo a None le global variables
    reader = csv.reader(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv'))
    lines_glob = list(reader)
    lines_glob[1] = ['None', 'None', 'None']
    writer_glob = csv.writer(open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w'))
    writer_glob.writerows(lines_glob)

    end()