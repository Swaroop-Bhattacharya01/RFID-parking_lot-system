import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
from tkinter import font as tkfont
import json
import os
from PIL import Image, ImageTk

class NeonButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, e):
        self.configure(style='Neon.TButton')
        
    def on_leave(self, e):
        self.configure(style='TButton')

class ParkingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Parking System")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0a0a0a')
        
        # Load images
        self.load_images()
        
        # Set custom style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.bg_color = '#0a0a0a'
        self.fg_color = '#ffffff'
        self.neon_blue = '#00f3ff'
        self.neon_pink = '#ff00ff'
        self.neon_green = '#00ff9d'
        self.neon_yellow = '#fff700'
        self.neon_red = '#ff0000'
        self.error_color = self.neon_red
        self.success_color = self.neon_green
        self.warning_color = self.neon_yellow
        
        # Configure styles
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, 
                           font=('Segoe UI', 10))
        self.style.configure('TButton', background=self.bg_color, foreground=self.fg_color, 
                           font=('Segoe UI', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), 
                           foreground=self.neon_blue)
        self.style.configure('Status.TLabel', font=('Segoe UI', 12))
        self.style.configure('Neon.TButton', background=self.neon_blue, foreground='#000000')
        self.style.configure('TLabelframe', background=self.bg_color, 
                           foreground=self.neon_blue)
        self.style.configure('TLabelframe.Label', background=self.bg_color, 
                           foreground=self.neon_blue)
        self.style.configure('TEntry', 
                           fieldbackground='#1a1a1a',
                           foreground=self.neon_blue,
                           insertcolor=self.neon_blue)
        
        # Initialize default users
        self.default_users = [
            {
                "uid": "89 D3 9D 94",
                "name": "Swaroop",
                "role": "Admin"
            },
            {
                "uid": "13 D3 09 27",
                "name": "Tester",
                "role": "User"
            }
        ]
        
        # Create a lookup dictionary for quick user info access
        self.user_lookup = {user["uid"]: user for user in self.default_users}
        
        # Serial connection
        self.serial_port = None
        self.serial_thread = None
        self.running = False
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create left and right panels
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Create header
        self.create_header()
        
        # Create connection frame
        self.create_connection_frame()
        
        # Create parking status frame
        self.create_parking_status_frame()
        
        # Create user management frame
        self.create_user_management_frame()
        
        # Create log frame
        self.create_log_frame()
        
        # Initialize serial port list
        self.update_ports()
        
        # Load saved users and add default users if not present
        self.load_users()
        self.add_default_users()
        
    def load_images(self):
        # Load and resize images
        try:
            # You can add your own images to the images directory
            # For now, we'll use placeholder paths
            self.images = {
                'logo': self.create_image('images/logo.png', (100, 100)),
                'car': self.create_image('images/car.png', (30, 30)),
                'connected': self.create_image('images/connected.png', (20, 20)),
                'disconnected': self.create_image('images/disconnected.png', (20, 20))
            }
        except:
            self.images = {}
            
    def create_image(self, path, size):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            return None
        
    def create_header(self):
        header_frame = ttk.Frame(self.left_panel)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo
        if 'logo' in self.images:
            logo_label = ttk.Label(header_frame, image=self.images['logo'])
            logo_label.pack(side="left", padx=5)
        
        # Title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", padx=5)
        
        title_label = ttk.Label(title_frame, text="RFID Parking Management", 
                              style='Header.TLabel')
        title_label.pack(side="left", padx=5)
        
        # System status
        self.system_status = ttk.Label(header_frame, text="⚡ System Ready", 
                                     foreground=self.neon_blue, font=('Segoe UI', 12))
        self.system_status.pack(side="right", padx=5)
        
    def create_connection_frame(self):
        connection_frame = ttk.LabelFrame(self.left_panel, text="Connection", padding="15")
        connection_frame.pack(fill="x", pady=(0, 20))
        
        # Connection controls
        controls_frame = ttk.Frame(connection_frame)
        controls_frame.pack(fill="x", pady=5)
        
        # Port selection
        ttk.Label(controls_frame, text="Port:", style='Status.TLabel').pack(side="left", padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls_frame, textvariable=self.port_var, width=15)
        self.port_combo.pack(side="left", padx=5)
        
        # Refresh button
        refresh_btn = NeonButton(controls_frame, text="🔄 Refresh", command=self.update_ports)
        refresh_btn.pack(side="left", padx=5)
        
        # Connect button
        self.connect_button = NeonButton(controls_frame, text="🔌 Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=5)
        
        # Status indicator
        status_frame = ttk.Frame(connection_frame)
        status_frame.pack(fill="x", pady=5)
        
        if 'disconnected' in self.images:
            self.status_image = ttk.Label(status_frame, image=self.images['disconnected'])
            self.status_image.pack(side="left", padx=5)
            
        self.connection_status = ttk.Label(status_frame, text="Disconnected", 
                                         foreground=self.error_color, style='Status.TLabel')
        self.connection_status.pack(side="left", padx=5)
        
    def create_parking_status_frame(self):
        status_frame = ttk.LabelFrame(self.left_panel, text="Parking Status", padding="15")
        status_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create a grid for parking slots
        self.slots = []
        for i in range(4):
            slot_frame = ttk.Frame(status_frame)
            slot_frame.pack(fill="x", pady=5)
            
            # Slot number with car icon
            if 'car' in self.images:
                car_label = ttk.Label(slot_frame, image=self.images['car'])
                car_label.pack(side="left", padx=5)
            
            slot_label = ttk.Label(slot_frame, text=f"Slot {i+1}:", style='Status.TLabel')
            slot_label.pack(side="left", padx=5)
            
            # Status with color
            status_label = ttk.Label(slot_frame, text="Available", foreground=self.neon_green, 
                                   style='Status.TLabel')
            status_label.pack(side="left", padx=5)
            
            # User info
            user_info = ttk.Label(slot_frame, text="", style='Status.TLabel')
            user_info.pack(side="left", padx=5)
            
            # Time occupied
            time_label = ttk.Label(slot_frame, text="", style='Status.TLabel')
            time_label.pack(side="right", padx=5)
            
            self.slots.append((status_label, time_label, user_info))
            
    def create_user_management_frame(self):
        management_frame = ttk.LabelFrame(self.right_panel, text="User Management", padding="15")
        management_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Add user section
        add_frame = ttk.Frame(management_frame)
        add_frame.pack(fill="x", pady=5)
        
        # UID input
        ttk.Label(add_frame, text="UID:").pack(side="left", padx=5)
        self.uid_entry = ttk.Entry(add_frame, width=20)
        self.uid_entry.pack(side="left", padx=5)
        
        # Name input
        ttk.Label(add_frame, text="Name:").pack(side="left", padx=5)
        self.name_entry = ttk.Entry(add_frame, width=20)
        self.name_entry.pack(side="left", padx=5)
        
        # Role input
        ttk.Label(add_frame, text="Role:").pack(side="left", padx=5)
        self.role_entry = ttk.Entry(add_frame, width=20)
        self.role_entry.pack(side="left", padx=5)
        
        # Buttons
        button_frame = ttk.Frame(management_frame)
        button_frame.pack(fill="x", pady=5)
        
        add_permitted_btn = NeonButton(button_frame, text="✅ Add Permitted User", 
                                     command=self.add_permitted_user)
        add_permitted_btn.pack(side="left", padx=5)
        
        add_denied_btn = NeonButton(button_frame, text="❌ Add Denied User", 
                                  command=self.add_denied_user)
        add_denied_btn.pack(side="left", padx=5)
        
        # User lists
        lists_frame = ttk.Frame(management_frame)
        lists_frame.pack(fill="both", expand=True, pady=5)
        
        # Permitted users list
        permitted_frame = ttk.Frame(lists_frame)
        permitted_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # Add header frame for permitted users
        permitted_header = ttk.Frame(permitted_frame)
        permitted_header.pack(fill="x")
        
        ttk.Label(permitted_header, text="Permitted Users:", style='Status.TLabel').pack(side="left")
        clear_permitted_btn = NeonButton(permitted_header, text="🗑️ Clear", command=self.clear_permitted_users)
        clear_permitted_btn.pack(side="right")
        
        self.permitted_list = tk.Listbox(permitted_frame, width=40, height=10,
                                       bg='#1a1a1a', fg=self.neon_green,
                                       selectbackground=self.neon_blue)
        self.permitted_list.pack(fill="both", expand=True)
        
        # Denied users list
        denied_frame = ttk.Frame(lists_frame)
        denied_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # Add header frame for denied users
        denied_header = ttk.Frame(denied_frame)
        denied_header.pack(fill="x")
        
        ttk.Label(denied_header, text="Denied Users:", style='Status.TLabel').pack(side="left")
        clear_denied_btn = NeonButton(denied_header, text="🗑️ Clear", command=self.clear_denied_users)
        clear_denied_btn.pack(side="right")
        
        self.denied_list = tk.Listbox(denied_frame, width=40, height=10,
                                    bg='#1a1a1a', fg=self.neon_red,
                                    selectbackground=self.neon_blue)
        self.denied_list.pack(fill="both", expand=True)
        
    def create_log_frame(self):
        log_frame = ttk.LabelFrame(self.right_panel, text="Access Log", padding="15")
        log_frame.pack(fill="both", expand=True)
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, 
                              font=('Consolas', 10), bg='#1a1a1a', fg=self.neon_blue,
                              insertbackground=self.neon_blue)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Clear log button
        clear_btn = NeonButton(log_frame, text="🗑️ Clear Log", command=self.clear_log)
        clear_btn.pack(side="bottom", pady=5)
        
    def update_ports(self):
        # Get both port device names and descriptions
        ports = list(serial.tools.list_ports.comports())
        port_list = []
        for port in ports:
            # Format: "COM1 - USB Serial Device" or similar
            port_desc = f"{port.device} - {port.description}"
            port_list.append(port_desc)
            
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.set(port_list[0])
            # Store the actual port device name
            self.port_var.set(ports[0].device)
            
    def toggle_connection(self):
        if self.serial_port is None:
            try:
                # Extract the actual port name from the selection
                port_name = self.port_var.get().split(' - ')[0] if ' - ' in self.port_var.get() else self.port_var.get()
                self.serial_port = serial.Serial(
                    port=port_name,
                    baudrate=9600,
                    timeout=1
                )
                self.running = True
                self.serial_thread = threading.Thread(target=self.read_serial)
                self.serial_thread.start()
                self.connect_button.config(text="🔌 Disconnect")
                self.connection_status.config(text="Connected", foreground=self.success_color)
                self.system_status.config(text="⚡ System Active", foreground=self.neon_blue)
                if 'connected' in self.images:
                    self.status_image.config(image=self.images['connected'])
                self.log_message("Connected to Arduino")
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            self.running = False
            if self.serial_thread:
                self.serial_thread.join()
            self.serial_port.close()
            self.serial_port = None
            self.connect_button.config(text="🔌 Connect")
            self.connection_status.config(text="Disconnected", foreground=self.error_color)
            self.system_status.config(text="⚡ System Ready", foreground=self.neon_blue)
            if 'disconnected' in self.images:
                self.status_image.config(image=self.images['disconnected'])
            self.log_message("Disconnected from Arduino")
            
    def read_serial(self):
        while self.running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        self.process_serial_data(line)
            except Exception as e:
                self.log_message(f"Error reading serial: {str(e)}")
                time.sleep(1)
                
    def process_serial_data(self, data):
        if "Card UID:" in data:
            self.log_message(data)
            self.current_uid = data.split(": ")[1].strip()
            
            # First check if it's a default user
            if self.current_uid in self.user_lookup:
                user = self.user_lookup[self.current_uid]
                self.log_message(f"Welcome, {user['name']} ({user['role']})")
                self.current_user = user
                self.handle_user_access()
                return
                
            # Then check if it's in permitted users list
            permitted_user = self.find_permitted_user(self.current_uid)
            if permitted_user:
                name, role = permitted_user
                user = {
                    "uid": self.current_uid,
                    "name": name,
                    "role": role
                }
                self.current_user = user
                self.log_message(f"Welcome, {name} ({role})")
                self.handle_user_access()
                return
                
            # If not found anywhere, show add user dialog
            self.show_add_user_dialog(self.current_uid)
                
    def find_permitted_user(self, uid):
        # Search through permitted users list
        for i in range(self.permitted_list.size()):
            item = self.permitted_list.get(i)
            if uid in item:
                # Extract name and role from the item text
                # Format is "UID - Name (Role)"
                parts = item.split(" - ")
                if len(parts) == 2:
                    name_role = parts[1].strip()
                    # Extract name and role from "Name (Role)"
                    if "(" in name_role and ")" in name_role:
                        name = name_role[:name_role.rfind("(")].strip()
                        role = name_role[name_role.rfind("(")+1:name_role.rfind(")")].strip()
                        return (name, role)
        return None
        
    def handle_user_access(self):
        # Check if user is already in a slot
        for slot in self.slots:
            status_label, time_label, user_info = slot
            if status_label.cget("text") == "Occupied":
                # Extract UID from user info
                user_text = user_info.cget("text")
                if user_text and " - " in user_text:
                    stored_uid = user_text.split(" - ")[0]
                    if stored_uid == self.current_uid:
                        # User is already in this slot, free it
                        status_label.config(text="Available", foreground=self.neon_green)
                        time_label.config(text="")
                        user_info.config(text="")
                        self.log_message(f"Slot freed for {self.current_user['name']}")
                        return
        
        # If not in a slot, show slot selection
        self.show_slot_selection()
        
    def show_slot_selection(self):
        # Create a new window for slot selection
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Parking Slot")
        selection_window.geometry("300x400")
        selection_window.configure(bg=self.bg_color)
        
        # Make window modal
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        # Title
        title_label = ttk.Label(selection_window, text="Available Parking Slots", 
                              style='Header.TLabel')
        title_label.pack(pady=10)
        
        # Create scrollable frame
        scroll_frame = ttk.Frame(selection_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add canvas and scrollbar
        canvas = tk.Canvas(scroll_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        
        # Create button frame
        button_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add button frame to canvas
        canvas.create_window((0, 0), window=button_frame, anchor="nw")
        
        # Create buttons for available slots
        for i, slot in enumerate(self.slots):
            status_label, time_label, user_info = slot
            status = status_label.cget("text")
            if status == "Available" or status == "Denied":
                btn = NeonButton(button_frame, text=f"Slot {i+1}", 
                               command=lambda idx=i: self.select_slot(idx, selection_window))
                btn.pack(pady=5)
        
        # Update scroll region
        button_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Add mousewheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        
        # Cleanup on window close
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            selection_window.destroy()
        selection_window.protocol("WM_DELETE_WINDOW", on_closing)
            
    def select_slot(self, slot_index, window):
        # Update the selected slot
        self.update_parking_status(True, slot_index)
        # Close the selection window
        window.destroy()
            
    def update_parking_status(self, granted, slot_index=None):
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if slot_index is not None and granted and hasattr(self, 'current_user'):
            # Update specific slot with current user info
            status_label, time_label, user_info = self.slots[slot_index]
            current_status = status_label.cget("text")
            if current_status == "Available" or current_status == "Denied":
                status_label.config(text="Occupied", foreground=self.neon_green)
                time_label.config(text=f"Since {current_time}")
                # Use current_user info for consistent display
                user_info.config(text=f"{self.current_uid} - {self.current_user['name']} ({self.current_user['role']})", 
                               foreground=self.neon_blue)
        else:
            # Handle denied access
            for slot in self.slots:
                status_label, time_label, user_info = slot
                current_status = status_label.cget("text")
                if current_status == "Available" or current_status == "Denied":
                    status_label.config(text="Denied",
                                      foreground=self.neon_red)
                    time_label.config(text=f"Since {current_time}")
                    user_info.config(text="")
                    break
                
    def update_user_info(self, name, role):
        for slot in self.slots:
            status_label, time_label, user_info = slot
            if status_label.cget("text") == "Occupied":
                # Update only the name and role part, keeping the UID
                current_text = user_info.cget("text")
                if " - " in current_text:
                    uid = current_text.split(" - ")[0]
                    user_info.config(text=f"{uid} - {name} ({role})", foreground=self.neon_blue)
                break
                
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def add_permitted_user(self):
        uid = self.uid_entry.get()
        name = self.name_entry.get()
        role = self.role_entry.get()
        
        if not all([uid, name, role]):
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return
            
        # Format the command to send to Arduino
        command = f"ADD_PERMITTED:{uid}:{name}:{role}\n"
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
            self.log_message(f"Added permitted user: {name} ({role})")
            self.permitted_list.insert(tk.END, f"{name} ({role})")
            self.save_users()
        else:
            messagebox.showerror("Error", "Not connected to Arduino")
            
    def add_denied_user(self):
        uid = self.uid_entry.get()
        name = self.name_entry.get()
        
        if not all([uid, name]):
            messagebox.showwarning("Input Error", "Please fill in UID and Name fields")
            return
            
        # Format the command to send to Arduino
        command = f"ADD_DENIED:{uid}:{name}\n"
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
            self.log_message(f"Added denied user: {name}")
            self.denied_list.insert(tk.END, name)
            self.save_users()
        else:
            messagebox.showerror("Error", "Not connected to Arduino")
            
    def save_users(self):
        users = {
            'permitted': [self.permitted_list.get(i) for i in range(self.permitted_list.size())],
            'denied': [self.denied_list.get(i) for i in range(self.denied_list.size())]
        }
        with open('users.json', 'w') as f:
            json.dump(users, f)
            
    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                users = json.load(f)
                for user in users['permitted']:
                    self.permitted_list.insert(tk.END, user)
                for user in users['denied']:
                    self.denied_list.insert(tk.END, user)
        except FileNotFoundError:
            pass

    def clear_permitted_users(self):
        self.permitted_list.delete(0, tk.END)
        self.save_users()
        self.log_message("Cleared permitted users list")
        
    def clear_denied_users(self):
        self.denied_list.delete(0, tk.END)
        self.save_users()
        self.log_message("Cleared denied users list")

    def add_default_users(self):
        for user in self.default_users:
            # Check if user already exists in the permitted list
            user_exists = False
            for i in range(self.permitted_list.size()):
                if user["uid"] in self.permitted_list.get(i):
                    user_exists = True
                    break
                    
            if not user_exists:
                # Add user to permitted users list
                user_text = f"{user['name']} ({user['role']})"
                self.permitted_list.insert(tk.END, user_text)
                self.save_users()
                self.log_message(f"Added default user: {user_text}")

    def add_to_permitted_list(self, uid, name, role):
        # Check if user already exists in the permitted list
        for i in range(self.permitted_list.size()):
            if uid in self.permitted_list.get(i):
                return  # User already in list
                
        # Add to permitted list
        user_text = f"{uid} - {name} ({role})"
        self.permitted_list.insert(tk.END, user_text)
        self.save_users()
        self.log_message(f"Added to permitted users: {user_text}")
        
    def show_add_user_dialog(self, uid):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        title_label = ttk.Label(dialog, text="Add New User", style='Header.TLabel')
        title_label.pack(pady=10)
        
        # UID display
        uid_frame = ttk.Frame(dialog)
        uid_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(uid_frame, text="UID:").pack(side="left", padx=5)
        ttk.Label(uid_frame, text=uid, foreground=self.neon_blue).pack(side="left")
        
        # Name input
        name_frame = ttk.Frame(dialog)
        name_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(name_frame, text="Name:").pack(side="left", padx=5)
        name_entry = ttk.Entry(name_frame, style='TEntry')
        name_entry.pack(side="left", fill="x", expand=True)
        
        # Role input
        role_frame = ttk.Frame(dialog)
        role_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(role_frame, text="Role:").pack(side="left", padx=5)
        role_entry = ttk.Entry(role_frame, style='TEntry')
        role_entry.pack(side="left", fill="x", expand=True)
        
        # User type selection
        type_frame = ttk.Frame(dialog)
        type_frame.pack(fill="x", padx=10, pady=10)
        
        user_type = tk.StringVar(value="permitted")  # Default to permitted
        
        type_label = ttk.Label(type_frame, text="User Type:", style='Status.TLabel')
        type_label.pack(pady=5)
        
        # Radio buttons for user type
        permitted_radio = ttk.Radiobutton(type_frame, text="Permitted User", 
                                        variable=user_type, value="permitted")
        permitted_radio.pack(pady=2)
        
        denied_radio = ttk.Radiobutton(type_frame, text="Denied User", 
                                     variable=user_type, value="denied")
        denied_radio.pack(pady=2)
        
        def save_user():
            name = name_entry.get().strip()
            role = role_entry.get().strip()
            is_permitted = user_type.get() == "permitted"
            
            if name and role:
                # Create user info
                new_user = {
                    "uid": uid,
                    "name": name,
                    "role": role
                }
                
                if is_permitted:
                    # Add to default users and lookup
                    self.default_users.append(new_user)
                    self.user_lookup[uid] = new_user
                    
                    # Add to permitted list
                    self.add_to_permitted_list(uid, name, role)
                    
                    # Set as current user and show slot selection
                    self.current_user = new_user
                    dialog.destroy()
                    self.show_slot_selection()
                else:
                    # Add to denied list
                    user_text = f"{uid} - {name} ({role})"
                    self.denied_list.insert(tk.END, user_text)
                    self.save_users()
                    self.log_message(f"Added to denied users: {user_text}")
                    dialog.destroy()
            else:
                messagebox.showwarning("Input Error", "Please fill in all fields")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        cancel_btn = NeonButton(button_frame, text="Cancel", 
                              command=dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = NeonButton(button_frame, text="Save", 
                             command=save_user)
        save_btn.pack(side="right", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingSystemGUI(root)
    root.mainloop()
