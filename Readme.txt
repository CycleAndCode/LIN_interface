To run:
1. Create a proper config.json file using a config python script
2. Run "USBlini_lib_sXX.exe". 
Caution: you need to have in the same directory:
-> the config.json file 
-> the used .ldf files

Result files can be found in the "Results" folder.

UP FROM s54, PROGRAM SUPPORTS OPTIONS:
C:\Users\mj97wq\output>USBlini_lib_s54.exe --help
Usage: USBlini_lib_s54.exe [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIG, --config=CONFIG
                        the .json config filename (include extension)
  -r RUNNING, --running=RUNNING
                        set the initial running status (0 by default)
  -n NAME, --name=NAME  text to be added to the filaname
  -t TEST_TIME, --time=TEST_TIME
                        time of sending and logging in seconds
  -d INIT_DELAY, --delay=INIT_DELAY
                        start delay in seconds. Use this option to compensate
                        the delay caused by initialization

USING OF OPTIONS IS OPTIONAL.
EXEMPLARY USAGE, RUN CMD AND:
C:\Users\mj97wq\output>USBlini_lib_s54.exe -c config2.json -r 1 d 5 t 30