from UI.src.GatePassSystemRegisterUI import *
import sys

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*Dialog.msg.width', 25)
    root.title("Registration Form")
    root.geometry("350x150")
    root.resizable(0, 0)
    try:
        program_directory = sys.path[0]
        img = tk.PhotoImage(file=os.path.join(program_directory, icon_path))
        root.tk.call('wm', 'iconphoto', root._w, img)
        gate = GateSystemPassRegisterUI(root)
        root.protocol("WM_DELETE_WINDOW", gate.exit_program)
        tk.mainloop()
    except tk.TclError as err:
        showerror("Error", "No Icon File Found.")
