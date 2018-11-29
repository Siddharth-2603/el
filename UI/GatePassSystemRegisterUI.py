import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry

class GateSystemPassUI:
    fields = ["UID", "Nama", "Expired Date"]
    entries = []

    def __init__(self, root):
        self.root = root
        ents = self.make_form()
        self.root.bind('<Return>', (lambda event, e = ents : self.get_entry_fields()))

        b1 = tk.Button(self.root, text="Exit", command=self.root.quit)
        b1.pack(side=tk.RIGHT, padx=5, pady=5)

        b2 = tk.Button(self.root, text="Submit", command=(lambda e=ents: self.get_entry_fields()))
        b2.pack(side=tk.RIGHT, padx=5, pady=5)

    def make_form(self):
        for field in self.fields:
            row = tk.Frame(self.root)
            lab = tk.Label(row, width=15, text=field, anchor='w')
            if field.lower() == "expired date":
                self.entryDate = tk.Entry(row)
                self.entryDate.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                self.entryDate.bind("<Button-1>", (lambda event, e = self.entryDate : self.input_datepicker()))
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
        for entry in self.entries:
            field = entry[0]
            text = entry[1].get()
            print(field,":", text)

    def input_datepicker(self):
        self.top = tk.Toplevel(self.root)
        cal = Calendar(self.top, font="Arial 12", selectmode='day', cursor="hand1")
        cal.pack(fill="both", expand=True)
        ttk.Button(self.top, text="OK", command=(lambda e = cal : self.get_input_datepicker(cal.selection_get()))).pack()

    def get_input_datepicker(self, text):
        self.entryDate.delete(0, tk.END)
        self.entryDate.insert(0, text)
        self.top.destroy()

    def input_only_numeric(self, event):
        temp = str(self.uid.get())
        if not temp.isdigit():
            print("input must be numberic only.")
            self.uid.delete(len(temp)-1, tk.END)