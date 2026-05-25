import os
os.environ["CTK_DISABLE_DARK_DETECT"] = "1"

import customtkinter as ctk
import psutil
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TaskManagerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("System Call Demonstrator - Task Manager")
        self.root.geometry("1200x700")

        # Header
        header = ctk.CTkFrame(root, height=50)
        header.pack(fill="x")

        ctk.CTkLabel(header, text="System Call Demonstrator",
                     font=("Segoe UI", 20, "bold")).pack(pady=10)

        # Tabs
        self.tabview = ctk.CTkTabview(root)
        self.tabview.pack(fill="both", expand=True)

        self.process_tab = self.tabview.add("Processes")
        self.performance_tab = self.tabview.add("Performance")
        self.system_tab = self.tabview.add("System Calls")

        # Build UI
        self.build_process_tab()
        self.build_performance_tab()
        self.build_system_tab()

        # Delay heavy load
        self.root.after(1000, self.update_processes)
        self.root.after(1000, self.update_performance)

    #PROCESS TAB 
    def build_process_tab(self):

        top_frame = ctk.CTkFrame(self.process_tab)
        top_frame.pack(fill="x", pady=5)

        self.search = ctk.CTkEntry(top_frame, placeholder_text="Search process...")
        self.search.pack(side="left", padx=10)

        ctk.CTkButton(top_frame, text="Refresh",
                      command=self.update_processes).pack(side="left")

        self.process_frame = ctk.CTkScrollableFrame(self.process_tab)
        self.process_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def update_processes(self):
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        keyword = self.search.get().lower()

        for i, proc in enumerate(psutil.process_iter(['pid', 'name', 'cpu_percent'])):
            if i > 80:
                break

            try:
                name = proc.info['name']
                if keyword in name.lower():

                    row = ctk.CTkFrame(self.process_frame)
                    row.pack(fill="x", pady=2)

                    ctk.CTkLabel(row, text=f"{proc.info['pid']}", width=80).pack(side="left")
                    ctk.CTkLabel(row, text=name, width=250, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=f"{proc.info['cpu_percent']}%", width=80).pack(side="left")

                    ctk.CTkButton(row, text="End Task",
                                  width=100,
                                  command=lambda p=proc.info['pid']: self.kill_process(p)
                                  ).pack(side="right")
            except:
                pass

        self.root.after(4000, self.update_processes)

    def kill_process(self, pid):
        try:
            os.kill(pid, 9)
        except Exception as e:
            print(e)

    #PERFORMANCE TAB 
    def build_performance_tab(self):

        self.cpu_data = []
        self.ram_data = []

        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.performance_tab)
        self.canvas.get_tk_widget().pack()

    def update_performance(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        self.cpu_data.append(cpu)
        self.ram_data.append(ram)

        if len(self.cpu_data) > 15:
            self.cpu_data.pop(0)
            self.ram_data.pop(0)

        self.ax.clear()
        self.ax.plot(self.cpu_data, label="CPU")
        self.ax.plot(self.ram_data, label="RAM")
        self.ax.legend()
        self.ax.set_title("Real-Time Performance")

        self.canvas.draw()

        self.root.after(2500, self.update_performance)

    #SYSTEM CALL TAB
    def build_system_tab(self):

        main_frame = ctk.CTkFrame(self.system_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # FILE SECTION
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(file_frame, text="File Operations",
                     font=("Segoe UI", 16, "bold")).pack(pady=5)

        self.file_entry = ctk.CTkEntry(file_frame, width=400,
                                      placeholder_text="Enter file name (example: test.txt)")
        self.file_entry.pack(pady=5)

        btn_frame1 = ctk.CTkFrame(file_frame)
        btn_frame1.pack(pady=5)

        ctk.CTkButton(btn_frame1, text="Create File", command=self.create_file).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame1, text="Read File", command=self.read_file).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame1, text="Delete File", command=self.delete_file).grid(row=0, column=2, padx=5)

        # COMMAND SECTION
        cmd_frame = ctk.CTkFrame(main_frame)
        cmd_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(cmd_frame, text="Command Execution",
                     font=("Segoe UI", 16, "bold")).pack(pady=5)

        self.cmd_entry = ctk.CTkEntry(cmd_frame, width=400,
                                     placeholder_text="Enter command (example: dir / ping google.com)")
        self.cmd_entry.pack(pady=5)

        ctk.CTkButton(cmd_frame, text="Run Command",
                      command=self.run_command).pack(pady=5)

        # OUTPUT
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(output_frame, text="Output",
                     font=("Segoe UI", 16, "bold")).pack(pady=5)

        self.output_box = ctk.CTkTextbox(output_frame, height=250)
        self.output_box.pack(fill="both", expand=True, padx=10, pady=10)

    def create_file(self):
        filename = self.file_entry.get()
        if not filename:
            self.output_box.insert("end", "Enter file name\n")
            return

        try:
            with open(filename, "w") as f:
                f.write("Created via System Call Demonstrator\n")
            self.output_box.insert("end", f"File '{filename}' created\n")
        except Exception as e:
            self.output_box.insert("end", f"Error: {e}\n")

    def read_file(self):
        filename = self.file_entry.get()
        try:
            with open(filename, "r") as f:
                content = f.read()
            self.output_box.insert("end", f"Content:\n{content}\n")
        except Exception as e:
            self.output_box.insert("end", f"Error: {e}\n")

    def delete_file(self):
        filename = self.file_entry.get()
        try:
            os.remove(filename)
            self.output_box.insert("end", f"File '{filename}' deleted\n")
        except Exception as e:
            self.output_box.insert("end", f"Error: {e}\n")

    def run_command(self):
        cmd = self.cmd_entry.get()
        if not cmd:
            self.output_box.insert("end", "Enter command\n")
            return

        try:
            result = subprocess.check_output(cmd, shell=True, text=True)
            self.output_box.insert("end", f"Output:\n{result}\n")
        except Exception as e:
            self.output_box.insert("end", f"Error: {e}\n")


# RUN APP
root = ctk.CTk()
app = TaskManagerApp(root)
root.mainloop()