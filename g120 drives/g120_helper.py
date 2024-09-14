from handlers.comm_handler import *


def main():
    sinamics_g120 = SINAMICS(ip_address='192.168.60.56')
    print(sinamics_g120.read_values())


if __name__ == "__main__":
    main()
