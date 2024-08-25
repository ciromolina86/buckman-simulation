from handlers.comm_handler import *
import snap7
from snap7.type import Area, BlocksList, Block

def test1():
    # Dirección IP del PLC y otros parámetros de conexión
    PLC_IP = '192.168.0.1'  # Cambia esta dirección IP por la dirección IP de tu PLC
    RACK = 0  # Rack donde está el PLC
    SLOT = 1  # Slot donde está el PLC

    # Crear una instancia del cliente
    plc = snap7.client.Client()

    # Conectar al PLC
    plc.connect(PLC_IP, RACK, SLOT)

    # Verificar si la conexión fue exitosa
    if plc.get_connected():
        print("Conectado al PLC")

        # Leer la información de un bloque específico
        block_type = BlocksList['DB']  # Tipo de bloque (ejemplo: DB)
        block_number = 1  # Número del bloque (ejemplo: DB1)

        try:
            block_info = plc.get_block_info(block_type, block_number)

            # Mostrar la información obtenida
            print("Block Type:", block_info.BlockType)
            print("Block Number:", block_info.BlockNumber)
            print("Length:", block_info.Length)
            print("Load Size:", block_info.LoadSize)
            print("MC7 Size:", block_info.MC7Size)
            print("Load Memory Address:", block_info.LoadMemoryAddress)
            print("Local Data:", block_info.LocalData)
            print("SBB Length:", block_info.SBBLength)
            print("Checksum:", block_info.Checksum)
            print("Version:", block_info.Version)

        except snap7.snap7exceptions.Snap7Exception as e:
            print(f"Error al obtener la información del bloque: {e}")

        # Desconectar del PLC
        plc.disconnect()

    else:
        print("No se pudo conectar al PLC")


def main():
    plc = S7_Manager(ip_address='192.168.0.1')
    print(plc.get_cpu_info())
    db2_bytearray = plc.read_area(Area.DB, 2, 0, 416)
    db2 = Analog_Filt_Scale(db2_bytearray)
    print(db2)

    # result = plc.
    # print(result)
    # print(snap7.util.get_real(result,46))
    # print(plc.read_area())


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
    # solisPLC_read_db()
    # solisPLC_write_db()
    # solisPLC_read_db()
