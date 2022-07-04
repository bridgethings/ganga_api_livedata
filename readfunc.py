import os
import sys
import serial
import time
import json
import requests
from datetime import datetime
import pytz
import base64
import subprocess
import netifaces as ni
import logging
import logging.handlers

BODLOOKUP = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
TODMF = [1, 3.0, 2.75, 1.0, 2.0, 2.5, 2.0, 1.75, 1.5]
CODMF = [1, 6.0, 5.5, 1.0, 4.5, 4.25, 4.0, 3.5, 3.0]


def fix_bodbased(bod, tod, cod):
    BODLOOKUP = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
    TODMF = [1, 3.0, 2.75, 1.0, 2.0, 2.5, 2.0, 1.75, 1.5]
    CODMF = [1, 6.0, 5.5, 1.0, 4.5, 4.25, 4.0, 3.5, 3.0]
    # get Index
    if bod > 20:
        idx = 8
    else:
        idx = [i for i, val in enumerate(BODLOOKUP) if bod >= val][-1]

    # check ranges
    if idx in range(1, 8):
        todlb = BODLOOKUP[idx]*TODMF[idx]
        todub = BODLOOKUP[idx+1]*TODMF[idx]
        # calculate cod ranges
        codlb = BODLOOKUP[idx]*CODMF[idx]
        codub = BODLOOKUP[idx+1]*CODMF[idx]
        if not (tod > todlb and tod <= todub):
            tod = bod*TODMF[idx]
        if not (cod > codlb and cod <= codub):
            cod = bod*CODMF[idx]
        #print(bod, tod, cod)
        return bod, tod, cod
    else:
        if bod >= 20:
            idx = 8
            if tod < BODLOOKUP[idx]*TODMF[idx]:
                tod = bod*TODMF[idx]
            if cod < BODLOOKUP[idx]*CODMF[idx]:
                cod = bod*CODMF[idx]
    return bod, tod, cod


def fix_codbased(bod, tod, cod):
    # CODLOOKUP = [0, 3.0, 5.5, 8.0, 9.0, 13.0, 20.0, 35.0, 60.0]
    CODLOOKUP = [0, 3.0, 6.0, 8.0, 10.0, 14.0, 22.0, 40.0, 70.0]
    TODMF = [1, 3.0, 2.75, 1.0, 2.0, 2.5, 2.0, 1.75, 1.5]
    CODMF = [1, 6.0, 5.5, 5.0, 4.5, 4.25, 4.0, 3.5, 3.0]
    BODLOOKUP = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
    # get Index
    if cod > 70:
        idx = 8
    else:
        idx = [i for i, val in enumerate(CODLOOKUP) if cod >= val][-1]
        # print(idx)

    bod = cod/CODMF[idx]

    # check ranges
    if idx in range(1, 8):
        todlb = BODLOOKUP[idx]*TODMF[idx]
        todub = BODLOOKUP[idx+1]*TODMF[idx]
        # calculate cod ranges

        if not (tod > todlb and tod <= todub):
            tod = bod*TODMF[idx]
        #print(bod, tod, cod)
        return bod, tod, cod
    else:
        if cod >= 60:
            idx = 8
            bod = cod/CODMF[idx]
            if tod < BODLOOKUP[idx]*TODMF[idx]:
                tod = bod*TODMF[idx]
    return bod, tod, cod


def fix_todbased(bod, tod, cod):
    BODLOOKUP = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
    TODLOOKUP = [0, 1.5, 3.0, 4.0, 5.0, 7.0, 12.0, 20.0, 35.0]
    TODMF = [1, 3.0, 2.75, 2.5, 2.0, 2.5, 2.0, 1.75, 1.5]
    CODMF = [1, 6.0, 5.5, 1.0, 4.5, 4.25, 4.0, 3.5, 3.0]

    # get Index
    if tod > 35:
        idx = 8
    else:
        idx = [i for i, val in enumerate(TODLOOKUP) if tod >= val][-1]

    # check ranges
    if idx in range(1, 8):
        # calculate cod ranges
        bod = tod/TODMF[idx]
        cod = bod*CODMF[idx]
        #print(bod, tod, cod)
        return bod, tod, cod
    else:
        if cod >= 60:
            idx = 8
            bod = cod/CODMF[idx]
            if tod < BODLOOKUP[idx]*TODMF[idx]:
                tod = bod*TODMF[idx]
    return bod, tod, cod


def checkRanges(bod, tod, cod):
    bod = float(bod)
    tod = float(tod)
    cod = float(cod)
    idx = 0

    if bod < 0.5 and cod < 0.5 and tod < 0.5:
        return 0.5, 0.5, 0.5
    elif bod >= 0.5 and cod >= 0.5 and tod >= 0.5:
        return fix_bodbased(bod, tod, cod)
    elif bod >= 0.5 and (cod < 0.5 or tod < 0.5):
        print("fixing based on bod")
        return fix_bodbased(bod, tod, cod)
    elif cod >= 0.5 and (bod < 0.5 or tod < 0.5):
        print("fixing based on cod")
        return fix_codbased(bod, tod, cod)
    elif tod >= 0.5 and (bod < 0.5 or cod < 0.5):
        return fix_todbased(bod, tod, cod)


def validate(bod, tod, cod):
    if bod != None and tod != None and cod != None:
        return checkRanges(bod, tod, cod)

    if bod is None:
        if tod is None:
            if cod is None:
                return "bdl", "bdl", "bdl"
            else:
                CODVAL = [a*b for a, b in zip(BODLOOKUP, CODMF)]
                idx = [i for i, val in enumerate(CODVAL) if cod >= val][-1]
                tod = BODLOOKUP[idx]*TODMF[idx]
                bod = BODLOOKUP[idx]
                return bod, tod, cod
        else:
            TODVAL = [a*b for a, b in zip(BODLOOKUP, TODMF)]
            idx = [i for i, val in enumerate(TODVAL) if tod >= val][-1]
            bod = BODLOOKUP[idx]
            if cod is None:
                cod = BODLOOKUP[idx]*CODMF[idx]
            return bod, tod, cod
    else:
        if tod is None:
            idx = [i for i, val in enumerate(BODLOOKUP) if bod >= val][-1]
            tod = BODLOOKUP[idx]*TODMF[idx]
        if cod is None:
            idx = [i for i, val in enumerate(BODLOOKUP) if bod >= val][-1]
            tod = BODLOOKUP[idx]*CODMF[idx]
        return bod, tod, cod


def read_data():
    ss = ""
    cfgDict = {}

    with open("/home/pi/swan/ganga.json", "r") as cfghandle:
        cfgDict = json.load(cfghandle)

    print(cfgDict)

    filename = cfgDict["filename"]
    token = cfgDict["token"]
    msl = cfgDict["msl"]

    configJson = {"Username": filename,
                  "Accesstoken": token, "TimeUTC": "time"}

    dataJson = {"Username": filename, "Accesstoken": token,
                "TimeUTC": "time", "Fields": "{}"}

    fieldsJson = {"SiteID": "12345", "GPS": "gps", "BOD": "1.20", "DO": "7.51", "TEMPERATURE": "0",
                  "CONDUCTIVITY": "0", "PH": "0", "COD": "0", "TURBIDITY": "0", "CHLORIDE": "0",
                  "NITRATE": "0", "TOC": "0", "DEPTH": "0", "TRYPPPB": "0", "TRYPTEMP": "0", "CDOMTEMP": "0", "CDOM": "0", "SignalStrength": "0"}

    fieldsDict = {3: "BOD", 4: "DO", 5: "TEMPERATURE", 6: "CONDUCTIVITY", 7: "PH", 8: "COD", 9: "TURBIDITY", 10: "CHLORIDE",
                  11: "NITRATE", 12: "TOC", 13: "DEPTH", 14: "TRYPPPB", 15: "TRYPTEMP", 16: "CDOMTEMP", 17: "CDOM"}

    dataurl = 'https://122.187.53.98:5443/api/v1/data'
    configurl = 'https://122.187.53.98:5443/api/v1/config'

    IST = pytz.timezone('Asia/Kolkata')
    UTC = pytz.timezone('UTC')
    retry_count = 0
    flag = True

    dbfile = "/home/pi/swan/proteus.csv"
    resp = ""
    ss = 28
    ser = None
    isCameraAvailable = False

    def turnOnSensor():
        try:
            os.system("sudo echo \"11\" > /sys/class/gpio/export")
            time.sleep(1)
            os.system("sudo echo \"out\" > /sys/class/gpio/gpio11/direction")
            time.sleep(1)
            os.system("sudo echo \"1\" > /sys/class/gpio/gpio11/value")
        except Exception as e:
            print("Error while truning on the sensor")
            print(e)

    def turnOffSensor():
        os.system("sudo echo \"0\" > /sys/class/gpio/gpio11/value")

    def getRSSI():
        try:
            global ss
            rssi = subprocess.check_output(
                "sudo qmicli -p -d /dev/cdc-wdm0 --nas-get-signal-info | grep RSSI", shell=True).decode('utf-8')
            output = rssi.split("'")
            ss = output[1].split(" ")[0]
        except Exception as e:
            print(e)

    def open_serial():
        try:
            global ser
            ser = serial.Serial(
                port="/dev/ttyS0",
                baudrate=19200,
                timeout=5,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS)
        except Exception as e:
            print(e)

    try:
        now = datetime.now(IST)
        print("Turning on the sensor")
        turnOnSensor()
        time.sleep(10)
        getRSSI()
        open_serial()
        while flag:
            print()
            print("**************************************")
            print("Starting to wipe the sensors, this will take some time ")
            #   ser.write("WIPE\r\n".encode())
            time.sleep(30)

            ser = serial.Serial(
                port="/dev/ttyS0",
                baudrate=19200,
                timeout=5,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS)
            ser.reset_input_buffer()
            print("Reading sensor values now \n")
            ser.write("READ\r\n".encode())
            time.sleep(5)
            line = None
            p = time.time()
            while time.time() - p < 60:
                if ser.inWaiting():
                    line = ser.readline()
                    if "DATA" in str(line):
                        print(str(line))
                        break
                    elif "Do What" in str(line):
                        print(line)
                    else:
                        print(str(line))
                time.sleep(1)
            turnOffSensor()
            if(line):
                line = str(line)
                line = line.replace("\\r\\n'", "")
                values = line.split(",")
                now = datetime.now(IST)
                utcnow = datetime.now(UTC)
                dataJson["TimeUTC"] = utcnow.strftime("%Y-%m-%dT%H:%M:%SZ")
                index = 3
                for i in values[3:]:
                    fieldsJson[fieldsDict[index]] = float(i)
                    index = index + 1
                fieldsJson["LEVEL"] = float(fieldsJson["DEPTH"]) + float(msl)
                fieldsJson["SignalStrength"] = ss
                print(fieldsJson["BOD"], fieldsJson["TOC"], fieldsJson["COD"])
                now_date_time = now.strftime("%Y%m%d_%H:%M:%S")
                resp = now_date_time
                print(validate(fieldsJson["BOD"],
                      fieldsJson["TOC"], fieldsJson["COD"]))
                fieldsJson["BOD"], fieldsJson["TOC"], fieldsJson["COD"] = validate(
                    fieldsJson["BOD"], fieldsJson["TOC"], fieldsJson["COD"])

                if fieldsJson["DO"] <= 0.2:
                    fieldsJson["DO"] = 0.2
                if fieldsJson["DO"] >= 20.0:
                    fieldsJson["DO"] = 20.0

                if fieldsJson["CONDUCTIVITY"] <= 1.0:
                    fieldsJson["CONDUCTIVITY"] = 1.0
                if fieldsJson["CONDUCTIVITY"] >= 5000.0:
                    fieldsJson["CONDUCTIVITY"] = 5000.0

                if fieldsJson["NITRATE"] <= float(0):
                    fieldsJson["NITRATE"] = float(0)
                if fieldsJson["NITRATE"] >= 50.0:
                    fieldsJson["NITRATE"] = 50.0

                if fieldsJson["PH"] <= float(0):
                    fieldsJson["PH"] = float(0)
                if fieldsJson["PH"] >= 14.0:
                    fieldsJson["PH"] = 14.0

                if fieldsJson["TURBIDITY"] <= float(0):
                    fieldsJson["TURBIDITY"] = float(0)
                if fieldsJson["TURBIDITY"] >= 2000.0:
                    fieldsJson["TURBIDITY"] = 2000.0

                if fieldsJson["TEMPERATURE"] <= float(0):
                    fieldsJson["TEMPERATURE"] = float(0)
                if fieldsJson["TEMPERATURE"] >= 50.0:
                    fieldsJson["TEMPERATURE"] = 50.0

                if fieldsJson["CHLORIDE"] <= float(0):
                    fieldsJson["CHLORIDE"] = float(0)
                if fieldsJson["CHLORIDE"] >= 200.0:
                    fieldsJson["CHLORIDE"] = 200.0

                dataJson["Fields"] = fieldsJson
                flag = False
                print(dataJson)
                return dataJson
            else:
                # find_tty()
                flag = False
                return "Failed to read values"
    except Exception as e:
        print("Something gone wrong")

    finally:
        ser.close()
        turnOffSensor()


# print(read_data())
