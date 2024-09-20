import json
import pandas as pd

from handlers.comm_handler import *


def get_chars(name: str):
    return [ord(char) for char in name]


def set_device_name(device_name):
    list_chars = get_chars(device_name)


def read_changed_params():
    sinamics_g120 = SINAMICS(ip_address='192.168.60.56')

    with open('changed_params_config.json', 'r') as file:
        params = json.load(file)

    changed_params_990 = []
    changed_params_991 = []

    for idx in range(0, 100, 1):
        for param in params.keys():
            params[param]["index"] = idx

        temp = sinamics_g120.read_values(params)
        changed_params_990.append(temp['r0990']['value'])
        changed_params_991.append(temp['r0991']['value'])
        time.sleep(0.1)

    print(f'changed_params_990 ({len(set(changed_params_990))}): {set(changed_params_990)}')
    print(f'changed_params_991 ({len(set(changed_params_991))}): {set(changed_params_991)}')


def read_ref_params():
    sinamics_g120 = SINAMICS(ip_address='192.168.60.56')

    df = pd.read_excel('g120-drive-parameters.xlsx', sheet_name='Reference', index_col='Parameter')

    params = df.to_dict(orient='index')
    # print(params)

    return sinamics_g120.read_values(params)

    # todo
    # df = pd.DataFrame(params)
    # df.to_excel('g120-drive-parameters.xlsx', sheet_name='Reference')


def write_commissioning_params():
    sinamics_g120 = SINAMICS(ip_address='192.168.60.57')
    df = pd.read_excel('g120-drive-parameters.xlsx', sheet_name='Sheet1', index_col='Parameter')
    params = df.to_dict(orient='index')
    sinamics_g120.write_values(params)


def read_all_params():
    sinamics_g120 = SINAMICS(ip_address='192.168.60.56')
    df = pd.read_excel('g120-drive-parameters.xlsx', sheet_name='Parameters', index_col='Parameter')
    params = df.to_dict(orient='index')
    params = sinamics_g120.read_values(params)
    df = pd.DataFrame.from_dict(params, orient='index')
    df.to_excel('g120-drive-parameters.xlsx', sheet_name='Parameters', index=True, index_label='Parameter')


def main():
    # read_ref_params()
    # write_commissioning_params()
    read_all_params()


if __name__ == "__main__":
    main()

    """     WRITE PARAMETERS
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
    """

    """     READ PARAMETERS

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
    p2004 - Reference power (kW)
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

    Communication
    r0052 - CO/BO: Status word 1
    r0054 - CO/BO: Control word 1
    r2050 - CO: PROFIdrive PZD receive word ()
    """
