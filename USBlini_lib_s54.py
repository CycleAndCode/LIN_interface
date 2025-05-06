import func_timeout
from func_timeout import func_set_timeout, FunctionTimedOut
import time
import datetime
import binascii
from tkinter import *
import ldfparser
from usblini import USBlini, USBliniError
from libusb1 import libusb_error
import os
import multiprocessing
import json

class libusb_error(Exception):
    def __init__(self):
        Exception.__init__(self)

def initialize(linino, serialno = None, baudno = 19200):
    my_lini = USBlini()
    my_lini.open(serialnumber = serialno)
    my_lini.set_baudrate(baudno)
    my_lini.serialnumber = serialno #add attribute
    my_lini.baudrate = baudno #add attribute
    my_lini.linino = linino
    msg = "initialized USBlini no: " + str(linino) + " serial number: " + serialno
    print(msg)
    return(my_lini)

@func_set_timeout(2.0)
def reinitialize(my_lini):
    serialno = my_lini.serialnumber
    baudno = my_lini.baudrate
    linino = my_lini.linino
    try:
        try:
            deinitialize(my_lini)
        except FunctionTimedOut:
            msg = 'Deinitialize_Timeout'
            print(msg)
        except:
            pass
        my_lini.open(serialnumber = serialno)
        my_lini.reset()
        my_lini.set_baudrate(baudno)        
        msg = f'reinitialized_USBlini_no:_{linino}_serial_number:_{serialno}'
        print(msg)
    except:
        msg = 'Reinitialize_Error'
#         print(msg)
    return(msg)

@func_set_timeout(2.0)
def set_frame0(my_lini, frameadr, framedata = "", CHSM_MODE = "E"):
    if CHSM_MODE == "E":
        checksumtype = my_lini.CHECKSUM_MODE_LIN2
    elif CHSM_MODE == "C":
        checksumtype = my_lini.CHECKSUM_MODE_LIN1
    else:
        msg = f'Checksum_Error: Checksum mode "{CHSM_MODE}" is not supported, choose "E"(Enchanced) or "C"(Classic)'
        print(msg)
        return(msg)
    
    try:
        data = my_lini.master_write(int(frameadr,16), checksumtype, binascii.unhexlify(framedata) )
        strdata = str(binascii.hexlify(data))
    except USBliniError:
        strdata = 'USBlini_Error'
    except libusb_error:
        strdata = reinitialize(my_lini)
    except:
        strdata = reinitialize(my_lini)
        
    if len(framedata) == 0:
        msg = "received: " + frameadr + ": " + strdata
    else:
        msg = "send: " + frameadr + ": " + strdata
    #print(msg)
    return(msg)
    
def set_frame(my_lini, frameadr, framedata = "", CHSM_MODE = "E"):
    try:
        msg = set_frame0(my_lini, frameadr, framedata, CHSM_MODE)
        return(msg)
    except FunctionTimedOut:
        try:
            msg = reinitialize(my_lini)
        except FunctionTimedOut:
            msg = 'Reinitialize_Timeout'
        except:
            msg = 'Unknown_Error'
        warning = 'Timeout_Error'
        msg = msg + '_' + warning
        return(msg)
    except:
        try:
            msg = reinitialize(my_lini)
        except FunctionTimedOut:
            msg = 'Timeout_Error'
        except:
            msg = 'Unknown_Error'
        warning = 'Timeout_Error'
        msg = msg + '_' + warning
        return(msg)
#    print(msg)
#    return(msg)

@func_set_timeout(2.0)
def deinitialize0(my_lini):
    linino = my_lini.linino
    try:
        my_lini.close()
        msg = f'closed USBlini no: {linino} with serial number: {my_lini.serialnumber} '
    except:
        msg = f'Error_while_closing_USBlini_no:_{linino}_with_serial_number:_{my_lini.serialnumber}'
    return(msg)

def deinitialize(my_lini):
    linino = my_lini.linino
    try:
        msg = deinitialize0(my_lini)
    except:
        msg = f'TimeoutError_while_closing_USBlini_no:_{linino}_with_serial_number:_{my_lini.serialnumber}'
    print(msg)
    return(msg)

def formatResponse(string):
#     response example:
#     send: A: b'c83c64c8643f14004b'
#     received: C: b'e0ffffffffffffffd2'
#     received: C: b''
#     send: A: USBlini_Error
#     received: C: USBlini_Error
    lista = string.split(':')
    try:
        lista[0] = lista[0].replace("send","t").replace("received","r")
        lista[1] = lista[1].replace(" ","").replace(" ","")
        lista[2] = lista[2].replace(" b'","").replace("'","").replace(" ","").replace(" ","")
        while len(lista[1])<3:
            lista[1] = f'0{lista[1]}'
        pl = int((len(lista[2]) - 2) / 2)
        if pl < 0:
            pl = 0
    #     if 'Error' in lista[2]:
    #         pl = 0
    #         lista[2] = f'_{lista[2]}'
        not_hex = ('g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
        for char in not_hex:
            if char in lista[2]:
                pl = 0
                lista[2] = f'_{lista[2]}'
                break
        formatFrame = f'{lista[1]}{pl}{lista[2]}'   
        return(lista[0], formatFrame)
    except:
        return("Error with input:", string)
def formatResponse2(string):
#     input response example:
#     send: A: b'c83c64c8643f14004b'
#     received: C: b'e0ffffffffffffffd2'
#     received: C: b''
#     send: A: USBlini_Error
#     received: C: USBlini_Error
#    string = "send: A: b'c83c64c8643f14004b'"
    frame = {}
    try:
        lista = string.split(':')
        lista[2] = lista[2].replace(" b'","").replace("'","")
        #lista[2] = lista[2][0:-2]    
        i = 0
        for item in lista:
            lista[i] = item.strip()
            i = i + 1
        #print(lista)
        # ['send', 'A', 'c83c64c8643f14004b']
     
        frame['adr'] = hex(int(lista[1], 16))
        try:
            frame['data'] = binascii.hexlify(binascii.unhexlify(lista[2]))
            frame['data'] = frame['data'][0:-2]    #cut off the checksum
        except:
            frame['data'] = lista[2]
        frame['status'] = lista[0]
        #print(frame)
        # {'adr': '0xa', 'data': b'c83c64c8643f14004b', 'status': 'send'}
    except:
        frame = {'adr': '', 'data': string, 'status': 'format2_error'}
    return(frame)

def USBlini_process(linino, linis, frame, frames_to_send, resultFileNames, waitBetweenFrames, waitBetweenFrameblocks, time1, ts0, baudno, running_event, stop_event, process_error_event, process_log_flags, selected_log_signals, dig_of_precision):
#     MojaNazwaProcesu = f'USBlini_process_no_{linino}'
#     print(f'USBlini_process_no_{linino} PID is: {os.getpid()}')    
    process_error_event[linino].clear()
    filepath = f'Results/{resultFileNames[linino]}'
    temp_filepath = f'temp_files/temp_{resultFileNames[linino]}'
    shared_signals = {}
    try:
        my_lini = initialize(linino, linis[linino], baudno)
    except:
        msg = f'error while initializing USBlini linino: {linino}, serial: {linis[linino]}'
        print(msg)
    Error = False       #flag used to restart the process after 10s in case if sth goes wrong
    Error_time = 0      #time stamp when the error occured, used to calculate the duration of the error event
    Error_time_limit_s = 10     #after this time in s while Error == True, the process_error_event will be .set(), what will try to terminate and restart the process
    while not stop_event.is_set():
        shared_signals = {}
        if running_event.is_set():
            try:
                if process_log_flags[linino].is_set():
                    time.sleep(waitBetweenFrameblocks)
                    ct = datetime.datetime.now()
                    ts = time.time() - ts0
                    try:
                        with open(filepath, 'a') as plik:
                            plik.write(f'{ct}\t{ts}\t')
                    except:
                        msg = f'Error writing time to file on linino: {linino}'
                        print(msg)
                    for frame_ts in frames_to_send:
                        time.sleep(waitBetweenFrames)
                        adr = frame_ts[0]
                        dat = frame_ts[1]
                        CKM = frame_ts[2]
                        try:
                            resp = set_frame(my_lini, adr, dat, CKM)
                            if 'USBlini' not in resp:                                
                                if 'rror' in resp:
                                    if not Error:
                                        Error = True
                                        Error_time = time.time()
                                else:
                                    Error = False
                            else:
                                Error = False                                    
                        except:
                            resp = {'adr': '', 'data': 'error', 'status': 'error'}
                        respo = formatResponse(resp)      # tuple (lista[0], formatFrame)
                        try:
                            with open(filepath, 'a') as plik:
                                plik.write(f'{respo[0]}\t{respo[1]}\t')
                        except:
                            msg = f'Error writing data to file on linino: {linino}'
                            print(msg)                          
                        respons = formatResponse2(resp) # {'adr': '0xa', 'data': b'c83c64c8643f14004b', 'status': 'send'}
                        try:
                            adre = int(respons['adr'], 16)
                            data = binascii.unhexlify(respons['data'])
                        except:
                            adre = 0
                            data = respons['data']
                        status = respons['status']
                        #if status == 'send':
                        if status == 'received':
                            try:
                                if selected_log_signals == []:
                                    decoded_signals = frame[adre].decode(data)
                                else:
                                    decoded_signals0 = frame[adre].decode(data)
                                    decoded_signals = {}
                                    for signal in decoded_signals0.keys():
                                        if signal in selected_log_signals:
                                            decoded_signals[signal] = decoded_signals0[signal]
                                for signal in decoded_signals.keys():
                                    try:
                                        decoded_signals[signal] = round(decoded_signals[signal], dig_of_precision)
                                    except:
                                        pass
                                for signal in decoded_signals.keys():
                                    shared_signals[signal] = decoded_signals[signal]
                                print(f'linino: {linino}, serial: {linis[linino]}, frame: {respo[1]}, dec.signals: {decoded_signals}')
#                                 print(shared_signals)
                                #print(decoded_signals)
                            except:
                                decoded_signals = {'error' : 'decode_error'}
#                                 shared_signals = decoded_signals
                            for signal in decoded_signals.keys():
                                value = decoded_signals[signal]
                                try:
                                    with open(filepath, 'a') as plik:
                                        plik.write(f'{signal}\t{value}\t')
                                except:
                                    msg = f'Error writing data to file on linino: {linino}'
                                    print(msg)
                    with open(temp_filepath, 'w') as plik:
                        plik.write(f'{ct} {str(dict(sorted(shared_signals.items())))}')                    
                    try:
                        with open(filepath, 'a') as plik:
                            plik.write('\n')
                    except:
                        pass
                    process_log_flags[linino].clear()
                else:
                    time.sleep(waitBetweenFrameblocks)
                    for frame_ts in frames_to_send:
                        time.sleep(waitBetweenFrames)
                        adr = frame_ts[0]
                        dat = frame_ts[1]
                        CKM = frame_ts[2]
                        try:
                            resp = set_frame(my_lini, adr, dat, CKM)
                        except:
                            pass
                if Error:
                    if time.time() - Error_time > Error_time_limit_s:
                        process_error_event[linino].set()
            except:
                try:
                    time.sleep(0.5)
                    initialize(linino, linis[linino], baudno)
                    print(f'try to initialize linino: {linino}, serial: {linis[linino]}')
                except:
                    print(f'process fatal error on linino: {linino}, serial: {linis[linino]}')
                    process_error_event[linino].set()          
        else:
            ct = datetime.datetime.now()
            with open(temp_filepath, 'w') as plik:
                plik.write(f'{ct}  Interface paused')                                
    deinitialize(my_lini)

def log_flag(log_interval, process_log_flags):
    lininos = []
    for linino in process_log_flags.keys():
        lininos.append(linino)
    current_time = time.time()
    next_log_time = current_time
    while True:
        current_time = time.time()
        if current_time >= next_log_time:
            for linino in process_log_flags.keys():
                process_log_flags[linino].set()
            next_log_time = next_log_time + log_interval
    
# ===================================================================================================================
if __name__ == "__main__":
    ts0 = time.time()
# ========= LINE FOR SUPPORT MULTIPROCESSING IN EXE MODE =====================
    multiprocessing.freeze_support()    
# ========= OPTION PARSE CODE ===================
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c','--config',dest = 'config',
                      help='the .json config filename (include extension)')    
    parser.add_option('-r','--running',dest = 'running',
                      help='set the initial running status (0 by default)')
    parser.add_option('-n','--name',dest = 'name',
                      help='text to be added to the filaname')
    parser.add_option('-t','--time',dest = 'test_time',
                      help='time of sending and logging in seconds')
    parser.add_option('-d','--delay',dest = 'init_delay',
                      help='start delay in seconds. Use this option to compensate the delay caused by initialization')
    (options,args) = parser.parse_args()
    
# ========= .json import code ===================
#     if options.config is None:
#         config_filename = 'config.json'
#     else:
#         config_filename = options.config        
    config_filename = options.config if options.config is not None else 'config.json'

    with open(config_filename, 'r') as json_file:
        config_dict = json.load(json_file)    
    
    default_value = None
    ldf_filename = config_dict.get('ldf_filename', default_value)
    get_frames = config_dict.get('get_frames', default_value)
    linis = config_dict.get('linis', default_value)
    frames_to_send = config_dict.get('frames_to_send', default_value)
    waitBetweenFrames = config_dict.get('waitBetweenFrames', default_value)
    waitBetweenFrameblocks = config_dict.get('waitBetweenFrameblocks', default_value)
    log_interval = config_dict.get('log_interval', default_value)
    selected_log_signals = config_dict.get('selected_log_signals', [])
#     selected_log_signals = set(selected_log_signals)
    dig_of_precision = config_dict.get('dig_of_precision', default_value)
    additional_file_description = config_dict.get('additional_file_description', '')
    start_delay_in_s = config_dict.get('start_delay_in_s', 0)
    test_time_in_s = config_dict.get('test_time_in_s', 0) 
    running = config_dict.get('running', False)
    
    ldf = {}
    for item in ldf_filename.keys():
        ldf[item] = ldfparser.parse_ldf(path = ldf_filename[item])
        baudno = ldf[item].get_baudrate()
    for item in ldf.keys():
        baudno = ldf[item].get_baudrate()
    frame = {}
    for ldf_id in get_frames.keys():
        for frame_id in get_frames[ldf_id]:
            frame[frame_id] = ldf[ldf_id].get_unconditional_frame(frame_id)
    
    for item in frames_to_send:
        if isinstance(item[1], dict):
            item[1] = binascii.hexlify(frame[int(item[0],16)].encode(item[1]))
    
    linis = linis.strip()
    linis = [x.strip() for x in linis.splitlines()]
    linis = dict(enumerate(linis, 1))
#     del linis[0]
    deletecandidate = []
    for key in linis.keys():
        if linis[key].startswith('#'):
            deletecandidate.append(key)
    for item in deletecandidate:
        del linis[item]
    # print(linis)
# ========= OVERWRITE OPTIONS FROM OPTION PARSER ===================
    additional_file_description = f'_{options.name}' if options.name is not None else additional_file_description
    start_delay_in_s = int(options.init_delay) if options.init_delay is not None else start_delay_in_s
    test_time_in_s = int(options.test_time) if options.test_time is not None else test_time_in_s
    running = bool(int(options.running)) if options.running is not None else running
    
# ========= FOLDER SETUP CODE ===================
    required_folders = {"Results", "temp_files"}
    for nazwa_folderu in required_folders:
        if os.path.exists(nazwa_folderu):
            print(f'Wymagany folder "{nazwa_folderu}" istnieje.')
        else:
            os.mkdir(nazwa_folderu)
            if os.path.exists(nazwa_folderu):
                print(f'Folder "{nazwa_folderu}" został utworzony pomyślnie.')
            else:
                print(f'Nie udało się utworzyć folderu "{nazwa_folderu}"')

# ========= LOGGER CODE =========================    
#     for linino in linis.keys():
#         initialize(linino, linis[linino], baudno)
        
    resultFileNames = {}
    ct = datetime.datetime.now()
    
    for linino in linis.keys():
        timestamp = str(ct).replace(':','.').replace(' ','_')
        fname = f'{timestamp}_results_{linino}_{linis[linino]}{additional_file_description}.txt'
        resultFileNames[linino] = fname
        
# ========= INTERFACE CODE =====================
    from tkinter import *
    import tkinter as tk
#     running = False  # Global flag
    time0 = ts0
    time1 = time0

    def start():
        """Enable scanning by setting the global flag to True."""
#         print('START was pressed!!!')
        global running
        running = True

    def stop():
        """Stop scanning by setting the global flag to False."""
#         print('STOP was pressed!!!')
        global running
        running = False

    root = Tk()
    root.title("USBlini LIN logger")
    root.geometry("1800x900")

    app = Frame(root)
    app.grid()

    start_button = Button(app, text="Start logging", command=start)
    stop_button = Button(app, text="Pause logging", command=stop)
    
    start_button.grid(row=0, column=0, padx=10, pady=2)
    stop_button.grid(row=1, column=0, padx=10, pady=2)

    USBlini_process_status = Entry(app, width=300)
    USBlini_process_status.grid(pady=2)

    USBlini_data = {}
    for linino in linis.keys():
        USBlini_data[linino] = Entry(app, width=300)
        USBlini_data[linino].grid(pady=2)
#         USBlini_data[linino].grid(row=1, column=0, padx=10, pady=10)
    
#     USBlini_data[3].delete(0, 'end')
#     USBlini_data[3].insert(0, 'hi there')
#     
#     USBlini_data[3].delete(0, 'end')
#     USBlini_data[3].insert(0, 'hi somfing els')
    
# ========= LOOP CODE===========================

# ========= MULTIPROCESSING CODE ================
#     import multiprocessing
       
    processes = {}
    process_args = {}
    process_log_flags = {}
    running_event = multiprocessing.Event()
    running_event.clear()
    stop_event = multiprocessing.Event()
    process_error_event = {}
    for linino in linis.keys():
        process_error_event[linino] = multiprocessing.Event()
        process_error_event[linino].clear()
        
    for linino in linis.keys():
        process_log_flags[linino] = multiprocessing.Event()
        process_log_flags[linino].clear()
    
    for linino in linis.keys():
    #for linino in (1,):
        process_args[linino] = (linino, linis, frame, frames_to_send, resultFileNames, waitBetweenFrames, waitBetweenFrameblocks, time1, ts0, baudno, running_event, stop_event, process_error_event, process_log_flags, selected_log_signals, dig_of_precision)
        process = multiprocessing.Process(target=USBlini_process, args=process_args[linino])
        processes[linino] = process
        processes[linino].start()
    
    log_flag_process_args = (log_interval, process_log_flags)
    log_flag_process = multiprocessing.Process(target=log_flag, args=log_flag_process_args)
    log_flag_process.start()
    
    mainpid = os.getpid()
    
    initialization_time = time.time() - time0
    msg = f'init time is: {initialization_time} seconds, init delay is set to: {start_delay_in_s} seconds'
    print(msg)
    while time.time() - time0 < start_delay_in_s:
        print('.', end = '')
#         print('.')
        time.sleep(0.1)
    print('.')
    print(f'\'running\' is set to: {running}')
    
    time_start_of_logging = time.time()
    while running != None:
        time2 = time.time()
        if running == True:
            running_event.set()
        if running == False:
            running_event.clear()
        process_status_string = f'Main PID: {mainpid}, Log flag PID: {log_flag_process.pid}, Process status {datetime.datetime.now()}: '
        if log_flag_process.is_alive():
            stat = "Alive"
        if not log_flag_process.is_alive():
            stat = "Dead"
        process_status_string = process_status_string + f'| 0 : {stat} |'
        for linino in sorted(processes.keys()):
            if processes[linino].is_alive():
                stat = "Alive"
            try:
                if process_error_event[linino].is_set():
                    stat = "Error"
            except:
                pass
            if not processes[linino].is_alive():
                stat = "Dead"
            if False:
                process_status_string = process_status_string + f'| {linino} : {stat}_{processes[linino].pid} |'
            else:
                process_status_string = process_status_string + f'| {linino} : {stat} |'
        try:
            USBlini_process_status.delete(0, 'end')
            USBlini_process_status.insert(0, process_status_string)
        except:
            pass
        if not log_flag_process.is_alive():
            try:
                log_flag_process.terminate()
            except:
                print(f'failed to terminate log flag process')
            try:
                log_flag_process_args = (log_interval, process_log_flags)
                log_flag_process = multiprocessing.Process(target=log_flag, args=log_flag_process_args)
                log_flag_process.start()
            except:
                print(f'failed to start log flag process')
        for linino in processes.keys():
            if process_error_event[linino].is_set() and processes[linino].is_alive():
                try:
                    processes[linino].terminate()
                except:
                    print(f'failed to terminate process of linino {linino} PID: {processes[linino].pid}')
            if not processes[linino].is_alive():
                processes[linino] = None
                del processes[linino]
                process = multiprocessing.Process(target=USBlini_process, args=process_args[linino])
                processes[linino] = process
                processes[linino].start()
                print(f'process of linino {linino} revived, new PID: {processes[linino].pid}')
            try:
                temp_filepath = f'temp_files/temp_{resultFileNames[linino]}'
                with open(temp_filepath, 'r') as plik:
                    # string = plik.readline()
                    string = plik.read()
                    string = string.strip()
#                     print(f'LIN {linino}, PID {processes[linino].pid}: {string}')
                if len(string) > 0:
                    USBlini_data[linino].delete(0, 'end')
                    USBlini_data[linino].insert(0, f'LIN {linino}, PID {processes[linino].pid}: {string}')                  
            except:
                pass
        if time2-time1 - 0.2 > 1:
            time1 = time2
            try:
                root.update()
            except TclError:     #error occured when the window is closed with "x"
                running = None
                stop_event.set()
        time.sleep(0.01)
        
        if test_time_in_s is not 0:
            if time.time() - time_start_of_logging > test_time_in_s:
                root.destroy()
                running = None

#     for process in processes:
#         processes[linino].join()
    log_flag_process.terminate()
    for linino in processes.keys():
        processes[linino].terminate()
        
# ========= FINALIZE PROGRAM ====================              
    print('Program finalized.')
# ========= END OF CODE =========================
