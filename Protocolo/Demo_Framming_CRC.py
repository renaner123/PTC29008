#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import poller
from Framming import Enquadramento
import serial
import sys

ser = serial.Serial('/dev/pts/3', 9600, timeout=5)  
cb = Enquadramento(ser)

  
msg = "a^dd~~^]}}^~}}~~csf"
quadro = bytearray([0,50,255])
for see in msg:
    quadro.append(ord(see))
cb.envia_byte(quadro)

print("Informação estufada", cb.temp[1:len(cb.temp)-3])
print("Crc gerado: ",cb.temp[len(cb.temp)-3:len(cb.temp)-1])
print("Mensagem enquadrada: ", cb.temp[0:len(cb.temp)])




    
    







  
  
                  

                  
