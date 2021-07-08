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
import qi

def scan_QRcode():
    import cv2
    import numpy as np
    import random
    import io
    import csv
    import datetime

    print("Stiamo dentro lo scanner!")

    ID = random.randint(1,5)
    image_name = "qrcode"+str(ID)+".png"

    inputImage = cv2.imread(image_name)
    
    qrDecoder = cv2.QRCodeDetector()
    
    # Detect and decode the qrcode
    data,bbox,rectifiedImage = qrDecoder.detectAndDecode(inputImage)

    if len(data)>0:
        print("Decoded Data : {}".format(data))
        data = data.split(", ")

        # prima bisogna leggere il file e vedere se gia presente
        with open('HRI_DB_patients.csv') as f:
            csvFile = csv.reader(f)
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
            ID_list.append(ID)
            # Ci salviamo anche l'ID su global_vars:
            with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
                reader = csv.reader(f)
                lines_glob = list(reader)
            lines_glob[1][0] = str(ID)
            born = data[2]
            views = 1
        else:
            print ("Paziente trovato!")
            views = str(int(lines[patientFound][4])+1)            
            lines[patientFound][4] = views
            # Ci salviamo anche l'ID su global_vars:
            with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
                reader = csv.reader(f)
                lines_glob = list(reader)
            lines_glob[1][0] = str(patientFound)
            born = lines[patientFound][3]
        
        patient_distance = float(lines_glob[1][5])

        # Compute age
        d = datetime.datetime.strptime(born, '%Y-%m-%d')
        today = datetime.date.today()
        age = today.year - d.year
        if today.month < d.month or (today.month == d.month and today.day < d.day):
            age -= 1

        lines_glob[1][3] = str(age)
        lines_glob[1][4] = str(views)
        
        with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w') as f:
            writer_glob = csv.writer(f)
            writer_glob.writerows(lines_glob)

        # Sort .csv file 
        ID_list = sorted(ID_list)
        lines_new = []
        lines_new.append(lines[0])
        for elem in ID_list:
            for j in range(len(lines)):
                if (lines[j][0] == str(elem)):
                    lines_new.append(lines[j])
        
        with open('HRI_DB_patients.csv','w') as f:
            writer = csv.writer(f)
            writer.writerows(lines_new)  

        # Posizionare Pepper alla giusta distanza dal paziente
        views = int(views)
        if (views >= 3):
            # friend
            if (patient_distance > 0.5):
                d = patient_distance - 0.5
                im.robot.forward(d)
        elif (views == 2):
            # acquaintance
            if (patient_distance > 0.8):
                d = patient_distance - 0.8
                im.robot.forward(d)
        elif (views == 1):
            # stranger
            if (patient_distance > 1):
                d = patient_distance - 1
                im.robot.forward(d)
        
    else:
        print("QR Code not detected")


def starting_steps():
    import csv

    im.init()
    a = im.ask('welcome', timeout=1)

    q = ('language')
    a = im.ask(q, timeout=3)

    if( (a=='italiano') or (a=='english')):
        if(a == 'italiano'):
            im.setProfile(['*', '*', 'it', '*'])
            lang = 'italiano'
        elif(a == 'english'):
            im.setProfile(['*', '*', 'en', '*'])
            lang = 'english'

        with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
            reader_glob = csv.reader(f)
            lines_glob = list(reader_glob)
        lines_glob[1][2] = lang

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

            if (a == 'payment'):
                q = ('payment')
                a = im.ask(q)
            elif (a == 'toilet'):
                q = ('toilet')
                a = im.ask(q)
            elif(a == 'timeout'):
                im.execute('wait_answer')
            im.init()

        elif(a == 'timeout'):
            im.execute('wait_answer')
            im.init()
        
        with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w') as f:
            writer_glob = csv.writer(f)
            writer_glob.writerows(lines_glob)

    elif(a == 'timeout'):
        im.execute('wait_answer')
        im.init()

def book_visit():
    import csv
    import datetime

    today = datetime.date.today()

    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader_glob = csv.reader(f)
        lines_glob = list(reader_glob)
    ID_patient = lines_glob[1][0]
    age_patient = lines_glob[1][3]
    views = int(lines_glob[1][4])

    lang = lines_glob[1][2]
    if(lang == 'italiano'):
        im.setProfile(['*', '*', 'it', '*'])
    elif(lang == 'english'):
        im.setProfile(['*', '*', 'en', '*'])
    
    if (views >= 3):
        im.ask('welcome_friend')
        q = ('choose_date')
        a1 = im.ask(q)
    elif (views == 2):
        q = ('choose_date')
        a1 = im.ask(q)
    elif (views == 1):
        q = ('choose_date_stranger')
        a1 = im.ask(q)


    if (a1 == 'next_week'):
        date = today + datetime.timedelta(days=7)
    elif (a1 == 'next_month'):
        date = today + datetime.timedelta(days=30)
    elif (a1 == 'timeout'):
        im.execute('wait_answer')
        im.init()
    
    if (a1 != 'timeout'):
        q = ('choose_department')
        a2 = im.ask(q)
        if (a2 == 'cardiology'):
            dep = 'cardiology'
            im.ask('visit_booked')
        elif (a2 == 'orthopedics'):
            dep = 'orthopedics'
            im.ask('visit_booked')
        elif (a2 == 'timeout'):
            im.execute('wait_answer')
            im.init()
    
        if (a2 != 'timeout'):
            with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv') as f:
                reader = csv.reader(f)
                lines = list(reader)
            line = [ID_patient, date.strftime("%Y-%m-%d"), dep]
            lines.append(line)

            with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv','w') as f:    
                writer = csv.writer(f)
                writer.writerows(lines)

    im.init()


def check_examination():
    import csv
    import datetime

    today = datetime.date.today()

    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader_glob = csv.reader(f)
        lines_glob = list(reader_glob)
    ID_patient = lines_glob[1][0]
    age_patient = lines_glob[1][3]
    views = int(lines_glob[1][4])

    lang = lines_glob[1][2]
    if(lang == 'italiano'):
        im.setProfile(['*', '*', 'it', '*'])
    elif(lang == 'english'):
        im.setProfile(['*', '*', 'en', '*'])
    
    if (views >= 3):
        im.ask('welcome_friend')
    
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv') as f:
        reader = csv.reader(f)
        lines = list(reader)

    visitFound = False

    for i in range(len(lines)):
        if (lines[i][0] == ID_patient):
            date = datetime.datetime.strptime(lines[i][1], '%Y-%m-%d')
            if(date.year == today.year and date.month == today.month and date.day == today.day):
                visitFound = i
                
                q = ('visit_confirmed_'+lines[i][2])
                a = im.ask(q)

                with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
                    reader_glob = csv.reader(f)
                    lines_glob = list(reader_glob)
                lines_glob[1][6] = lines[i][2]

                with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv', 'w') as f:
                    writer_glob = csv.writer(f)
                    writer_glob.writerows(lines_glob)
    
    if(visitFound == False):
        if (views >= 3):
            q = ('no_visit_friend')
            a = im.ask(q)
        elif (views >= 1):
            q = ('no_visit')
            a = im.ask(q)
        
        im.init()

    new_lines = []
    new_lines.append(lines[0])
    for j in range(1,len(lines)):
        if (j != visitFound):
            new_lines.append(lines[j])

    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'HRI_DB_appointments.csv','w') as f:
        writer = csv.writer(f)
        writer.writerows(new_lines)

def indicate_direction():
    import csv

    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader = csv.reader(f)
        lines_glob = list(reader)
    
    if (lines_glob[1][6] == 'cardiology'):
        q = ('indicate_dir_left')
        im.ask(q)
    elif (lines_glob[1][6] == 'orthopedics'):
        q = ('indicate_dir_right')
        im.ask(q)

    im.init()

if __name__ == "__main__":
    import cv2
    import csv

    pip = os.getenv('PEPPER_IP')
    pport = 9559
    url = "tcp://" + pip + ":" + str(pport)

    app = qi.Application(["App", "--qi-url=" + url ])
    app.start()
    session = app.session
    memory_service=app.session.service("ALMemory")
    tts_service = session.service("ALTextToSpeech")
    motion_service = session.service("ALMotion")
    sonarValueList = ["Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
                    "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"] # sonar memory keys
    sonarValues =  memory_service.getListData(sonarValueList)
    sonarValues[0] = 2.0 # front

    # while the distance is >= 2.0, Pepper does not see the patient
    # when the distance is < 2.0, Pepper sees the patient
    while (sonarValues[0] >= 2.0):
        sonarValues =  memory_service.getListData(sonarValueList)
        if (sonarValues[0] == 0.0 or sonarValues[0] == None):
            sonarValues[0] = 2.0
        patient_distance = sonarValues[0]
    
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader = csv.reader(f)
        lines_glob = list(reader)
    lines_glob[1][5] = str(patient_distance)
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w') as f:
        writer_glob = csv.writer(f)
        writer_glob.writerows(lines_glob) 
    
    mws = ModimWSClient()

    # local execution
    mws.setDemoPathAuto(__file__)
    # remote execution
    # mws.setDemoPath('<ABSOLUTE_DEMO_PATH_ON_REMOTE_SERVER>')

    mws.run_interaction(starting_steps)

    # Controlliamo se c'e' un'operazione da effettuare 
    # e quindi se dobbiamo scansionare un CF - qrcode
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader = csv.reader(f)
        lines_glob = list(reader)
    if (lines_glob[1][1] == 'book' or lines_glob[1][1] == 'examination'):
        mws.run_interaction(scan_QRcode)
    
    # Settiamo volume e velocita' in base all'eta' del paziente
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader = csv.reader(f)
        lines_glob = list(reader)
    age_patient = lines_glob[1][3]
    if (int(age_patient) > 75):
        tts_service.setVolume(1.7)
        tts_service.setParameter("speed", 80)
    elif (int(age_patient) > 60):
        tts_service.setVolume(1.2)
        tts_service.setParameter("speed", 90)
    
    
    if (lines_glob[1][1] == 'book'):
        mws.run_interaction(book_visit)
    elif (lines_glob[1][1] == 'examination'):
        mws.run_interaction(check_examination)

    # Resettiamo a None le global variables
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv') as f:
        reader = csv.reader(f)
        lines_glob = list(reader)
    if (lines_glob[1][6] != 'None'):
        motion_service.wakeUp()

        if (lines_glob[1][6] == 'cardiology'):
            # move head and shoulder in the left direction
            # to indicate the way to the patient
            names  = ["HeadYaw", "LShoulderRoll"]
            angles = [math.pi/2.0, math.pi/2.2]
            times  = [2.0, 2.0]
            isAbsolute = True
            motion_service.angleInterpolation(names, angles, times, isAbsolute)
        elif (lines_glob[1][6] == 'orthopedics'):
            # move head and shoulder in the right direction
            # to indicate the way to the patient
            names  = ["HeadYaw", "RShoulderRoll"]
            angles = [-math.pi/2.0, -math.pi/2.2]
            times  = [2.0, 2.0]
            isAbsolute = True
            motion_service.angleInterpolation(names, angles, times, isAbsolute)

        time.sleep(1.0)

        mws.run_interaction(indicate_direction)

        # Go to rest position
        motion_service.rest()
    
    lines_glob[1] = ['None', 'None', 'None', 'None', 'None', 'None', 'None']
    with open(os.getenv('MODIM_HOME')+'/src/GUI/'+'global_vars.csv','w') as f:
        writer_glob = csv.writer(f)
        writer_glob.writerows(lines_glob)

    end()