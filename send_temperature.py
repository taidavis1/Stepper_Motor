import sys
import json
import os
import glob
import time
import socket
import datetime
import socket
import pymysql
#### Read Temperature ###########
def read_file():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    directory = '/sys/bus/w1/devices/'
    folder = glob.glob(directory + '28*')[0]
    file = folder + '/w1_slave'
    temperature_data = open(file, 'r')
    lines = temperature_data.readlines()
    temperature_data.close()
    return lines

def read_temp():
    tempf = 0
    lines = read_file()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_file()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        tempf = round(temp_f)
        return tempf
        
#### Connection With Amazon Web Services ############

data = 0

class DB_Connection:
    
    def __init__(self , host , user , password , port , db):
        
        self.host = host
        
        self.user = user
        
        self.password = password
        
        self.port = port
        
        self.db = db
                
        self.cursor = pymysql.connect(
            host= self.host,
            user= self.user,
            password= self.password,
            port=self.port,
            db= self.db,
            autocommit=True
        ).cursor(pymysql.cursors.DictCursor)
            
        self.connect = pymysql.connect(
            host= self.host,
            user= self.user,
            password= self.password,
            port=self.port,
            db= self.db,
            autocommit=True
        )
        
    def create_table(self):
    
        self.cursor.execute("CREATE TABLE IF NOT EXISTS temperature_data(id INT PRIMARY KEY AUTO_INCREMENT NOT NULL , temperature INT NOT NULL, timestream VARCHAR(32) NOT NULL)")
                           
    def send_data(self , date):
                        
        temp = read_temp()
                
        message = {
                
            'temperature' : temp,
            'time' : date
        }
        
        print("Message To Insert: " , message)
        
        self.cursor.execute("SELECT * FROM temperature_data WHERE temperature = %s" , (temp))
        
        check = self.cursor.fetchone()
        
        print(check)
        
        time.sleep(1)
            
        if check:
            
            print("Data already in the database! ")
            
            self.cursor.execute("UPDATE temperature_data SET timestream = %s WHERE temperature = %s " , (date , temp) )
                                                                        
            print("Update The time successfully")
            
        else:
        
            self.cursor.execute("INSERT INTO temperature_data (timestream , temperature) VALUES (%s , %s) ", (date , temp))
                                            
            print("Successfuly Publish")
            
        time.sleep(5)

    def data_proccessing(self , date):
                                                    
        self.cursor.execute("SELECT temperature FROM temperature_data WHERE timestream = %s" , (date))
        
        data = self.cursor.fetchone()
                
        return data
    
    def send_to_motor(self , data):
        
        IP = '*****'

        PORT = 5000

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.sendto(bytes(json.dumps(data) , encoding= 'utf-8'),(IP,PORT))
        
        print("Send Successfully !")
        
        time.sleep(5)
        
##################################################################

if __name__ == '__main__':
            
    db = DB_Connection(
        host= '*****',
        user= '*****',
        password= '*****',
        port=3306,
        db='*****'
    )
    
    db.create_table()
        
    try:
        
        while True:
            
            date = datetime.datetime.now()
                                                   
            db.send_data(date)
            
            time.sleep(2)
                                    
            a = db.data_proccessing(date)
            
            print("Data Sent to Motor: " , a)
            
            db.send_to_motor(data = a)
                        
            time.sleep(5)
                                                                                
    except KeyboardInterrupt:
        print("End Program! \n")
        db.connect.close()
        exit(1)
