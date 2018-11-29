from UI.GatePassSystemRegisterUI import *

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Registration Form")
    root.geometry("350x150")
    root.resizable(0,0)
    # s = ttk.Style(root)
    # s.theme_use('clam')

    gate = GateSystemPassRegisterUI(root)
    tk.mainloop()