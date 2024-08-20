import os
import datetime
import time
import threading
import snap7
from snap7.util import *
from snap7.type import *


class S7_Manager:
    def __init__(self, ip_address: str = '192.168.0.3', rack: int = 0, cpu_slot: int = 1, tcp_port: int = 102):
        self._ip_address = ip_address
        self._rack = rack
        self._cpu_slot = cpu_slot
        self._tcp_port = tcp_port

        self._plc = snap7.client.Client()
        self._plc.connect(self._ip_address, self._rack, self._cpu_slot)
        print(self._plc.get_connected())
        # print(self._path)

    # get info from plc
    def get_cpu_info(self):
        with self._plc as plc:
            return plc.get_cpu_info()

    # get tag list from plc
    def get_tag_list(self):
        pass
        # with self._plc as plc:
        #     return plc.get_tag_list()

    def get_tag_list_json(self):
        pass
        # with self._plc as plc:
        #     return plc.tags_json

    def read_single_tag(self, tag_name: str = 'testDINT'):
        pass
        # # Reading a single tag returns a Tag object
        # # e.g. Tag(tag='testDINT', value=20, type='DINT', error=None)
        #
        # with self._plc as plc:
        #     result = plc.read(tag_name)
        #     # print(result)
        #     if result.error is None:
        #         # print(f'{datetime.datetime.now()}\t|\tReading successfully from \t{tag_name}: {result.value:.2f}')
        #         return result.value
        #     else:
        #         print(f'{datetime.datetime.now()}\t|\tError reading from \t{tag_name}: {result.error}')
        #         return None

    def read_multiple_tags(self, tag_names: list = ['testDINT', 'testSine']):
        pass
        # # Reading multiple tags returns a list of Tag objects
        # # e.g. [Tag(tag='testDINT', value=20, type='DINT', error=None),
        # #       Tag(tag='testSine', value=100.36, type='REAL', error=None)]
        #
        # values = []
        # with self._plc as plc:
        #     results = plc.read(*tag_names)
        #
        #     for tag_name, result in zip(tag_names, results):
        #         if result.error is None:
        #             values.append(result.value)
        #         else:
        #             print(f'Error reading {tag_name}: {result.error}')
        #             values.append(None)
        #
        # return values

    def read_udt(self, inst_name: str = 'Tank1'):
        pass
        # # Structures can be read as a whole, assuming that no attributes have External Access set to None.
        # # Structure tags will be a single Tag object, but the value attribute will be a dict of {attribute: value}.
        # # e.g. Tag(tag='Tank1', value={'Level': 100.5, 'Level_EU': "ft", 'Volume': 1000, 'Volume_EU': "gal"},
        # #          type='udtTank', error=None)
        #
        # with self._plc as plc:
        #     return plc.read(inst_name)

    def write_single_tag(self, tag_name: str = 'testSine', tag_value=None):
        pass
        # # Writing a single tag returns a single Tag object response
        # # e.g. Tag(tag='testSine', value=100.5, type='REAL', error=None)
        #
        # with self._plc as plc:
        #     result = plc.write((tag_name, tag_value))
        #     # print(result)
        #
        # if result.error is None:
        #     # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
        #     return result.value
        # else:
        #     print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
        #     return None

    def read_db(self, db_number: int, start: int, size: int):
        return self._plc.db_read(db_number, start, size)

    def write_multiple_tags(self, tag_names: list = ['testSine', 'testDINT'], tag_values: list = [None, None]):
        pass
        # # Writing multiple tags will return a list of Tag objects
        # # e.g. [Tag(tag='testSine', value=25.2, type='REAL', error=None),
        # #       Tag(tag='testDINT', value=20, type='DINT', error=None)]
        #
        # with self._plc as plc:
        #     data = list(zip(tag_names, tag_values))
        #     results = plc.write(*data)
        #     # print(type(result),result)
        #
        # for tag_name, result in zip(tag_names, results):
        #     if result.error is None:
        #         # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
        #         return result.value
        #     else:
        #         print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
        #         return None

    def get_block_info(self):
        pass
        # print(snap7.client.Client().get_block_info(snap7.type.Block.DB, 363))
        block_type = BlocksList['DB']  # Tipo de bloque (ejemplo: DB)
        block_number = 363  # Número del bloque (ejemplo: DB1)

        block_info = self._plc.get_block_info(block_type, block_number)
        print(block_info)
