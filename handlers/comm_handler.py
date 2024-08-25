import os
import datetime
import time
import threading
import snap7
from snap7 import Client, Block, Area
from snap7.util import *
import json


class S7_Manager:
    def __init__(self, ip_address: str = '192.168.0.1', rack: int = 0, cpu_slot: int = 1, tcp_port: int = 102):
        self._ip_address = ip_address
        self._rack = rack
        self._cpu_slot = cpu_slot
        self._tcp_port = tcp_port

        self._plc = snap7.client.Client()
        self._plc.connect(self._ip_address, self._rack, self._cpu_slot)

        if self._plc.get_connected():
            print("PLC connected successfully!")
        else:
            print("Could not connect to PLC!")

    def parse_S7CpuInfo(self, data) -> dict:
        return {
            "ModuleTypeName": f"{bytes(data.ModuleTypeName).decode('utf-8')}",
            "SerialNumber": f"{bytes(data.SerialNumber).decode('utf-8')}",
            "ASName": f"{bytes(data.ASName).decode('utf-8')}",
            "Copyright": f"{bytes(data.Copyright).decode('utf-8')}",
            "ModuleName": f"{bytes(data.ModuleName).decode('utf-8')}"
        }

    def parse_S7OrderCode(self, data) -> dict:
        return {
            "ModulePartNumber": f"{bytes(data.OrderCode).decode('utf-8').strip()}"
        }

    # get info from plc cpu
    def get_cpu_info(self):
        result = self.parse_S7CpuInfo(self._plc.get_cpu_info())
        result.update(self.parse_S7OrderCode(self._plc.get_order_code()))
        return result

    # get datetime from PLC
    def get_plc_datetime(self):
        pass

    def read_area(self, area: Area, db_number: int, start_byte: int, number_of_bytes: int):
        return self._plc.read_area(area, db_number, start_byte, number_of_bytes)

    # result = snap7.util.get_real(result, 0)
    # def get_tag_list(self):
    #     pass
    # with self._plc as plc:
    #     return plc.get_tag_list()

    # def get_tag_list_json(self):
    #     pass
    #     # with self._plc as plc:
    #     #     return plc.tags_json

    # def read_single_tag(self, tag_name: str = 'testDINT'):
    #     pass
    #     # # Reading a single tag returns a Tag object
    #     # # e.g. Tag(tag='testDINT', value=20, type='DINT', error=None)
    #     #
    #     # with self._plc as plc:
    #     #     result = plc.read(tag_name)
    #     #     # print(result)
    #     #     if result.error is None:
    #     #         # print(f'{datetime.datetime.now()}\t|\tReading successfully from \t{tag_name}: {result.value:.2f}')
    #     #         return result.value
    #     #     else:
    #     #         print(f'{datetime.datetime.now()}\t|\tError reading from \t{tag_name}: {result.error}')
    #     #         return None

    # def read_multiple_tags(self, tag_names: list = ['testDINT', 'testSine']):
    #     pass
    #     # # Reading multiple tags returns a list of Tag objects
    #     # # e.g. [Tag(tag='testDINT', value=20, type='DINT', error=None),
    #     # #       Tag(tag='testSine', value=100.36, type='REAL', error=None)]
    #     #
    #     # values = []
    #     # with self._plc as plc:
    #     #     results = plc.read(*tag_names)
    #     #
    #     #     for tag_name, result in zip(tag_names, results):
    #     #         if result.error is None:
    #     #             values.append(result.value)
    #     #         else:
    #     #             print(f'Error reading {tag_name}: {result.error}')
    #     #             values.append(None)
    #     #
    #     # return values

    # def read_udt(self, inst_name: str = 'Tank1'):
    #     pass
    #     # # Structures can be read as a whole, assuming that no attributes have External Access set to None.
    #     # # Structure tags will be a single Tag object, but the value attribute will be a dict of {attribute: value}.
    #     # # e.g. Tag(tag='Tank1', value={'Level': 100.5, 'Level_EU': "ft", 'Volume': 1000, 'Volume_EU': "gal"},
    #     # #          type='udtTank', error=None)
    #     #
    #     # with self._plc as plc:
    #     #     return plc.read(inst_name)

    # def write_single_tag(self, tag_name: str = 'testSine', tag_value=None):
    #     pass
    #     # # Writing a single tag returns a single Tag object response
    #     # # e.g. Tag(tag='testSine', value=100.5, type='REAL', error=None)
    #     #
    #     # with self._plc as plc:
    #     #     result = plc.write((tag_name, tag_value))
    #     #     # print(result)
    #     #
    #     # if result.error is None:
    #     #     # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
    #     #     return result.value
    #     # else:
    #     #     print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
    #     #     return None

    # def write_multiple_tags(self, tag_names: list = ['testSine', 'testDINT'], tag_values: list = [None, None]):
    #     pass
    #     # # Writing multiple tags will return a list of Tag objects
    #     # # e.g. [Tag(tag='testSine', value=25.2, type='REAL', error=None),
    #     # #       Tag(tag='testDINT', value=20, type='DINT', error=None)]
    #     #
    #     # with self._plc as plc:
    #     #     data = list(zip(tag_names, tag_values))
    #     #     results = plc.write(*data)
    #     #     # print(type(result),result)
    #     #
    #     # for tag_name, result in zip(tag_names, results):
    #     #     if result.error is None:
    #     #         # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
    #     #         return result.value
    #     #     else:
    #     #         print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
    #     #         return None


class Analog_Filt_Scale:
    def __init__(self, buffer: bytearray):
        self._buffer = buffer
        # Inputs
        self.Raw_Input = get_int(self._buffer, 0)
        self.Def_High_Range = round(get_real(self._buffer, 2), 2)
        self.Def_Low_Range = round(get_real(self._buffer, 6), 2)
        self.Def_High_Proc = round(get_real(self._buffer, 10), 2)
        self.Def_Low_Proc = round(get_real(self._buffer, 14), 2)
        self.Def_High_Warn = round(get_real(self._buffer, 18), 2)
        self.Def_Low_Warn = round(get_real(self._buffer, 22), 2)
        self.Def_Num_Samp = get_int(self._buffer, 26)
        self.Def_Sample_Time = get_time(self._buffer, 28)
        self.Def_Range_Timer = get_time(self._buffer, 32)
        self.Def_Proc_Timer = get_time(self._buffer, 36)
        self.Def_Warn_Timer = get_time(self._buffer, 40)
        self.Cmd_Reset_Alarm = get_bool(self._buffer, 44, 0)
        # Outputs
        self.Stat_PV = round(get_real(self._buffer, 46), 2)
        self.Stat_High_Range = get_bool(self._buffer, 50, 0)
        self.Stat_Low_Range = get_bool(self._buffer, 50, 1)
        # Static
        self.Cmd_Clear_Table = get_bool(self._buffer, 52, 0)
        self.Cmd_Filter_En = get_bool(self._buffer, 52, 1)
        self.Cmd_Auto = get_bool(self._buffer, 52, 2)
        self.Cmd_Sim = get_bool(self._buffer, 52, 3)
        self.Cmd_Proc_En = get_bool(self._buffer, 52, 4)
        self.Cmd_Warn_En = get_bool(self._buffer, 52, 5)
        self.Cmd_Alarm_En = get_bool(self._buffer, 52, 6)
        self.Cmd_Sim_Value = get_real(self._buffer, 54)
        self.Cfg_High_Range = get_real(self._buffer, 58)
        self.Cfg_Low_Range = get_real(self._buffer, 62)
        self.Cfg_Scale_Offset = get_real(self._buffer, 66)
        self.Cfg_High_Proc = get_real(self._buffer, 70)
        self.Cfg_Low_Proc = get_real(self._buffer, 74)
        self.Cfg_High_Warn = get_real(self._buffer, 78)
        self.Cfg_Low_Warn = get_real(self._buffer, 82)
        self.Cfg_Range_Timer = get_time(self._buffer, 86)
        self.Cfg_Proc_Timer = get_time(self._buffer, 90)
        self.Cfg_Warn_Timer = get_time(self._buffer, 94)
        self.Cfg_Num_Of_Samp = get_int(self._buffer, 98)
        self.Cfg_Sample_time = get_time(self._buffer, 100)
        self.Stat_Auto = get_bool(self._buffer, 104, 0)
        self.Stat_Sim = get_bool(self._buffer, 104, 1)
        self.Stat_Raw = get_int(self._buffer, 106)
        self.Stat_Scale = get_real(self._buffer, 108)
        self.Stat_Fault = get_bool(self._buffer, 112, 0)
        self.Stat_High_Proc = get_bool(self._buffer, 112, 1)
        self.Stat_Low_Proc = get_bool(self._buffer, 112, 2)
        self.Stat_High_Warn = get_bool(self._buffer, 112, 3)
        self.Stat_Low_Warn = get_bool(self._buffer, 112, 4)
        self.Cfg_Return_Auto = get_time(self._buffer, 114)

    def __str__(self):
        return json.dumps(self.get_all_values(),indent=4)


    def get_all_values(self):
        result = {}
        result.update({'Raw_Input': self.Raw_Input})
        result.update({'Def_High_Range': self.Def_High_Range})
        result.update({'Def_Low_Range':self.Def_Low_Range})
        result.update({'Def_Low_Proc':self.Def_Low_Proc})
        result.update({'Def_High_Warn':self.Def_High_Warn})
        result.update({'Def_Low_Warn':self.Def_Low_Warn})
        result.update({'Def_Sample_Time':self.Def_Sample_Time})
        result.update({'Def_Range_Timer':self.Def_Range_Timer})
        result.update({'Def_Proc_Timer':self.Def_Proc_Timer})
        result.update({'Def_Warn_Timer':self.Def_Warn_Timer})
        result.update({'Cmd_Reset_Alarm':self.Cmd_Reset_Alarm})
        result.update({'Stat_PV':self.Stat_PV})
        result.update({'Stat_High_Range':self.Stat_High_Range})
        result.update({'Stat_Low_Range':self.Stat_Low_Range})
        #
        #
        # f"'Cmd_Clear_Table':{self.Cmd_Clear_Table}, 'Cmd_Filter_En':{self.Cmd_Filter_En}, " \
        # f"'Cmd_Auto':{self.Cmd_Auto},'Cmd_Sim':{self.Cmd_Sim}, 'Cmd_Proc_En':{self.Cmd_Proc_En}, " \
        # f"'Cmd_Warn_En':{self.Cmd_Warn_En}, 'Cmd_Alarm_En':{self.Cmd_Alarm_En}, " \
        # f"'Cmd_Sim_Value':{self.Cmd_Sim_Value}, 'Cfg_High_Range':{self.Cfg_High_Range}," \
        # f"'Cfg_Low_Range':{self.Cfg_Low_Range}, 'Cfg_Scale_Offset':{self.Cfg_Scale_Offset}," \
        # f"'Cfg_High_Proc:{self.Cfg_High_Proc}', 'Cfg_Low_Proc:{self.Cfg_Low_Proc}', " \
        # f"'Cfg_High_Warn':{self.Cfg_High_Warn},     'Cfg_Low_Warn':{self.Cfg_Low_Warn}, " \
        # f"'Cfg_Range_Timer':{self.Cfg_Range_Timer},     'Cfg_Proc_Timer':{self.Cfg_Proc_Timer}, " \
        # f"'Cfg_Warn_Timer':{self.Cfg_Warn_Timer},     'Cfg_Num_Of_Samp':{self.Cfg_Num_Of_Samp}, " \
        # f"'Cfg_Sample_time':{self.Cfg_Sample_time}, 'Stat_Auto':{self.Stat_Auto}," \
        # f"'Stat_Sim':{self.Stat_Sim}, ''Stat_Raw':{self.Stat_Raw}, " \
        # f"'Stat_Scale':{self.Stat_Scale},     'Stat_Fault':{self.Stat_Fault}, " \
        # f"'Stat_High_Proc':{self.Stat_High_Proc}, 'Stat_Low_Proc':{self.Stat_Low_Proc}," \
        # f"'Stat_High_Warn':{self.Stat_High_Warn}, 'Stat_Low_Warn':{self.Stat_Low_Warn}," \
        # f"'Cfg_Return_Auto':{self.Cfg_Return_Auto}}}"
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})
        # result.update({})

        return result

    def get_all_attributes(self):
        return list(self.get_all_values().keys())
