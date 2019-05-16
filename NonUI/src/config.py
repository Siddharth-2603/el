# Database Configuration
host = "localhost"
username = "takeru"
password = "takeru123"
db_name = "gate_pass_system"
#unix_socket = "/opt/lampp/var/mysql/mysql.sock"
added_expired_date = 30 # in day(s) from current date

# Log
path_dir_log = "/home/pi/Documents/python/gate-pass/logs/"
path_dir_log_excel = "/home/pi/Documents/python/gate-pass/logs/excel/"

# GPIO Configuration
gpio_button = 2 # GPIO-2

# Barrier Gate
url_barrier_gate = "http://192.168.88.88:23567"
timeout_connection = 10 # in second(s)