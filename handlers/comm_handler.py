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
    Integer8 = 1
    Integer16 = 2
    Unsigned8 = 1
    Unsigned16 = 2
    Unsigned32 = 4
    FloatingPoint32 = 4


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
            buffer = self.read_area(area=Area.DB,
                                    db_number=param_no,
                                    start_byte=offset,
                                    number_of_bytes=param_data_type)

            if param_data_type == DataType.Integer8 or param_data_type == DataType.Unsigned8:
                return get_byte(buffer, 0)
            if param_data_type == DataType.Integer16 or param_data_type == DataType.Unsigned16:
                return get_int(buffer, 0)
            if param_data_type == DataType.Unsigned32:
                return get_dint(buffer, 0)
            if param_data_type == DataType.FloatingPoint32:
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

    def write_values(self):
        """
        Commissioning
        p003 - Access level
        p010 - Drive commissioning parameter filter
        p100 - IEC/NEMA Standards (0: IEC (50 Hz line, SI units), 1: NEMA (60 Hz line, US units), 2: NEMA (60 Hz line, SI units)),
        p210 - Drive unit line supply voltage (380 ... 480 V),
        p300 - Motor type selection (1: Induction motor),
        p301 - Motor code (0 = enter motor data),
        p304 - Rated motor voltage (Vrms),
        p305 - Rated motor current (Amps),
        p307 - Rated motor power (kW),
        p308 - Rated motor power factor,
        p309 - Rated motor efficiency (%),
        p310 - Rated motor frequency (Hz),
        p311 - Rated motor speed (rpm),
        p322 - Maximum motor speed (rpm)
        p323 - Maximum motor current (Amps)
        p332 - Rated motor power factor
        p335 - Motor cooling (0: Natural ventilation, 1: Forced cooling)
        p500 - Technology application (1: Pumps and fans, 3: Pumps and fans, efficiency optimization)
        p501 - Technological application (Standard Drive Control) (0: Constant load (linear characteristic), 1: Speed-dependent load (parabolic characteristic))
        p502 - Technological application (Dynamic Drive Control) (3: Pumps and fans, efficiency optimization)
        p015 - Macro drive unit
        p1080 - Minimum speed (rpm)
        p1082 - Maximum speed (rpm)
        p758[0, 1, 2, 3] - CU analog inputs characteristic value y1 ([0] = AI0 (X132 3/4), [1] = AI1 (X132 10/11))
        p1120 - Ramp-function generator ramp-up time (s)
        p1121 - Ramp-function generator ramp-down time (s)
        p1135 - OFF3 ramp-down time (s)
        p1300 - Open-loop/closed-loop control operating mode (0: U/f control with linear characteristic, 2: U/f control with parabolic characteristic, 20: Speed control (encoderless))
        p1900 - Motor data identification and rotating measurement (2: Identifying motor data (at standstill))

        p1000 - Speed setpoint selection (0: No main setpoint, 1: Motorized potentiometer, 2: Analog setpoint, 6: Fieldbus)
        p1070 - CI: Main setpoint ([0] 2050[1], [1] 0, [2] 0, [3] 0)

        Energy
        p0040 - Reset energy consumption display
        p0043 - BI: Enable energy usage display

        Communication
        p2030 - Field bus interface protocol selection (0: No protocol, 7: PROFINET, 10: EtherNet/IP)
        p8921[0..3] - PN IP address
        p8922[0..3] - PN Default Gateway
        p8923[0..3] - PN Subnet Mask
        p8925 - Activate PN interface configuration (0: No function, 2: Activate and save configuration)
        p8920[0..239] - PN Name of Station
        p8980 - Ethernet/IP profile (0: SINAMICS, 1: ODVA AC/DC)
        p922 - PROFIdrive PZD telegram selection (1: Standard telegram 1, PZD-2/2, 999: Free telegram configuration with BICO)
        p2079 - PROFIdrive PZD telegram selection extended (1: Standard telegram 1, PZD-2/2, 999: Free telegram configuration with BICO)
        p2051 - CI: PROFIdrive PZD send word ([0] 2089[0], [1] 63[0], [2] 27[0], [3] 32[0])

        Inverter
        p0970 - Reset drive parameters
        p0971 - Save parameters (0: Inactive, 1: Save drive object)
        p0972 - Drive unit reset (0: Inactive, 1: Hardware-Reset immediate)
        :return:
        """
        pass

    def read_values(self, params):
        """
        r0980[0...299] List of existing parameters 1
        r0981[0...299] List of existing parameters 2
        r0989[0...299] List of existing parameters 10
        r0990[0...99] List of modified parameters 1
        r0991[0...99] List of modified parameters 2
        r0999[0...99] List of modified parameters 10

        Commissioning
        p2000 - Reference speed reference frequency (rpm)
        p2001 - Reference voltage (Vrms)
        p2002 - Reference current (Arms)
        p2003 - Reference torque (Nm)
        r2004 - Reference power (kW)
        p2006 - Reference temperature (*C)

        Inverter
        r0018 - Control Unit firmware version (The value 1010100 should be interpreted as V01.01.01.00)
        r0037[0..19] - CO: Power unit temperatures (*C) ([4] = Interior of power unit)
        r0046 - CO/BO: Missing enable signal (bits)
        r0050 - CO/BO: Command Data Set CDS effective
        r0051 - CO/BO: Drive Data Set DDS effective
        r0945 - Fault Code

        Motor
        r0021 - Actual speed smoothed (rpm)
        r0024 - Output frequency smoothed (Hz)
        r0025 - Output voltage smoothed (Vrms)
        r0026 - DC link voltage smoothed (V)
        r0027 - Absolute actual current smoothed (Amps)
        r0031 - Actual torque smoothed (Nm)
        r0032 - Active power actual value smoothed (kW)
        r0035 - Motor temperature (*C)
        r0038 - Power factor smoothed
        r0039[0..2] - CO: Energy display (kWh) ([0] = Energy balance (sum), [1] = Energy drawn, [2] = Energy fed back)
        r0042[0..2] - CO: Process energy display (Wh) ([0] = Energy balance (sum), [1] = Energy drawn, [2] = Energy fed back)

        Communication
        r0052 - CO/BO: Status word 1
        r0054 - CO/BO: Control word 1
        r2050 - CO: PROFIdrive PZD receive word ()

        :return:
        """
        result = {}
        result.update({'r0021': {'param_no': 21, 'param_desc': 'Actual speed smoothed', 'value': self.read_param(param_no=21, param_data_type=DataType.FloatingPoint32, param_idx=0)}})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        result.update({'Motor Active Power': self.read_param(param_no=32, param_data_type=DataType.FloatingPoint32, param_idx=0)})
        # result.update({'Def_Low_Range': self.Def_Low_Range})
        # result.update({'Def_Low_Proc': self.Def_Low_Proc})
