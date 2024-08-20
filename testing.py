from handlers.comm_handler import S7_Manager
import snap7
from snap7.type import *

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
    plc = S7_Manager()
    print(plc)
    print(plc.get_cpu_info())
    # plc.read_db(db_number=363, start=46, size=2)
    plc.get_block_info()


if __name__ == "__main__":
    # main()
    test1()
