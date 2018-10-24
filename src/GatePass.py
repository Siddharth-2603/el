from src.config import *

import mysql.connector
import datetime
import re
import os
import xlsxwriter

class GatePass :
    flagError = False
    errMessage = ""

    def __init__(self):
        self.db = self.connect_to_database()
        if(self.flagError == False) :
            self.db_cursor = self.db.cursor()

    def connect_to_database(self):
        try :
            db = mysql.connector.connect(
                host=host,
                user=username,
                passwd=password,
                database=db_name
            )
            return db
        except :
            self.flagError = True
            self.errMessage = "Error : cannot connect to database"
            print(self.errMessage)

    def get_current_datetime(self):
        return datetime.datetime.now()

    def get_full_current_datetime(self):
        return "[" + self.get_current_datetime().strftime("%a, %d %b %Y %H:%M:%S") + "]"

    def insert_data_to_database(self, code, dt):
        try :
            sql = "INSERT INTO entries (code, dt_scan) VALUES (%s, %s)"
            value = (code, dt)
            self.db_cursor.execute(sql, value)
            self.db.commit()

            message = "Success : record inserted."
            print(message)
            return message
        except :
            self.flagError = True
            self.errMessage = "Error : failed to insert data to database."
            print(self.errMessage)
            return self.errMessage

    def get_log_filename(self):
        return "Log_" + self.get_current_datetime().strftime("%Y-%m-%d") + ".txt"

    def post_log_txt(self, code="", dt="", status=""):
        try :
            if self.check_log_file_is_exist(self.get_log_filename()) :
                type = "a+"
            else :
                type = "w+"
            f = open(path_dir_log + self.get_log_filename(), type)
            f.write(dt + "\nCode : " + code + "\n" + status + "\n\n")
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
            columns = ['No.', 'Date/Time', 'Code', 'Status']
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
                        code = str(input(dt + " Scan Code : "))
                        current_dt = self.get_current_datetime()
                        input_code = re.sub(r"\W", "", code).replace("B", "")
                        if code != "" :
                            status = self.insert_data_to_database(input_code, current_dt)
                            self.post_log_txt(input_code, dt, status)
                        else :
                            status = "Invalid Code."
                            print(status)
                            self.post_log_txt(code, dt, status)
                        print("\n")
                    else :
                        print(self.errMessage)
                        self.post_log_txt("", dt, self.errMessage)
                        break
            else :
                print(self.errMessage)
                self.post_log_txt("", dt, self.errMessage)
        except KeyboardInterrupt:
            print("\nProgram is exit.")