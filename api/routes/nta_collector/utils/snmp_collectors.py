import traceback,sys
from pysnmp.hlapi import *
from datetime import datetime
import time
import requests
import re



class SnmpCollector():
    def __init__(self):
        pass
        # self.engine = engine
        # self.community = community
        # self.port = port
        # self.snmp_version = snmp_version
        # self.device_type  =  device_type


    def snmp_device_type(self,device_type):
        try:
            device_typ_dict = {
                'cisco_ios':{
                    'device_name': '1.3.6.1.2.1.1.5',
                    'device_description': '1.3.6.1.2.1.1.1',
                    'interfaces': '1.3.6.1.2.1.31.1.1.1.1',
                    'interface_status': '1.3.6.1.2.1.2.2.1.7',
                    'interface_description': '1.3.6.1.2.1.2.2.1.2',
                    'download': '1.3.6.1.2.1.31.1.1.1.6',
                    'upload': '1.3.6.1.2.1.31.1.1.1.10',

                }
            }

            return device_typ_dict.get(device_type, {})

        except Exception as e:
            print(f"Unknown device type: {device_type}", file=sys.stderr)

    def createSnmpObjectV2(self, ip, string, port):
        try:
            print(f"{ip}: Creating SNMP V1/V2 Object", file=sys.stderr)
            engin = SnmpEngine()
            community = CommunityData(mpModel=1, communityIndex=ip, communityName=string)
            transport = UdpTransportTarget((ip, port), timeout=5.0, retries=1)
            context = ContextData()
            return [engin, community, transport, context]
        except Exception as e:
            print(f"{ip}: Exception While Creating SNMP V1/V2 Object", file=sys.stderr)
            traceback.print_exc()
            return None

    def testSnmpConnection(self, snmp):
        try:
            engn = snmp[0]
            community = snmp[1]
            transport = snmp[2]
            cnxt = snmp[3]

            oid = ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)

            error_indication, error_status, error_index, var_binds = next(
                getCmd(engn, community, transport, cnxt, ObjectType(oid))
            )
            # Check if SNMP query was successful
            if error_indication:
                print(f"SNMP query failed: {error_indication}", file=sys.stderr)
            elif error_status:
                print(f"SNMP query failed: {error_status.prettyPrint()}", file=sys.stderr)
            else:
                return True

            return False
        except Exception as e:
            traceback.print_exc()
            return False

    def createSnmpObjectV3(self, ip_address, community,port):
        try:
            auth_proc = None
            encryp_proc = None
            if credentials.authentication_method == "MD5":
                auth_proc = usmHMACMD5AuthProtocol
            if credentials.authentication_method == "SHA":
                auth_proc = usmHMACSHAAuthProtocol
            if credentials.authentication_method == "SHA-128":
                auth_proc = usmHMAC128SHA224AuthProtocol
            if credentials.authentication_method == "SHA-256":
                auth_proc = usmHMAC192SHA256AuthProtocol
            if credentials.authentication_method == "SHA-512":
                auth_proc = usmHMAC384SHA512AuthProtocol

            if credentials.encryption_method == "DES":
                encryp_proc = usmDESPrivProtocol
            if credentials.encryption_method == "AES-128" or credentials.encryption_method == "AES":
                encryp_proc = usmAesCfb128Protocol
            if credentials.encryption_method == "AES-192":
                encryp_proc = usmAesCfb192Protocol
            if credentials.encryption_method == "AES-256":
                encryp_proc = usmAesCfb256Protocol

            engin = SnmpEngine()
            community = UsmUserData(
                userName=credentials.username,
                authKey=credentials.password,
                privKey=credentials.encryption_password,
                authProtocol=auth_proc,
                privProtocol=encryp_proc,
            )
            transport = UdpTransportTarget(
                (ip_address, credentials.snmp_port), timeout=5.0, retries=1
            )
            context = ContextData()
            return [engin, community, transport, context]
        except Exception as e:
            print(
                f"{ip_address}: Exception While Creating SNMP V3 Object",
                file=sys.stderr,
            )
            traceback.print_exc()
            return None

    def getSnmpData(self, community, port,snmp_version,device_type,ip_address,collector_data):
        try:
            device_data_list = {}
            # if snmp_version == "v3":
            #     snmp = self.createSnmpObjectV3(ip_address=ip_address, community = community,port=port)
            #     connection = self.testSnmpConnection(snmp)
            if snmp_version == "v1/v2" and collector_data =='All':
                snmp = self.createSnmpObjectV2(ip_address, community,port)
                print("snmp bject for version v1/v2 is:",snmp,file=sys.stderr)
                connection = self.testSnmpConnection(snmp)
                if connection:
                    device = self.getDeviceData(ip_address=ip_address, snmp = snmp,device_type=device_type)
                    device_data_list['device'] = device #.append({"device":device})

                    interfaces =  self.getInterfaceData(ip_address, snmp, device_type)
                    print("Interfaces dat is@@@@@@@@@@@@@@@@@@@@@@@@@@@@",interfaces,file=sys.stderr)
                    device_data_list['interfaces'] = interfaces #.append({"interfaces":interfaces})
                else:
                    print(f"SNMP connection failed for {ip_address}, setting SNMP status to 'Down'", file=sys.stderr)
            elif snmp_version == "v1/v2" and collector_data == 'interface':
                snmp = self.createSnmpObjectV2(ip_address, community,port)
                print("snmp bject for version v1/v2 is:",snmp,file=sys.stderr)
                connection = self.testSnmpConnection(snmp)
                if connection:
                    # device = self.getDeviceData(ip_address=ip_address, snmp = snmp,device_type=device_type)
                    # device_data_list.append(device)

                    interfaces =  self.getInterfaceData(ip_address, snmp, device_type)
                    print("Interfaces dat is@@@@@@@@@@@@@@@@@@@@@@@@@@@@",interfaces,file=sys.stderr)
                    device_data_list['interfaces'] = interfaces 
                else:
                    print(f"SNMP connection failed for {ip_address}, setting SNMP status to 'Down'", file=sys.stderr)
            else:
                print(f"{ip_address}: Error : SNMP Version Unknown", file=sys.stderr)



            return device_data_list  # Change here
        except Exception as e:
            traceback.print_exc()
            print("Error Occurred while getting SNMP data", str(e), file=sys.stderr)

    def getDeviceName(self,ip_address, snmp, oid):
        try:
            print(f"working on ip:{ip_address} oid:{oid}", file=sys.stderr)
            engn = snmp[0]
            community = snmp[1]
            transport = snmp[2]
            cnxt = snmp[3]

            device = "NA"
            try:
                value = self.get_oid_data(engn, community, transport, cnxt, oid)
                print("value for the device name is:",value,file=sys.stderr)
                device = self.parse_general(value)
            except:
                print(f"{ip_address}: Error in Device Name", file=sys.stderr)
                traceback.print_exc()

            print(f"{ip_address}: Device Name : {device}", file=sys.stderr)
            return device
        except Exception as e:
            traceback.print_exc()
            print("Error Occured while getting device name", str(e))


    def getDeviceData(self, ip_address, snmp, device_type):
        try:
            device = ip_address
            uptime_result = None
            output = dict()

            device_oids = self.snmp_device_type(device_type)
            if device_oids is not None:
                device_name_result = self.getDeviceName(ip_address, snmp, device_oids['device_name'])
                output['device_name'] = device_name_result

                device_description_result = self.getDeviceName(ip_address, snmp, device_oids['device_description'])
                output['device_description'] = device_description_result
                output['datetime'] = datetime.now()

                interface = dict()
                try:
                    print(f"{ip_address}: Interface Data Extraction/Insertion Started", file=sys.stderr)
                    interface = self.getInterfaceData(ip_address, snmp, device_oids)

                except Exception as e:
                    print(f"Error while processing interface data for {ip_address}: {e}", file=sys.stderr)

            print("------------------------------------Output is getDeviceData >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", uptime_result, file=sys.stderr)
            return output

        except Exception as e:
            # Catch any exceptions and log the traceback
            traceback.print_exc()
            print("Error Occurred while getting device data:", str(e), file=sys.stderr)
            return None






    def get_oid_data(self, engn, community, transport, cnxt, oid):
        try:
            print(f"\nSNMP walk started for OID {oid}", file=sys.stderr)

            oid = ObjectType(ObjectIdentity(oid))
            all = []

            for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
                engn, community, transport, cnxt, oid, lexicographicMode=False
            ):
                if errorIndication:
                    print(f"error=>{errorIndication}", file=sys.stderr)
                    return "NA"
                elif errorStatus:
                    print(
                        "%s at %s"
                        % (
                            errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                        ),
                        file=sys.stderr
                    )
                    return "NA"
                else:
                    for varBind in varBinds:
                        all.append(varBind)
            return all
        except Exception as e:
            print(f"Failed to run SNMP walk: {e}", file=sys.stderr)
            traceback.print_exc()
            return "NA"

    def parse_general(self,varbinds):
        try:
            for varBind in varbinds:
                print("var bind is:########################",varBind,file=sys.stderr)
                res = " = ".join([x.prettyPrint() for x in varBind])
                if "No Such Instance" not in res:
                    result = res.split("=")[1].strip()
                    return result
        except Exception as e:
            traceback.print_exc()
            print("error occured while parse genenral", str(e))

    def getInterfaceData(self, ip_address, snmp, device_type):
        try:
            oids = self.snmp_device_type(device_type)
            interfaceList = dict()

            if oids is None:
                print(f"{ip_address}: OIDs not found for device type {device_type}", file=sys.stderr)
                return None

            # Retrieve interfaces and descriptions
            interfaces = self.getInterfaceList(ip_address, snmp, oids["interfaces"])
            if not interfaces:
                return None

            interface_description = self.getInterfaceList(ip_address, snmp, oids["interface_description"])
            if not interface_description:
                interface_description = {key: ["NA"] for key in interfaces.keys()}

            interface_status = self.getInterfaceList(ip_address, snmp, oids["interface_status"])
            if not interface_status:
                interface_status = {key: ["NA"] for key in interfaces.keys()}

            # Take first snapshot
            start_time = datetime.now()
            print(f"{ip_address}: Taking 1st Snapshot: {str(start_time)}", file=sys.stderr)
            download_counter_start = self.getInterfaceList(ip_address, snmp, oids["download"])
            upload_counter_start = self.getInterfaceList(ip_address, snmp, oids["upload"])

            time.sleep(10)  # Wait for second snapshot

            # Take second snapshot
            end_time = datetime.now()
            print(f"{ip_address}: Taking 2nd Snapshot: {str(end_time)}", file=sys.stderr)
            download_counter_end = self.getInterfaceList(ip_address, snmp, oids["download"])
            upload_counter_end = self.getInterfaceList(ip_address, snmp, oids["upload"])

            time_difference = (end_time - start_time).total_seconds()
            print(f"{ip_address}: Time Difference: {time_difference} seconds", file=sys.stderr)

            # Helper function to calculate bandwidth with wrap-around handling
            def calculate_speed(start, end, time_diff, max_counter=2 ** 32):
                print(f"Calculate speed is {start}::::{end}:::{time_diff}::{max_counter}:::",file=sys.stderr)
                # if start is None or end is None:
                #     return 0.0
                try:
                    start = float(start)
                    end   = float(end)

                    print("start is :::::::::::::::::::::::::::::",start,file=sys.stderr)
                    print("end value is  :::::::::",end,file=sys.stderr)
                    
                    delta = end - start if end >= start else (max_counter - start) + end
                    print("delta is :::::::::::::::::::::::::::::",delta,file=sys.stderr)
                    speed = (delta * 8) / time_diff / 1_000_000  # Convert to Mbps
                    print("speed is :::::::::::::::::::::::::::::",speed,file=sys.stderr)
                    return round(speed, 5)
                except Exception as e:
                    traceback.print_exc()
                    print(f"{ip_address}: Error in speed calculation: {e}", file=sys.stderr)
                    return 0.0

            # Build interface data
            for key in interfaces.keys():
                description = interface_description.get(key, ["NA"])[0]
                status = "Up" if interface_status.get(key, ["0"])[0] == "1" else "Down"
                
                print("int(download_counter_start.get(key, [0])[0]) is::",download_counter_start,file=sys.stderr)
                print("download counter star is::",int(download_counter_start.get(key, [0])[0]),file=sys.stderr)
                

                download_start = download_counter_start.get(key, [0])[0] if download_counter_start else 0
                download_end = download_counter_end.get(key, [0])[0] if download_counter_end else 0
                upload_start = upload_counter_start.get(key, [0])[0] if upload_counter_start else 0
                upload_end = upload_counter_end.get(key, [0])[0]  if upload_counter_end else 0
                

                print("download start is @@@@@@@@@@@",download_start,file=sys.stderr)
                print("download ed is @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",download_end,file=sys.stderr)
                
                download_speed = calculate_speed(download_start, download_end, time_difference)
                upload_speed = calculate_speed(upload_start, upload_end, time_difference)
                
                print("download speeed is @@@@@@@@@@@@@@@@@@@@@@@@@@@@",download_speed,file=sys.stderr)
                print("upload speeed is @@@@@@@@@@@@@@@@@",upload_speed,file=sys.stderr)
                
                interfaceObj = {
                    "name": interfaces[key][0],
                    "status": status,
                    "description": description,
                    "download": download_speed,
                    "upload": upload_speed,
                }

                interfaceList[key] = interfaceObj

            print(f"{ip_address}: Interface Data: {interfaceList}", file=sys.stderr)
            interfaceList['datetime'] = datetime.now()
            return interfaceList

        except Exception as e:
            traceback.print_exc()
            print(f"Error occurred while getting interface data: {e}", file=sys.stderr)
            return None
    def getInterfaceList(self,ip_address, snmp, oid):
        try:
            print(f"Get Insertface list parameters are   {ip_address} {snmp} {oid}------------------>", file=sys.stderr)
            engn = snmp[0]
            community = snmp[1]
            transport = snmp[2]
            cnxt = snmp[3]

            interfaces = None
            try:
                value = self.get_oid_data(engn, community, transport, cnxt, oid)
                print("<---------------------Values in the Get OID data is -------------------->", value,
                      file=sys.stderr)
                interfaces = self.parse_snmp_output(value)
                print("<------------------------Interfaces in the get interfaces list is ---------->", interfaces,
                      file=sys.stderr)
            except:
                print(f"{ip_address}: Error in Interfaces", file=sys.stderr)
                traceback.print_exc()
                return None

            print(f"{ip_address}: Interfaces : {interfaces}", file=sys.stderr)
            return interfaces
        except Exception as e:
            traceback.print_exc()
            print("Error OCcured while getting interface list", str(e))

    def parse_snmp_output(self,varbinds):
            try:
                intefaces_val = dict()
                for varbind in varbinds:
                    out = re.search(r"\d* .*", str(varbind)).group()
                    value = out.split("=")
                    intefaces_val[value[0].strip()] = [value[1].strip()]

                return intefaces_val
            except Exception as e:
                traceback.print_exc()
                print("Error Occured while getting parse snmp output", str(e))

