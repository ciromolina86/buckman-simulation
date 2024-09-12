from handlers.comm_handler import *
import snap7
from snap7.type import Area


def main():
    plc = S7_Manager(ip_address='192.168.0.3')
    print(plc.get_cpu_info())

    print("read 1: original data")
    db363_bytearray = plc.read_area(Area.DB, 363, 0, 416)  # read db raw data from PLC
    db363 = Analog_Filt_Scale(db363_bytearray)  # interpret raw data as Analog_Filt_Scale object
    print(db363)    # read values from Analog_Filt_Scale object
    db363.Raw_Input = 26000.0  # modify attributes
    db363.Cfg_High_Range = 150.0  # modify attributes
    db363.Cfg_Low_Range = 0.0   # modify attributes
    db363.Cfg_High_Proc = 120.0   # modify attributes
    db363.Cfg_Low_Proc = 30.0    # modify attributes
    db363.Cfg_High_Warn = 100.0   # modify attributes
    db363.Cfg_Low_Warn = 50.0    # modify attributes
    # print(db363.read_values())
    db363_bytearray = db363.write_values()  # write Analog_Filt_Scale object attribute values to raw data
    plc.write_area(Area.DB, 363, 0, db363_bytearray)  # write db raw data to PLC

    print("read 2: modified data")
    db363_bytearray_ = plc.read_area(Area.DB, 363, 0, 416)
    db363_ = Analog_Filt_Scale(db363_bytearray_)
    print(db363_)


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


if __name__ == "__main__":
    main()

