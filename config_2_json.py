# ====== LDF setup ============
# import toml
import json

ldf_filename = {
    'LED': "LED_LDF_FILENAME.ldf",
    'SENSOR': "SENSOR_LDF_FILENAME.ldf"
    }
get_frames = {
    'LED': (0xA, 0xC),
    'SENSOR': (0x1, 0x2)
    }
# ========= FRAME SETUP =========================    
CKM = 'E'
# CKM (Checksum) options: 'E' - Enchanced, 'C' - Classic
waitBetweenFrames = 0.0     # 10 ms acc. ldf
waitBetweenFrameblocks = 0.0
log_interval = 1.0   # [s]

signals = {}

signals[0xA] = {
    'CIL1_Int_Hi_Rq_ST3' : 15.0,
    'CIL1_Int_Lo_Rq_ST3' : 0.0,
    'CIL1_Red_Val_Rq_ST3' : 100.0,
    'CIL1_Blu_Val_Rq_ST3' : 45.0,
    'CIL1_Grn_Val_Rq_ST3' : 90.0,
    'CIL1_Blnk_Fd_Tm_ST3' : 0.0,
    'CIL1_FuncMd_Rq_ST3' : 'ON',
    'CIL1_Hold_Tm_ST3' : 0.0
    }

frames_to_send = [
    # ('frame_hex_ID', 'frame_DATA', 'CHECKSUM_MODE'),
    ['1', '', CKM],
    ['2', '', CKM],
#         ['A', '1E00C85AB4200000', CKM],
    ['A', signals[0xA], CKM],
    ['C', '', CKM]
    ]

# ONLY this signals from received frames will be decoded and logged and printed in the terminal.
# to decode and log all signals from received frames, make this set empty or comment it
# selected_log_signals = []
selected_log_signals = [
    'CIS_DC_DCplus_Temp_ST3',
    'CIS_DC_DCminus_Temp_ST3',
    'CIS_DC_AC_Temp_ST3',
    'CIL1_Occur_ST3'
    ]

#     frames_to_send = (
#         # ('frame_ID', 'frame_DATA', 'CHECKSUM_MODE'),
#         ('A', '1E3C14A0C83F1400', CKM),
#         ('C', '', CKM),
#         ('A', 'C83CC864643F1400', CKM),
#         ('C', '', CKM),
#         ('A', 'C83C6464C83F1400', CKM),
#         ('C', '', CKM),
#         ('A', 'C83C64C8643F1400', CKM),
#         ('C', '', CKM)   
#         )

#     baudno = 9600
#     CKM = 'C'
#     waitBetweenFrames = 0.3
#     waitBetweenFrameblocks = 0.0
#     frames_to_send = (
#         ('1B', '', CKM),
#         ('26', '', CKM)
#         )
# ========= HARDWARE SETUP ======================
# można zakomentować nieużywane interfejsy w standardowy sposób
linis = """

152D1567   
152D3A79   
152D0CBB
152D9361
152D3717
152D20F8

"""   
# ========= OTHER ======================
dig_of_precision = 3
additional_file_description = ''
start_delay_in_s = 0
test_time_in_s = 0       #takes action only if running is set to True. 0 means run forever
running = True           #False means that you need to push the "start" button. True runs immediately after start_delay_in_s is elapsed

# ========= JSON DUMP ===================
config_dict = {
    'ldf_filename': ldf_filename,
    'get_frames': get_frames,
    'linis': linis,
    'frames_to_send': frames_to_send,
    'waitBetweenFrames': waitBetweenFrames,
    'waitBetweenFrameblocks': waitBetweenFrameblocks,
    'log_interval': log_interval,
    'selected_log_signals': selected_log_signals,
    'dig_of_precision': dig_of_precision,
    'additional_file_description': additional_file_description,
    'start_delay_in_s': start_delay_in_s,
    'test_time_in_s': test_time_in_s,
    'running': running
}

# with open('config.toml', 'w') as toml_file:
#     toml.dump(config_dict, toml_file)
    
with open('config.json', 'w') as json_file:
    json.dump(config_dict, json_file, indent=4)
    
print('config.json successfully created')
