import socket
import time
import RPi.GPIO as GPIO
import json

class Stepper_Motor:
    
    def __init__(self , in1 , in2 , in3 , in4):
        
        self.in1 = in1
        
        self.in2 = in2
        
        self.in3 = in3
        
        self.in4 = in4
        
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        
    def cleanup(self):
        GPIO.cleanup()
        
    def receive_data(self):
        
        IP = "10.33.59.139"
        PORT = 5000
        sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
        sock.bind((IP,PORT))
        data, addr = sock.recvfrom(1024)
        print("Receive: " , data.decode('utf-8'))
        data_re = json.loads(data)
        return data_re
        
    def rotate(self , data):
        motor_step_counter = 0
        step_sequence = [
            [1,0,0,1],
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1]
        ]
        
        motor_pins = [self.in1 , self.in2 , self.in3 , self.in4]
        step_count = (int(data['temperature'])/5.625)*(64)
        print("Rotate Clockwise: " , step_count)
        i = 0
        for i in range(int(step_count)):
            for pin in range(0, len(motor_pins)):
                GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
            motor_step_counter = (motor_step_counter + 1) % 8

            time.sleep(0.002)
                
    def __str__(self):
            
        return f" Pin1: {self.in1} , Pin2: {self.in2} , Pin3: {self.in3} , Pin4: {self.in4}"
    
    
if __name__ == '__main__':
    
    # Setup Stepper motor
    
    motor = Stepper_Motor(17,18,27,22)
    
    motor.setup()

    try:
        
        while True:
                    
            data = motor.receive_data()
            
            motor.rotate(data=data)
            
            print("Finish Rotate")
        
    except KeyboardInterrupt:
        
        print("End Program! \n")
        
        motor.cleanup()
        
        exit(1)