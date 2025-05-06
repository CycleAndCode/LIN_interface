import json

try:
    with open('config.json', 'r') as json_file:
        config_dict = json.load(json_file)
except FileNotFoundError:
    print("Plik config.json nie został znaleziony.")
    config_dict = {}
    
default_value = None

ldf_filename = config_dict.get('ldf_filename', default_value)
get_frames = config_dict.get('get_frames', default_value)
linis = config_dict.get('linis', default_value)
frames_to_send = config_dict.get('frames_to_send', default_value)
waitBetweenFrames = config_dict.get('waitBetweenFrames', default_value)
waitBetweenFrameblocks = config_dict.get('waitBetweenFrameblocks', default_value)
log_interval = config_dict.get('log_interval', default_value)
selected_log_signals = config_dict.get('selected_log_signals', default_value)
dig_of_precision = config_dict.get('dig_of_precision', default_value)

print(config_dict)
print('===========================================================')

for item in config_dict.keys():
    print(f'{item}: {config_dict[item]}  ')
    print("============================================")

