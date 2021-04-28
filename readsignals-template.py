import platform
import sys
#ensure you have downloaded the correct library for your biosignal plux sensor.
#this script was placed inside the same folder as the library.
sys.path.append("plux.so")
import plux
import paho.mqtt.client as mqtt

class NewDevice(plux.SignalsDev):    
    
    def __init__(self, address): 
        plux.MemoryDev.__init__(address)        
        self.time = 0
        self.frequency = 0        

    def onRawFrame(self, nSeq, data):  # onRawFrame takes three arguments        
        if nSeq % 2000 == 0:
            print(nSeq)
            #data returns as an array with two indexes, the first one contains the ADC
            signal = data[0]
            
            #interpolate data using r.i. equation
            ri = signal/2**16
            print(ri)          
            
            #transmit data
            client.publish("biosignal",ri, qos=1)
            
            
            #trigger TRUE through MQTT for syncing with the game.
        if nSeq/self.frequency > self.time:
            client.disconnect()
            return True
        return False

# example routines

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Error connecting with code: " + str(rc))

def on_message(client, userdata, msg):
    print("Topic: " + msg.topic + " Data: " + msg.payload.decode("utf-8"))

#connect to MQTT once
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set("username","password")
print("will connect to hive")
#change the port to the appropriate number. The port is the second parameter below.
client.connect("hostname",8883)
print("connected to MQTT")
#Assumes you are using biosignal as the topic.
client.subscribe("biosignal")
#Test your topic
#client.publish("biosignal", "data incoming")
client.loop_start()

def deviceAcquisition(address, time, freq, code):  # time acquisition for each frequency
    """
    Example acquisition.
    #Address: 00:07:80:4D:2B:08
    #PI IP: 192.168.0.139

    Supported channel number codes:
    {1 channel - 0x01, 2 channels - 0x03, 3 channels - 0x07
    4 channels - 0x0F, 5 channels - 0x1F, 6 channels - 0x3F
    7 channels - 0x7F, 8 channels - 0xFF}

    Maximum acquisition frequencies for number of channels:
    1 channel - 8000, 2 channels - 5000, 3 channels - 4000
    4 channels - 3000, 5 channels - 3000, 6 channels - 2000
    7 channels - 2000, 8 channels - 2000
    """
    device = NewDevice(address)
    device.time = time  # interval of acquisition in seconds
    device.frequency = freq
    device.start(device.frequency, code, 16)
    device.loop()  # calls device.onRawFrame until it returns True
    device.stop()
    device.close()


deviceAcquisition("Bluetooth Address", 20, 1000, 0x01)
