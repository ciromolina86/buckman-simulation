from handlers.comm_handler import *
import snap7
from snap7.type import Area


def main():
    plc = S7_Manager(ip_address='192.168.0.1')
    print(plc.get_cpu_info())

    print("read 1: original data")
    db2_bytearray = plc.read_area(Area.DB, 2, 0, 416)  # read db raw data from PLC
    db2 = Analog_Filt_Scale(db2_bytearray)  # interpret raw data as Analog_Filt_Scale object
    print(db2.read_values())  # read values from Analog_Filt_Scale object
    db2.Cfg_High_Range = 999.0  # modify attributes
    db2.Cfg_Low_Range = 111.0  # modify attributes
    db2.Cfg_High_Proc = 888.0  # modify attributes
    db2.Cfg_Low_Proc = 222.0  # modify attributes
    db2.Cfg_High_Warn = 777.0  # modify attributes
    db2.Cfg_Low_Warn = 333.0  # modify attributes
    print(db2.read_values())
    db2_bytearray = db2.write_values()  # write Analog_Filt_Scale object attribute values to raw data
    plc.write_area(Area.DB, 2, 0, db2_bytearray)  # write db raw data to PLC

    print("read 2: modified data")
    db2_bytearray_ = plc.read_area(Area.DB, 2, 0, 416)
    db2_ = Analog_Filt_Scale(db2_bytearray_)
    print(db2_.read_values())


def solisPLC_read_db():
    plc = snap7.client.Client()
    plc.connect('192.168.0.1', 0, 1)

    # reading 8 bytes from db 1
    result_bytearray = plc.db_read(2, 0, 50)

    # extracting values from result byte array
    # bool1 = snap7.util.get_bool(result_bytearray, 0, 0)
    # int1 = snap7.util.get_int(result_bytearray, 2)
    real1 = snap7.util.get_real(result_bytearray, 46)

    # print(f"bool1 = {bool1} \nint1 = {int1} \nreal1 = {real1}")
    print(f"stat_pv = {real1}")


def solisPLC_write_db():
    plc = snap7.client.Client()
    plc.connect('192.168.0.1', 0, 1)

    # reading 8 bytes from db 1
    result_bytearray = plc.db_read(1, 0, 8)

    # modifying the real1 value on the result byte array
    snap7.util.set_real(result_bytearray, 4, 1236.78)

    # writing the result byte array with the modified real value to PLC
    plc.db_write(1, 0, result_bytearray)


def g120():
    plc = S7_Manager(ip_address='192.168.60.56', rack=0, cpu_slot=0)
    # print(plc.get_cpu_info())

    print("read 1: original data")
    buffer = plc.read_area(Area.DB, 27, 1024, 4)  # read db raw data from PLC
    current = round(get_real(buffer, 0), 2)
    print(current, 'A')



    # db2 = Analog_Filt_Scale(buffer)  # interpret raw data as Analog_Filt_Scale object
    # print(db2.read_values())  # read values from Analog_Filt_Scale object
    # db2.Cfg_High_Range = 999.0  # modify attributes
    # db2.Cfg_Low_Range = 111.0  # modify attributes
    # db2.Cfg_High_Proc = 888.0  # modify attributes
    # db2.Cfg_Low_Proc = 222.0  # modify attributes
    # db2.Cfg_High_Warn = 777.0  # modify attributes
    # db2.Cfg_Low_Warn = 333.0  # modify attributes
    # print(db2.read_values())
    # buffer = db2.write_values()  # write Analog_Filt_Scale object attribute values to raw data
    # plc.write_area(Area.DB, 2, 0, buffer)  # write db raw data to PLC
    #
    # print("read 2: modified data")
    # db2_bytearray_ = plc.read_area(Area.DB, 2, 0, 416)
    # db2_ = Analog_Filt_Scale(db2_bytearray_)
    # print(db2_.read_values())

if __name__ == "__main__":
    # main()
    g120()

