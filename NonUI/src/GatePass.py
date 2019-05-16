from src.config import *
from gpiozero import Button

import mysql.connector
import datetime
import re
import os
import xlsxwriter
import socket, fcntl, struct, io
import requests

class GatePass :
    flagError = False
    errMessage = ""

    def __init__(self):
        self.db = self.connect_to_database()
        if(self.flagError == False) :
            self.button = Button(gpio_button)
            self.db_cursor = self.db.cursor(buffered=True)

    def connect_to_database(self):
        try :
            db = mysql.connector.connect(
                host=host,
                user=username,
                passwd=password,
                database=db_name,
#                unix_socket=unix_socket
            )
            return db
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            print(self.errMessage)
            return self.errMessage

    def get_current_datetime(self):
        return datetime.datetime.now()

    def get_full_current_datetime(self):
        return "[" + self.get_current_datetime().strftime("%a, %d %b %Y %H:%M:%S") + "]"

    def get_added_expired_date(self, days):
        temp = self.get_current_datetime() + datetime.timedelta(days=added_expired_date)
        return temp.strftime("%Y-%m-%d %H:%M:%S")

    def set_format_datetime(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def has_been_registered(self, uid):
        try:
            sql = "SELECT id FROM members WHERE uid = " + str(uid)
            self.db_cursor.execute(sql)
            member_id = self.db_cursor.fetchone()

            if member_id is not None:
                return True
            else:
                return False
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            print(self.errMessage)
            return self.errMessage

    def insert_data_to_database(self, code, dt):
        try :
            # get Gate ID first
            gate_id = -1
            ip_address_device = self.get_ip_address()

            if ip_address_device != '':
                sql = "SELECT id FROM gates WHERE ip_address = '" + str(ip_address_device) + "';"
                self.db_cursor.execute(sql)
                gate_id = self.db_cursor.fetchone()[0]

            if gate_id != -1:
                # insert data into 'members' table
                sql = "INSERT INTO members (uid, expired_dt, created, modified) VALUES (%s, %s, %s, %s)"
                expired_date = self.get_added_expired_date(added_expired_date)
                value = (code, expired_date, dt, dt)
                self.db_cursor.execute(sql, value)
                self.db.commit()

                # insert data into 'member_details' table
                sql = "INSERT INTO member_details (member_id, gate_id, created, modified) VALUES (LAST_INSERT_ID(), %s, %s, %s)"
                value = (gate_id, dt, dt)
                self.db_cursor.execute(sql, value)
                self.db.commit()

                message = "Success : record inserted."
                print(message)
                return message
            else:
                message = "Error : Invalid Gate ID."
                print(message)
                return message
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            print(err)
            return self.errMessage
        
    def open_barrier_gate(self):
        try:
            param = {"code":700}
            response = requests.post(url_barrier_gate, json=param, timeout=timeout_connection)
            response.raise_for_status()
            response_data = response.json()
            print(self.get_full_current_datetime(), response_data['message'])
        except requests.exceptions.ConnectionError :
            print("Cannot establish connection to server, please setup the server properly.")
            self.retry_connect()
        except requests.exceptions.Timeout as err_timeout :
            print(err_timeout)
            self.retry_connect()
        except requests.exceptions.HTTPError as err_http :
            print(err_http)
            self.retry_connect() 
            
    def retry_connect(self):
        x = retry_connect
        while(x >= 1) :
            print("Retrying connect to server in " + str(x) + " second ...")
            sleep(1)
            x -= 1
        print("Reconnecting ...")
        self.main()

    def check_validity(self, code):
        try :
            # check if UID is registered
            sql = "SELECT id FROM members WHERE uid = '" + str(code) + "';"
            self.db_cursor.execute(sql)
            member_id = self.db_cursor.fetchone()

            # if UID registered, then check expired date
            if member_id is not None:
                member_id = member_id[0]
                sql = "SELECT id FROM members WHERE id = " + str(member_id) + " AND NOW() <= expired_dt;"
                self.db_cursor.execute(sql)
                member_id = self.db_cursor.fetchone()
                if member_id is not None and member_id != "":
                    message = "UID is valid"
                    print(message)
                    self.open_barrier_gate()
                    return message
                else:
                    self.errMessage = "UID is expired."
                    print(self.errMessage)
                    return self.errMessage
            else:
                self.errMessage = "UID is not registered yet."
                print(self.errMessage)
                return self.errMessage
        except mysql.connector.Error as err:
            self.flagError = True
            self.errMessage = err
            print(err)
            return self.errMessage

    def get_ip_address(self, ifname=''):
        if self.is_raspberry_pi():
            ifname = "eth0"
        else:
            ifname = "enp3s0"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_address = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
        return str(ip_address)

    def is_raspberry_pi(self, raise_on_errors=False):
        try:
            with io.open('/proc/cpuinfo', 'r') as cpuinfo:
                found = False
                for line in cpuinfo:
                    if line.startswith('Hardware'):
                        found = True
                        label, value = line.strip().split(':', 1)
                        value = value.strip()
                        if value not in (
                                'BCM2708',
                                'BCM2709',
                                'BCM2835',
                                'BCM2836'
                        ):
                            if raise_on_errors:
                                raise ValueError(
                                    'This system does not appear to be a '
                                    'Raspberry Pi.'
                                )
                            else:
                                return False
                if not found:
                    if raise_on_errors:
                        raise ValueError(
                            'Unable to determine if this system is a Raspberry Pi.'
                        )
                    else:
                        return False
        except IOError:
            if raise_on_errors:
                raise ValueError('Unable to open `/proc/cpuinfo`.')
            else:
                return False
        return True

    def get_log_filename(self):
        return "Log_" + self.get_current_datetime().strftime("%Y-%m-%d") + ".txt"

    def post_log_txt(self, code="", dt="", status=""):
        try :
            if self.check_log_file_is_exist(self.get_log_filename()) :
                type = "a+"
            else :
                type = "w+"
            f = open(path_dir_log + self.get_log_filename(), type)
            f.write(dt + "\nCode : " + str(code) + "\n" + str(status) + "\n\n")
            f.close()
        except IOError :
            self.flagError = True
            if self.check_log_file_is_exist(self.get_log_filename()) :
                self.errMessage = "Error : cannot append the file."
            else :
                self.errMessage = "Error : cannot create the file."
            print(self.errMessage)

    def check_log_file_is_exist(self, filename):
        if os.path.exists(path_dir_log + filename) :
            return True
        else :
            return False

    def set_log_file_to_list(self, full_path_log):
        result = []
        try :
            temp = open(full_path_log, 'r').readlines()
            temp = list(filter(lambda a: a != "\n", temp))
            for text in temp :
                if text.endswith("\n") :
                    replaced_text = text.replace("\n", "")
                    if 'Code : ' in replaced_text :
                        replaced_text = replaced_text.replace("Code : ", "")
                    result.append(replaced_text)
            return result
        except IOError:
            self.flagError = True
            self.errMessage = "Error : cannot open file '" + full_path_log + "'"
            return self.errMessage

    def export_log_to_excel(self, log_filename=""):
        try :
            if log_filename == "" :
                full_path_log = path_dir_log + self.get_log_filename()
                file_excel_name = self.get_log_filename().replace(".txt", "")
            else :
                if self.check_log_file_is_exist(log_filename) == False :
                    self.flagError = True
                    self.errMessage = "Error : file or directory not found. \nMaybe you forgot the extension? (example.txt)"
                    print(self.errMessage)
                    return
                full_path_log = path_dir_log + log_filename
                file_excel_name = log_filename.replace(".txt", "")
            data_log = self.set_log_file_to_list(full_path_log)

            full_path_excel = path_dir_log_excel + file_excel_name + ".xlsx"
            workbook = xlsxwriter.Workbook(full_path_excel)
            worksheet = workbook.add_worksheet()

            # widen the columns
            worksheet.set_column('B:B', 40)
            worksheet.set_column('C:C', 40)
            worksheet.set_column('D:D', 40)

            style_title = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'center'})

            # create the column title
            columns = ['No.', 'Date/Time', 'UID', 'Status']
            for i, title in enumerate(columns) :
                worksheet.write(0, i, title, style_title)

            # append the data
            row = 1
            col = 1
            counter = 1
            style_data = workbook.add_format({'align': 'center', 'valign': 'center'})
            for data in data_log :
                worksheet.write(row, col, data, style_data)
                col += 1
                if col > 3 :
                    col = 1
                    worksheet.write(row, 0, counter, style_data)
                    row += 1
                    counter += 1

            workbook.close()
            print("Successfully export log to Excel File : '" + full_path_excel + "'.")
        except :
            self.flagError = True
            self.errMessage = "Error : failed to export log into excel file."
            print(self.errMessage)

    def main_entry(self):
        try :
            dt = self.get_full_current_datetime()
            if self.flagError == False :
                while True :
                    if self.flagError == False :
                        code = str(input(dt + " Scan UID : "))
                        current_dt = self.get_current_datetime()
                        input_code = re.sub(r"\W", "", code).replace("B", "")
                        if code != "" :
                            if self.button.is_pressed:
                                if not self.has_been_registered(input_code):
                                    status = self.insert_data_to_database(input_code, current_dt)
                                else:
                                    status = "Warning: UID is already registered."
                                    print(status)
                            else:
                                status = self.check_validity(input_code)
                        else :
                            status = "Invalid UID."
                            print(status)
                        self.post_log_txt(code, dt, status)
                        print("\n")
                    else :
                        print(self.errMessage)
                        self.post_log_txt("", dt, self.errMessage)
                        break
            else :
                self.post_log_txt("", dt, self.errMessage)
        except KeyboardInterrupt:
            print("\nProgram is exit.")