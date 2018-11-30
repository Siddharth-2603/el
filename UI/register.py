from UI.src.GatePassSystemRegisterUI import *
import sys

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*Dialog.msg.width', 15)
    root.title("Registration Form")
    root.geometry("350x150")
    root.resizable(0, 0)
    try:
        program_directory = sys.path[0]
        # root.iconphoto(True, tk.PhotoImage(file=os.path.join(program_directory, "src/icons/mPay-icon.png")))
        img = tk.PhotoImage(file=os.path.join(program_directory, "src/icons/mPay-icon.png"))
        root.tk.call('wm', 'iconphoto', root._w, img)
        # root.wm_iconbitmap(bitmap="@/home/takeru/Documents/My-Projects/Python/gate-pass/UI/src/icons/Account-Card-Blue.ico")
        gate = GateSystemPassRegisterUI(root)
        tk.mainloop()
    except tk.TclError as err:
        showerror("Error", "No Icon File Found.")
