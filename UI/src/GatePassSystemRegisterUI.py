import tkinter as tk
import mysql.connector
from tkinter import ttk
from tkcalendar import Calendar
from tkinter.messagebox import *

from UI.src.GatePassSystem import *


class GateSystemPassRegisterUI:
    fields = ["UID", "Nama", "Expired Date"]
    entries = []

    def __init__(self, root):
        self.count_window = 0
        self.root = root
        ents = self.make_form()
        self.root.bind('<Return>', (lambda event, e=ents: self.get_entry_fields()))

        b1 = tk.Button(self.root, text="Exit", command=self.exit_program, bg="red", fg='white')
        b1.pack(side=tk.RIGHT, padx=5, pady=5)

        b2 = tk.Button(self.root, text="Submit", command=(lambda e=ents: self.submit_data_to_database()), bg='green', fg='white')
        b2.pack(side=tk.RIGHT, padx=5, pady=5)

    def make_form(self):
        for field in self.fields:
            row = tk.Frame(self.root)
            lab = tk.Label(row, width=15, text=field, anchor='w')
            if field.lower() == "expired date":
                self.entryDate = tk.Entry(row)
                self.entryDate.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                self.entryDate.bind("<Button-1>", (lambda event, e=self.entryDate: self.input_datepicker()))
                lab.pack(side=tk.LEFT)
                self.entries.append((field, self.entryDate))
            elif field.lower() == "uid":
                self.uid = tk.Entry(row)
                self.uid.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                self.uid.bind("<KeyRelease>", self.input_only_numeric)
                lab.pack(side=tk.LEFT)
                self.entries.append((field, self.uid))
            else:
                entry = tk.Entry(row)
                entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                self.entries.append((field, entry))
                lab.pack(side=tk.LEFT)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        return self.entries

    def get_entry_fields(self):
        data = []
        is_valid = True
        warning_message = ""
        for entry in self.entries:
            field = entry[0]
            if field.lower() == "expired date":
                text = entry[1].get() + " 23:59:59"
            else:
                text = entry[1].get()
            if text != "" and text != " 23:59:59":
                data.append(text)
            else:
                is_valid = False
                warning_message = "Warning : " + field + " Harus Diisi."
                break
        if is_valid:
            return data
        else:
            return warning_message

    def input_datepicker(self):
        self.count_window += 1
        if self.count_window < 2:
            self.top = tk.Toplevel(self.root)
            self.top.protocol("WM_DELETE_WINDOW", self.set_count_window)
            cal = Calendar(self.top, font="Arial 12", selectmode='day', cursor="hand1")
            cal.pack(fill="both", expand=True)
            ttk.Button(self.top, text="OK", command=(lambda e=cal: self.get_input_datepicker(cal.selection_get()))).pack()

    def get_input_datepicker(self, text):
        self.reset_count_window()
        self.entryDate.delete(0, tk.END)
        self.entryDate.insert(0, text)
        self.top.destroy()

    def input_only_numeric(self, event):
        temp = str(self.uid.get())
        if not temp.isdigit():
            print("input must be numberic only.")
            self.uid.delete(len(temp) - 1, tk.END)

    def submit_data_to_database(self):
        data = self.get_entry_fields()
        if type(data) != str:
            gps = GatePassSystem()
            uid = data[0]
            name = data[1]
            expired_dt = data[2]
            if gps.flagError == False:
                if gps.has_been_registered(uid):
                    showwarning("Warning", "UID '" + uid + "' Already Registered.")
                else:
                    result = gps.insert_data_to_database(uid, name, expired_dt)
                    if gps.flagError:
                        showerror("Failed", result)
                    else:
                        showinfo("Success", result)
            else:
                showerror("Failed", "Cannot connect to database.")
        else:
            showwarning("Warning", data)

    def reset_count_window(self):
        self.count_window = 0

    def set_count_window(self):
        self.reset_count_window()
        self.top.destroy()

    def exit_program(self):
        if askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
