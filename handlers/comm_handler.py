import enum
import os
import datetime
import time
import threading
from typing import Union
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
        return json.dumps(result, indent=4)

    # get datetime from PLC
    def get_plc_datetime(self):
        pass

    def read_area(self, area: Area, db_number: int, start_byte: int, number_of_bytes: int) -> bytearray:
        """
        Read a data area from a PLC: DB, Inputs, Outputs, Memory, Timers and Counters.

        Args:
            area: area to be read from.
            db_number: The DB number, only used when area=Areas.DB
            start_byte: byte index to start reading.
            number_of_bytes: number of bytes to read.

        Returns:
            Buffer with the data read.
        """
        try:
            return self._plc.read_area(area, db_number, start_byte, number_of_bytes)
        except Exception as e:
            print(e)

    def write_area(self, area: Area, db_number: int, start_byte: int, data: bytearray) -> int:
        """
        Writes a data area into a PLC.

        Args:
            area: area to be written.
            db_number: number of the db to be written to. In case of Inputs, Marks or Outputs, this should be equal to 0
            start: byte index to start writting.
            data: buffer to be written.

        Returns:
            Snap7 error code.
        """
        try:
            self._plc.write_area(area, db_number, start_byte, data)
        except Exception as e:
            print(e)


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
        self.Cmd_Sim_Value = round(get_real(self._buffer, 54), 2)
        self.Cfg_High_Range = round(get_real(self._buffer, 58), 2)
        self.Cfg_Low_Range = round(get_real(self._buffer, 62), 2)
        self.Cfg_Scale_Offset = round(get_real(self._buffer, 66), 2)
        self.Cfg_High_Proc = round(get_real(self._buffer, 70), 2)
        self.Cfg_Low_Proc = round(get_real(self._buffer, 74), 2)
        self.Cfg_High_Warn = round(get_real(self._buffer, 78), 2)
        self.Cfg_Low_Warn = round(get_real(self._buffer, 82), 2)
        self.Cfg_Range_Timer = get_time(self._buffer, 86)
        self.Cfg_Proc_Timer = get_time(self._buffer, 90)
        self.Cfg_Warn_Timer = get_time(self._buffer, 94)
        self.Cfg_Num_Of_Samp = get_int(self._buffer, 98)
        self.Cfg_Sample_time = get_time(self._buffer, 100)
        self.Stat_Auto = get_bool(self._buffer, 104, 0)
        self.Stat_Sim = get_bool(self._buffer, 104, 1)
        self.Stat_Raw = get_int(self._buffer, 106)
        self.Stat_Scale = round(get_real(self._buffer, 108), 2)
        self.Stat_Fault = get_bool(self._buffer, 112, 0)
        self.Stat_High_Proc = get_bool(self._buffer, 112, 1)
        self.Stat_Low_Proc = get_bool(self._buffer, 112, 2)
        self.Stat_High_Warn = get_bool(self._buffer, 112, 3)
        self.Stat_Low_Warn = get_bool(self._buffer, 112, 4)
        self.Cfg_Return_Auto = get_time(self._buffer, 114)

    def __str__(self):
        return json.dumps(self.read_values(), indent=4)

    def get_attributes(self):
        return list(self.read_values().keys())

    def read_values(self):
        result = {}
        result.update({'Raw_Input': self.Raw_Input})
        result.update({'Def_High_Range': self.Def_High_Range})
        result.update({'Def_Low_Range': self.Def_Low_Range})
        result.update({'Def_Low_Proc': self.Def_Low_Proc})
        result.update({'Def_High_Warn': self.Def_High_Warn})
        result.update({'Def_Low_Warn': self.Def_Low_Warn})
        result.update({'Def_Sample_Time': self.Def_Sample_Time})
        result.update({'Def_Range_Timer': self.Def_Range_Timer})
        result.update({'Def_Proc_Timer': self.Def_Proc_Timer})
        result.update({'Def_Warn_Timer': self.Def_Warn_Timer})
        result.update({'Cmd_Reset_Alarm': self.Cmd_Reset_Alarm})
        result.update({'Stat_PV': self.Stat_PV})
        result.update({'Stat_High_Range': self.Stat_High_Range})
        result.update({'Stat_Low_Range': self.Stat_Low_Range})
        result.update({'Cmd_Clear_Table': self.Cmd_Clear_Table})
        result.update({'Cmd_Filter_En': self.Cmd_Filter_En})
        result.update({'Cmd_Auto': self.Cmd_Auto})
        result.update({'Cmd_Sim': self.Cmd_Sim})
        result.update({'Cmd_Proc_En': self.Cmd_Proc_En})
        result.update({'Cmd_Warn_En': self.Cmd_Warn_En})
        result.update({'Cmd_Alarm_En': self.Cmd_Alarm_En})
        result.update({'Cmd_Sim_Value': self.Cmd_Sim_Value})
        result.update({'Cfg_High_Range': self.Cfg_High_Range})
        result.update({'Cfg_Low_Range': self.Cfg_Low_Range})
        result.update({'Cfg_Scale_Offset': self.Cfg_Scale_Offset})
        result.update({'Cfg_High_Proc': self.Cfg_High_Proc})
        result.update({'Cfg_Low_Proc': self.Cfg_Low_Proc})
        result.update({'Cfg_High_Warn': self.Cfg_High_Warn})
        result.update({'Cfg_Low_Warn': self.Cfg_Low_Warn})
        result.update({'Cfg_Range_Timer': self.Cfg_Range_Timer})
        result.update({'Cfg_Proc_Timer': self.Cfg_Proc_Timer})
        result.update({'Cfg_Warn_Timer': self.Cfg_Warn_Timer})
        result.update({'Cfg_Num_Of_Samp': self.Cfg_Num_Of_Samp})
        result.update({'Cfg_Sample_time': self.Cfg_Sample_time})
        result.update({'Stat_Auto': self.Stat_Auto})
        result.update({'Stat_Sim': self.Stat_Sim})
        result.update({'Stat_Raw': self.Stat_Raw})
        result.update({'Stat_Scale': self.Stat_Scale})
        result.update({'Stat_Fault': self.Stat_Fault})
        result.update({'Stat_High_Proc': self.Stat_High_Proc})
        result.update({'Stat_Low_Proc': self.Stat_Low_Proc})
        result.update({'Stat_High_Warn': self.Stat_High_Warn})
        result.update({'Stat_Low_Warn': self.Stat_Low_Warn})
        result.update({'Cfg_Return_Auto': self.Cfg_Return_Auto})

        return result

    def write_values(self):
        # Inputs
        set_int(self._buffer, 0, self.Raw_Input)
        set_real(self._buffer, 2, self.Def_High_Range)
        set_real(self._buffer, 6, self.Def_Low_Range)
        set_real(self._buffer, 10, self.Def_High_Proc)
        set_real(self._buffer, 14, self.Def_Low_Proc)
        set_real(self._buffer, 18, self.Def_High_Warn)
        set_real(self._buffer, 22, self.Def_Low_Warn)
        set_int(self._buffer, 26, self.Def_Num_Samp)
        set_time(self._buffer, 28, self.Def_Sample_Time)
        set_time(self._buffer, 32, self.Def_Range_Timer)
        set_time(self._buffer, 36, self.Def_Proc_Timer)
        set_time(self._buffer, 40, self.Def_Warn_Timer)
        set_bool(self._buffer, 44, 0, self.Cmd_Reset_Alarm)
        # Outputs
        # set_real(self._buffer, 46, self.Stat_PV)
        # set_bool(self._buffer, 50, 0, self.Stat_High_Range)
        # set_bool(self._buffer, 50, 1, self.Stat_Low_Range)
        # Static
        set_bool(self._buffer, 52, 0, self.Cmd_Clear_Table)
        set_bool(self._buffer, 52, 1, self.Cmd_Filter_En)
        set_bool(self._buffer, 52, 2, self.Cmd_Auto)
        set_bool(self._buffer, 52, 3, self.Cmd_Sim)
        set_bool(self._buffer, 52, 4, self.Cmd_Proc_En)
        set_bool(self._buffer, 52, 5, self.Cmd_Warn_En)
        set_bool(self._buffer, 52, 6, self.Cmd_Alarm_En)
        set_real(self._buffer, 54, self.Cmd_Sim_Value)
        set_real(self._buffer, 58, self.Cfg_High_Range)
        set_real(self._buffer, 62, self.Cfg_Low_Range)
        set_real(self._buffer, 66, self.Cfg_Scale_Offset)
        set_real(self._buffer, 70, self.Cfg_High_Proc)
        set_real(self._buffer, 74, self.Cfg_Low_Proc)
        set_real(self._buffer, 78, self.Cfg_High_Warn)
        set_real(self._buffer, 82, self.Cfg_Low_Warn)
        set_time(self._buffer, 86, self.Cfg_Range_Timer)
        set_time(self._buffer, 90, self.Cfg_Proc_Timer)
        set_time(self._buffer, 94, self.Cfg_Warn_Timer)
        set_int(self._buffer, 98, self.Cfg_Num_Of_Samp)
        set_time(self._buffer, 100, self.Cfg_Sample_time)
        # set_bool(self._buffer, 104, 0, self.Stat_Auto)
        # set_bool(self._buffer, 104, 1, self.Stat_Sim)
        # set_int(self._buffer, 106, self.Stat_Raw)
        # set_real(self._buffer, 108, self.Stat_Scale)
        # set_bool(self._buffer, 112, 0, self.Stat_Fault)
        # set_bool(self._buffer, 112, 1, self.Stat_High_Proc)
        # set_bool(self._buffer, 112, 2, self.Stat_Low_Proc)
        # set_bool(self._buffer, 112, 3, self.Stat_High_Warn)
        # set_bool(self._buffer, 112, 4, self.Stat_Low_Warn)
        set_time(self._buffer, 114, self.Cfg_Return_Auto)

        return self._buffer


class DataType(enum.IntEnum):
    Integer8 = 1  # 1
    Unsigned8 = 2  # 1
    Integer16 = 3  # 2
    Unsigned16 = 4  # 2
    Unsigned32 = 5  # 4
    FloatingPoint32 = 6  # 4


class SINAMICS:
    def __init__(self, ip_address: str = '192.168.60.56', rack: int = 0, cpu_slot: int = 0, tcp_port: int = 102):
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

    def read_area(self, area: Area, db_number: int, start_byte: int, number_of_bytes: int) -> bytearray:
        """
        Read a data area from a PLC: DB, Inputs, Outputs, Memory, Timers and Counters.

        Args:
            area: area to be read from.
            db_number: The DB number, only used when area=Areas.DB
            start_byte: byte index to start reading.
            number_of_bytes: number of bytes to read.

        Returns:
            Buffer with the data read.
        """
        try:
            return self._plc.read_area(area, db_number, start_byte, number_of_bytes)
        except Exception as e:
            print(e)

    def write_area(self, area: Area, db_number: int, start_byte: int, data: bytearray) -> int:
        """
        Writes a data area into a PLC.

        Args:
            area: area to be written.
            db_number: number of the db to be written to. In case of Inputs, Marks or Outputs, this should be equal to 0
            start_byte: byte index to start writing.
            data: buffer to be written.

        Returns:
            Snap7 error code.
        """
        try:
            self._plc.write_area(area, db_number, start_byte, data)
        except Exception as e:
            print(e)

    def read_param(self, param_no: int, param_data_type: DataType, param_idx: int = 0):
        """
        DB<param_no>.DB<param_data_type><offset>

        where:
        <param_no> … is G120X parameter number without index
        <param_data_type> … is a DB offset size depending on Data type.
        <offset> … for SINAMICS G120X is calculated as 1024+<param_idx>

        :param param_no:
        :param param_data_type:
        :param param_idx:
        :return:
        """

        offset = 1024 + param_idx

        try:
            if param_data_type == DataType.Integer8:
                # print('Integer8', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=1)
                return get_byte(buffer, 0)

            if param_data_type == DataType.Unsigned8:
                # print('Unsigned8', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=1)
                return get_byte(buffer, 0)

            if param_data_type == DataType.Integer16:
                # print('Integer16', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=2)
                return get_int(buffer, 0)

            if param_data_type == DataType.Unsigned16:
                # print('Unsigned16', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=2)
                return get_word(buffer, 0)

            if param_data_type == DataType.Unsigned32:
                # print('Unsigned32', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=4)
                return get_dword(buffer, 0)

            if param_data_type == DataType.FloatingPoint32:
                # print('FloatingPoint32', param_data_type)
                buffer = self.read_area(area=Area.DB,
                                        db_number=param_no,
                                        start_byte=offset,
                                        number_of_bytes=4)
                return round(get_real(buffer, 0), 2)

        except Exception as e:
            print(e)

    def write_param(self, buffer: bytearray, data: Union[int, float], param_no: int, param_data_type: DataType,
                    param_idx: int = 0):
        """
        DB<param_no>.DB<param_data_type><offset>

        where:
        <param_no> … is G120X parameter number without index
        <param_data_type> … is a DB offset size depending on Data type.
        <offset> … for SINAMICS G120X is calculated as 1024+<param_idx>

        :param buffer:
        :param data:
        :param param_no:
        :param param_data_type:
        :param param_idx:
        :return:
        """

        offset = 1024 + param_idx

        try:
            if param_data_type == DataType.Integer8 or param_data_type == DataType.Unsigned8:
                set_byte(buffer, offset, data)
            if param_data_type == DataType.Integer16 or param_data_type == DataType.Unsigned16:
                set_int(buffer, offset, data)
            if param_data_type == DataType.Unsigned32:
                set_dint(buffer, offset, data)
            if param_data_type == DataType.FloatingPoint32:
                set_real(buffer, offset, data)

            self.write_area(area=Area.DB,
                            db_number=param_no,
                            start_byte=offset,
                            data=buffer)

        except Exception as e:
            print(e)

    def write_values(self, params):
        try:
            for param in params:
                buffer = self.read_area(area=Area.DB,
                                        db_number=params[param]['number'],
                                        start_byte=1024 + params[param]['index'],
                                        number_of_bytes=DataType[params[param]['data_type']])

                set_int(buffer, 0, params[param]['value'])

                self.write_area(area=Area.DB,
                                db_number=params[param]['number'],
                                start_byte=1024 + params[param]['index'],
                                data=buffer)
        except Exception as e:
            print(e)

    def read_values(self, params):
        try:
            result = {}
            for param in params.keys():
                temp = params[param]
                temp.update({'Value': self.read_param(param_no=params[param]['Number'],
                                                      param_data_type=DataType[params[param]['Data Type']],
                                                      param_idx=params[param]['Index'])})
                result.update({param: temp})
            return result
        except Exception as e:
            print(f'ERROR ', e)
