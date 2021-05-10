from Layer import Layer_Use
import serial
from tun import Tun

if __name__ == "__main__":
    ser = serial.Serial('/dev/pts/3', 9600, timeout=4)   #porta serial que será monitorada pelo poller
    tun = Tun("tun1","10.0.0.2","10.0.0.1",mask="255.255.255.252",mtu=1500,qlen=4)

    Projeto = Layer_Use(ser,tun,0)
    
