from src.GatePass import *

import sys

if __name__ == "__main__" :
    try :
        gate = GatePass()
        log_filename = sys.argv[1]
        gate.export_log_to_excel(log_filename)
    except :
        gate.export_log_to_excel()