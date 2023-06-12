# Reviewed and revised for MSO5X
import os
import sys
import time
import re
import pyvisa

verNum = "v1.03, Feb 18, 2023"
mainAuthor = "Masashi Nogawa @ Qorvo"
debug = 0

license = '''\
Qorvo "Double Pulse Testing on Tektronix MSO5 Oscilloscope Example" Software License Agreement
'''


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    lfile = os.path.dirname(sys.executable) + "\\LICENSE"
else:
    lfile = os.path.dirname(__file__) + "\\LICENSE"


if not os.path.isfile(lfile):

  with open(lfile, "w") as f:
    f.write(license)

  print("First use notice:\nPlease read the license file at \"" + lfile + "\".\n")

  sys.exit(1)

########################################################

args = sys.argv

########################################################
rm = pyvisa.ResourceManager()
# print(rm)

list = rm.list_resources()
#list = ('TCPIP0::192.168.0.101::inst0::INSTR', 'ASRL4::INSTR', 'ASRL5::INSTR', 'ASRL7::INSTR')

########################################################
use = f"""

Usage-1:
  {args[0]}        => no parameter to list equipment connected

Usage-2:
  {args[0]} <id/IP> <Ton1> <Toff1> <Ton2> <Toff2> <Ton3>
    <id/IP>:
             Integer "0" to "99" as an ID of your MSO-Scope, use "{args[0]}" without parameters for available IDs
         OR
             IP address in the format of 00.00.00.00 of your MSO-Scope
    <Ton1> : First pulse length, in us (micro-second)
    <Toff1>: Interval between the 1st and 2nd pulses, in us (micro-second)
    <Ton2> : Second pulse length, in us (micro-second)
    <Toff2>: [Optional] Interval between the 2nd and 3rd pulses, in us (micro-second)
    <Ton3> : [Optional] Second pulse length, in us (micro-second)

  Example-1: ""> {args[0]} 0 10 1 3""
      Selecting your MSO-Scope at <id> = 0,
      1st ON pulse (to charge coil current) is 10us,
      wait for 1us between 1st and 2nd ON pulses,
      2nd ON pulse is 3us

  Example-2: ""> {args[0]} 192.168.9.99 45.2 1 2 1 3.5""
      Selecting your MSO-Scope at IP address 192.168.9.99,
      1st ON pulse (to charge coil current) is 45.2us,
      wait for 1us between 1st and 2nd ON pulses,
      2nd ON pulse is 2us,
      wait for another 1us between 1st and 2nd ON pulses,
      3rd ON pulse is 3.5us,

"""

########################################################
if len(args) == 1:
  msg = f"""
Double pulse test on MSO-Scope {verNum} (main coding by {mainAuthor})
"""
  print(msg)


  print("Following equipment found...")

  idx = 0
  for a in list:
    print(str(idx) + ":    " + a)
    idx += 1

  print("\nRun \"<prompt> " + args[0] + " <id> <Ton1> <Toff1> <Ton2> <Toff2> <Ton3>\"")
  print("\nIf your MSO-Scope is not listed, specify your MSO-Scope's IP address directly in below format:")
  print("Run \"<prompt> " + args[0] + " 00.00.00.00 <Ton1> <Toff1> <Ton2> <Toff2> <Ton3>\"")
  rm.close()
  sys.exit(0)

########################################################
if not((len(args) == 5) or (len(args) == 7)):
  msg = f"""
Error:  wrong parameters
"""
  if len(args) == 6:
    msg = f"""
Error: <Ton3> parameter is missing
  """
  print(msg + use)
  rm.close()
  sys.exit(1)

########################################################
pIP = re.compile('\d+\.\d+\.\d+.\d')
if pIP.match(args[1]):
  IPAddr = args[1]
  args[1] = "100"

########################################################
#if not(args[1].isdigit() and args[2].isdigit() and args[3].isdigit() and args[4].isdigit()):

def notNumber():
  msg = ""

  if not(args[1].isdigit()):
    msg += "\nERROR: 1st parameter should be an integer \"0\" to \"99\" or an IP address in dotted-decimal 00.00.00.00\n"

  msg += "\nERROR: 2nd/3rd/4th/5th/6th parameter(s) should be a number: integer \"0\" to \"99\", or floating \"99.9\", NO unit: \"us\", \"(us)\"\n"

  print(msg + use)
  rm.close()
  sys.exit(1)

if not(args[1].isdigit()):
  notNumber()

try:
  ton1 = round(float(args[2]),1)
except ValueError:
  notNumber()
try:
  tof1 = round(float(args[3]),1)
except ValueError:
  notNumber()
try:
  ton2 = round(float(args[4]),1)
except ValueError:
  notNumber()

if len(args) == 7:
  try:
    tof2 = round(float(args[5]),1)
  except ValueError:
    notNumber()
  try:
    ton3 = round(float(args[6]),1)
  except ValueError:
    notNumber()


########################################################
id   = int(args[1])

if ((id < 0) or (id >= len(list))) and (id != 100):
  msg = """
Error:  Equipment <id> is our of range, please specify one ID of below.
Error:  Or specify your MSO-Scope IP address at the 1st parameter.
"""
  print(msg)

  idx = 0
  for a in list:
    print(str(idx) + ":    " + a)
    idx += 1

  print("\nRun \"> " + args[0] + " <id/IP> <Ton1> <Toff1> <Ton2> <Toff2> <Ton3>\"")
  rm.close()
  sys.exit(1)


########################################################
if id == 100:
  print("Target MSO-Scope: IP address at " + IPAddr)
else:
  print("Target MSO-Scope: " + list[id])
print("1st Pulse: " + str(ton1) + "(us)")
print("1st OFF  : " + str(tof1) + "(us)")
print("2nd Pulse: " + str(ton2) + "(us)")
if len(args) == 7:
  print("2nd OFF  : " + str(tof2) + "(us)")
  print("3rd Pulse: " + str(ton3) + "(us)")

CSV = b'TIME,ARB\n'

c = 0
CSV += str(c).encode() + b'e-7,0\r\n'
c += 1
for i in range(int(ton1*10)):
  CSV += str(c).encode() + b'e-7,5\r\n'
  c += 1
for i in range(int(tof1*10)):
  CSV += str(c).encode() + b'e-7,0\r\n'
  c += 1
for i in range(int(ton2*10)):
  CSV += str(c).encode() + b'e-7,5\r\n'
  c += 1
if len(args) == 7:
  for i in range(int(tof2*10)):
    CSV += str(c).encode() + b'e-7,0\r\n'
    c += 1
  for i in range(int(ton3*10)):
    CSV += str(c).encode() + b'e-7,5\r\n'
    c += 1
CSV += str(c).encode() + b'e-7,0\r\n'
c += 1

if debug:
  print(CSV)
  rm.close()
  sys.exit(1)

########################################################
if id == 100:
  MsoScopeHandle = rm.open_resource("TCPIP::" + IPAddr)
else:
  MsoScopeHandle = rm.open_resource(list[id])

MsoScopeHandle.write('FileSystem:MKDir "c:/QorvoDPT"')
MsoScopeHandle.query("*OPC?")

print(MsoScopeHandle.query('*IDN?'))
#    print(MSO6.query('FILESystem:CWD?'))
#    print(MSO6.query('FileSystem:Dir?'))

msg = 'FileSystem:WriteFile "c:/QorvoDPT/pulse_data.csv", '

#    print(MSO6.query('FileSystem:Dir?'))
#print(MSO6.query('FileSystem:Dir?'))

MsoScopeHandle.write('AFG:Output:Mode OFF')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Output:State OFF')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('FileSystem:Delete "c:/QorvoDPT/pulse_data.csv"')
MsoScopeHandle.write_binary_values(msg, CSV, datatype='s')
MsoScopeHandle.query("*OPC?")

#    print(MSO6.query('FileSystem:Dir?'))

#MsoScopeHandle.write('AFG:Output:Load:Impedance Fifty')
#MsoScopeHandle.query("*OPC?")
#MSO6.write('AFG:Amplitude 3.3;:AFG:Offset 1.65')
#MsoScopeHandle.query("*OPC?")

MsoScopeHandle.write('AFG:OUTPut:LOAd:IMPEDance HIGHZ')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:LowLevel 0;:AFG:HighLevel 5')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Function Arb')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Arbitrary:Source "C:/QorvoDPT/pulse_data.csv"')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Output:Mode burst')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Burst:CCount 1')
MsoScopeHandle.query("*OPC?")
MsoScopeHandle.write('AFG:Period ' + str(c) + 'e-7')
MsoScopeHandle.query("*OPC?")

MsoScopeHandle.close()
rm.close()

print('\n>>>> Your MSO scope is ready to run, hit the "Burst" button in the AFG dialog.\n')

