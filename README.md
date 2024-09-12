the purpose of this scripts is to read and write Siemens datablocks (non-optimized) 

here is an example of how to use it:

plc = S7_Manager(ip_address='192.168.0.1')
db2_bytearray = plc.read_area(Area.DB, 2, 0, 416)  # read db raw data from PLC
db2 = Analog_Filt_Scale(db2_bytearray)  # interpret raw data as Analog_Filt_Scale object

db2.Cfg_High_Range = 999.0  # modify attributes
db2.Cfg_Low_Range = 111.0  # modify attributes
db2.Cfg_High_Proc = 888.0  # modify attributes
db2.Cfg_Low_Proc = 222.0  # modify attributes
db2.Cfg_High_Warn = 777.0  # modify attributes
db2.Cfg_Low_Warn = 333.0  # modify attributes

db2_bytearray = db2.write_values()  # write Analog_Filt_Scale object attribute values to raw data
plc.write_area(Area.DB, 2, 0, db2_bytearray)  # write db raw data to PLC
