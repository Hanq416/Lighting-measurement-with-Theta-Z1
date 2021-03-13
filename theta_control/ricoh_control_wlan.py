# -*- coding: utf-8 -*-
#Hankun Li 08/15/2020

print('*****************************************************************************************\n')
print('Copyright (c) 2021 Hankun Li\n')
print('\
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.')
print('\n*****************************************************************************************\n\n')
print('Connect the Theta via WLAN\n')

import json
import requests
import os
from time import time, sleep

class Z1HdrFormatter(object):

    # theta Z1 camera value DO NOT CHANGE #
    aperture_range = ['2.1','3.5','5.6']
    ss_range = ['0.00004','0.00005','0.0000625','0.00008','0.0001','0.000125',
                '0.00015625','0.0002','0.00025','0.0003125','0.0004','0.0005',
                '0.000625','0.0008','0.001','0.00125','0.0015625','0.002',
                '0.0025','0.003125','0.004','0.005','0.00625','0.008','0.01',
                '0.0125','0.01666666','0.02','0.025','0.03333333','0.04',
                '0.05','0.06666666','0.07692307','0.1','0.125','0.16666666',
                '0.2','0.25','0.33333333','0.4','0.5','0.625','0.76923076','1',
                '1.3','1.6','2','2.5','3.2','4','5','6','8','10','13','15',
                '20','25','30','60']
    iso_range = ['80','100','125','160','200','250','320','400','500','640','800','1000','1250',
                 '1600','2000','2500','3200','4000','5000','6400']
    yn_range = ['Y','N', 'y', 'n','yes','no', 'Yes', 'No', 'YES', 'NO']
    y_range = ['Y', 'y','yes','Yes','YES']
    opt = [ "aperture", "_colorTemperature", "iso", "shutterSpeed"]
    # camera value end #

    def __init__(self, cct, shuttervolume, workspace_path):
        self.cct = cct
        self.sv = shuttervolume
        self.wp = workspace_path

    @staticmethod
    def initial_a():
        info = {'name': 'camera.setOptions','parameters':
                {'options': {'captureMode': 'image','_function': 'normal'}}}
        return info

    def initial_b(self):
        if self.cct not in range(2500,10001):
            print ('Err[1]: input CCT is out of range (2500 to 10000 kelvin)!\n')
            exit()
        info = {'name': 'camera.setOptions','parameters': {'options': {'exposureProgram': 1,
                                                                       '_imageStitching': 'none',
                                                                       '_shutterVolume': self.sv,
                                                                       'whiteBalance': '_colorTemperature',
                                                                       '_colorTemperature': int(self.cct)}}}
        return info

    @staticmethod
    def set_options(f, ss, iso):
        fsi = {'aperture': str(f), 'shutterSpeed': str(ss), 'iso': str(iso)}
        info = {"name": "camera.setOptions","parameters": {"options": fsi}}
        return info

    def get_options(self): #debug usage
        info = {"name": "camera.getOptions","parameters":{"optionNames": self.opt}}
        return info

    @staticmethod
    def input_c(rg, msg):
        while True:
            ans = input(msg)
            if ans in rg:
                return ans
            else:
                print('Wrong input! please try again. \n')
                print(rg) #debug


    def config(self, num):
        msg1 = 'input aperture size for # %d LDR image.\n' %num
        msg2 = 'input shutter speed for # %d LDR image.\n' %num
        msg3 = 'input film speed (iso) for # %d LDR image.\n' %num
        f = self.input_c(self.aperture_range, msg1)
        ss = self.input_c(self.ss_range, msg2)
        iso = self.input_c(self.iso_range, msg3)
        print('config of LDR # %d: f-number: %s, shutter speed: %s, iso: %s. \n' %(num, f, ss, iso))
        temp = [f,ss,iso]
        return temp
        
    def schedule_gen(self):
        msg1 = 'create a new schedule(Yes) or using saved schedule(No)? [Y/N]\n'
        sc = self.input_c(self.yn_range, msg1)
        if sc in self.y_range:
            msg2 = 'Workload of LDR images range(1 to 35)\n'
            srgt = list(range(1,36))
            srg = [str(g) for g in srgt]
            num = int(self.input_c(srg, msg2))
            ldrs = [num]
            for i in range (1,(num+1)):
                fsi = self.config(i)
                ldrs.append(fsi)
            msg3 = 'do you want to save the schedule? \n'
            ans3 = self.input_c(self.yn_range, msg3)
            if ans3 in self.y_range:
                for j in ldrs:
                    print(str(j) + '\n')
                fn = input('input the name of schedule \n')
                fnp = self.wp + '/' + fn
                if os.path.exists(fnp):
                    msg4 = 'file already exists, overwrite it? [Y/N]\n'
                    ans4 = self.input_c(self.yn_range, msg4)
                    if ans4 in self.y_range:
                        fi = open(fnp, 'w+')
                        for j in ldrs:
                            if type(j) == list:
                                fi.write('%s#%s#%s' %(j[0],j[1],j[2]) + '\n')
                        fi.close()
                    else:
                        print('schedule saving skipped\n')
                else:
                    fi = open(fnp, 'a+')
                    for j in ldrs:
                        if type(j) == list:
                            fi.write('%s#%s#%s' %(j[0],j[1],j[2]) + '\n')
                    fi.close()
        else:
            while True:
                print('Saved LDR schedules in the work path: \n')
                for sp in os.listdir(self.wp):
                    print(sp)
                sleep(1)
                scn = input('\nInput the name saved LDRi schedule!\n')
                sc = self.wp + '/' + scn
                if not os.path.exists(sc):
                    print('wrong input! file not exists, try agian or press [ctrl + c] to exit\n')
                    continue
                break
            ldrs = []
            f = open(sc, 'r')
            lines = f.readlines()
            f.close()
            ldrs.append(len(lines))
            print('schedule loaded!')
            for line in lines:
                line = line.strip('\n')
                print(line) #debug
                ct = 0
                for o in range(0,len(line)):
                    if line[o] == '#':
                        if ct == 0:
                            m1 = o
                        elif ct == 1:
                            m2 = o
                        else:
                            break
                        ct += 1
                st = [line[0:m1], line[m1+1:m2], line[m2+1:len(line)]]
                ldrs.append(st)
        return ldrs



class Z1Request(object):

    def __init__(self, address):
        self.adr = address

    @staticmethod
    def response_code(resp):
        try:
            code = resp.status_code
            return code
        except Exception as err:
            print(err)

    def getinfo(self):
        try:
            response = requests.get(self.adr + '/osc/info', timeout = 2)
            if self.response_code(response) == 200:
                jr = response.json()
                return json.dumps(jr, indent = 4, sort_keys = True)
            else:
                print('Error code: ', self.response_code(response))
                print('Error! check the reference of error code\n')
                return 0
        except Exception as err:
            print(err)
            return 0

    def check_capture_status(self, cid):
        info = {"id": str(cid)}
        try:
            response = requests.post(self.adr + '/osc/commands/status', json = info, timeout = 2)
            if self.response_code(response) == 200:
                jr = response.json()
                # print(jr) #debug
                if jr['state'] == 'done':
                    return 1
                else:
                    return 0
            else:
                print('Error code: ', self.response_code(response))
                print('Error! check the reference of error code\n')
                return 2
        except Exception as err:
            print(err)
            return 2

    def execute_post(self, info):
        response = requests.post(self.adr + '/osc/commands/execute', json = info, timeout = 3)
        if self.response_code(response) == 200:
            return 1
        else:
            print('Error code: ', self.response_code(response))
            return 0

    def capture_img(self):
        info = {"name": "camera.takePicture"}
        while True:
            try:
                response = requests.post(self.adr + '/osc/commands/execute', json = info, timeout = 3)
                if self.response_code(response) == 200:
                    jr = response.json()
                    return jr['id']
                else:
                    print('[capture] Error code: ', self.response_code(response))
            except Exception as err:
                print(err)
                return

    def execute_callback(self, info):
        response = requests.post(self.adr + '/osc/commands/execute', json = info, timeout = 3)
        if self.response_code(response) == 200:
            jr = response.json()
            return json.dumps(jr, indent=4, sort_keys=True)
        else:
            print('Error code: ', self.response_code(response))
            return 'error!'


# main machine input:
theta_adr = str(input('input theta z1 WLAN address [type 0 to use the default: [192.168.1.1]\n'))
if theta_adr == '0':
    theta_adr = 'http://192.168.1.1'
else:
    theta_adr = 'http://' + theta_adr
work_path = str(input('input the path of workspace for z1 HDR \n'))
# work_path = 'H:/FAST_HDRI/workspace_z1'

while True:
    try:
        cct1 = int(input('input CCT of target scene! range [2500-10000 Kelvin]\n'))
    except Exception as err:
        print(err)
        continue
    cct = round(cct1/100)*100
    if cct not in range(2500,10001):
        print('wrong input!\n')
    else:
        break

#program start:

req = Z1Request(theta_adr)
z1f = Z1HdrFormatter(cct,20,work_path)

#check connection
z1_info = req.getinfo()
if z1_info is not 0:
    print('Camera connected! \n\n')
    # print('Camera information: \n', z1_info)
else:
    print('Camera not connected, check your WLAN settings\n')
    exit()

# create LDRi schedule:
sch = z1f.schedule_gen()

# camera initialization:
ca = req.execute_post(z1f.initial_a())
cb = req.execute_post(z1f.initial_b())
if ca == 1 and cb == 1:
    print('initialization: OK\n')
else:
    print('initialization failed, check reference \n')
    exit()

# auto bracket start

t1 = time()
for i in range(1, int(sch[0])+1):
    rc = req.execute_post(z1f.set_options(sch[i][0],sch[i][1],sch[i][2]))
    sleep(0.4)
    if rc == 1:
        # print(req.execute_callback(z1f.get_options())) #debug
        pass
    else:
        print('Unexpected errors, Hint: check the LDR schedule and camera connection\n')
        exit(0)
    zid = req.capture_img()
    if zid != '':
        if float(sch[i][1]) >= 1:
            sleep(float(sch[i][1]) + 0.5)
        else:
            sleep(0.5)
    else:
        print('can not taking pictures!\n')
        exit()
    # ct = 0 #debug
    while True:
        status = req.check_capture_status(zid)
        if  status == 1:
            break
        elif status == 0:
            sleep(0.5) #debug
            # print('counter', ct) #debug
            # ct += 1 #debug
            continue
        else:
            print('unexpected error!\n')
            exit(-1)

# auto-bracket finished, summary
t2 = time()
ts = t2 - t1
print('Work finished! time consumption: %.2f secs\n' %ts)
sleep(1)

input('Press any key to exit!\n')
exit(0)




                
            
                
                
            
        
        
    
