import os
import json
import shutil  # For copying and moving files
import datetime  # For timestamps in the header
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, Canvas
from PIL import Image, ImageTk

PUSH_REQUESTS_FILE = 'push_requests.json'

class CampfireApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Campfire 1.0")
        
        # User role and level will be set at login.
        self.user_role = None    # "programmer_manager", "programmer", "user_manager", "user"
        self.user_level = None   # Numeric level: 4, 3, 2, or 1
        
        # Current environment (DEV, TEST, PROD) is set later.
        self.environment = None
        
        # Ensure necessary directories exist.
        self.ensure_directories_exist(["DEV", "TEST", "PROD"])
        
        # Load any existing push requests.
        self.push_requests = self.load_push_requests()
        
        # Load subapplications (if needed).
        self.subapplications = self.load_subapplications()
        
        # Start at the login screen.
        self.login_screen()
        self.root.mainloop()
    
    ### Utility Functions ###
    
    def ensure_directories_exist(self, directories):
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def load_push_requests(self):
        if os.path.exists(PUSH_REQUESTS_FILE):
            with open(PUSH_REQUESTS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_push_requests(self):
        with open(PUSH_REQUESTS_FILE, 'w') as f:
            json.dump(self.push_requests, f)
    
    def load_subapplications(self):
        if os.path.exists('subapplications.json'):
            with open('subapplications.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_subapplications(self):
        with open('subapplications.json', 'w') as f:
            json.dump(self.subapplications, f)
    
    def get_subapplications_from_directory(self, directory):
        try:
            return [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith(".py")]
        except FileNotFoundError:
            return []
    
    def get_icon_for_subapp(self, subapp_name):
        icon_path = "default_icon.png"
        if os.path.exists(icon_path):
            image = Image.open(icon_path).resize((32, 32))
            return ImageTk.PhotoImage(image)
        else:
            image = Image.new("RGB", (32, 32), "gray")
            return ImageTk.PhotoImage(image)
    
    ### Menu Hierarchy ###
    
    def login_screen(self):
        """Display the login screen."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Login", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Select your user role:", font=("Arial", 12)).pack(pady=5)
        
        self.role_var = tk.StringVar(value="user")
        roles = [
            ("Programmer Manager (Level 4)", "programmer_manager"),
            ("Programmer (Level 3)", "programmer"),
            ("User Manager (Level 2)", "user_manager"),
            ("User (Level 1)", "user")
        ]
        for text, role in roles:
            tk.Radiobutton(self.root, text=text, variable=self.role_var, value=role).pack(anchor=tk.W, padx=20)
        
        tk.Button(self.root, text="Login", command=self.process_login, width=20).pack(pady=10)
    
    def process_login(self):
        """Set the user role and level then go to the main menu."""
        self.user_role = self.role_var.get()
        role_to_level = {
            "programmer_manager": 4,
            "programmer": 3,
            "user_manager": 2,
            "user": 1
        }
        self.user_level = role_to_level.get(self.user_role, 1)
        self.main_menu()
    
    def main_menu(self):
        """The main menu after login, with options to enter environments, approve pushes (for managers), or logout."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Campfire 1.0 - Main Menu", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Enter Environment(s)", command=self.create_environment_selection_ui, width=40).pack(pady=5)
        
        # Approve push requests is on the main menu for managers.
        if self.user_role in ["programmer_manager", "user_manager"]:
            tk.Button(self.root, text="Approve TEST to PROD Push Requests", 
                      command=self.create_approve_push_requests_ui, width=40).pack(pady=5)
        
        tk.Button(self.root, text="Logout", command=self.login_screen, width=40).pack(pady=5)
    
    def create_environment_selection_ui(self):
        """Allow the user to select an environment (DEV, TEST, PROD)."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Select Environment", font=("Arial", 16)).pack(pady=10)
        for env in ["DEV", "TEST", "PROD"]:
            ttk.Button(self.root, text=env, command=lambda e=env: self.set_environment(e), width=40).pack(pady=5)
        
        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu, width=40).pack(pady=5)
    
    def set_environment(self, environment):
        self.environment = environment
        self.create_environment_menu()
    
    def create_environment_menu(self):
        """
        Display a combined environment menu that shows original top buttons (for push actions and removal)
        and then directly lists the sub-applications available in the selected environment.
        The original buttons appear at the top.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title
        title_text = f"Campfire 1.0 - Environment: {self.environment} | Role: {self.user_role.replace('_', ' ').title()}"
        tk.Label(self.root, text=title_text, font=("Arial", 16)).pack(pady=10)
        
        # Top action buttons (environment-specific)
        if self.environment == "DEV" and self.user_role == "programmer":
            tk.Button(self.root, text="Push from DEV to TEST", command=self.create_push_dev_to_test_ui, width=40).pack(pady=5)
        elif self.environment == "TEST":
            if self.user_role == "programmer":
                tk.Button(self.root, text="Request Push from TEST to PROD", command=self.create_request_push_ui, width=40).pack(pady=5)
        # (No push actions for PROD)
        
        if self.user_role in ["programmer_manager", "user_manager"]:
            tk.Button(self.root, text="Remove Sub-Application", command=self.create_remove_subapp_ui, width=40).pack(pady=5)
        
        # Navigation button at top: Back to Environment Selection
        tk.Button(self.root, text="Back to Environment Selection", command=self.create_environment_selection_ui, width=40).pack(pady=5)
        
        # Now, list all sub-applications in the current environment
        tk.Label(self.root, text=f"Sub-Applications in {self.environment}", font=("Arial", 14)).pack(pady=10)
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        subapp_names = self.get_subapplications_from_directory(self.environment)
        for subapp_name in subapp_names:
            frame = ttk.Frame(scrollable_frame, padding=10)
            frame.pack(fill=tk.X, pady=5)
            icon = self.get_icon_for_subapp(subapp_name)
            icon_label = tk.Label(frame, image=icon)
            icon_label.image = icon
            icon_label.pack(side=tk.LEFT, padx=5)
            details_frame = ttk.Frame(frame)
            details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(details_frame, text=f"Name: {subapp_name}").pack(anchor=tk.W)
            tk.Label(details_frame, text=f"Filename: {subapp_name}.py").pack(anchor=tk.W)
            ttk.Button(frame, text="Run", command=lambda name=subapp_name: self.run_subapplication(name)).pack(side=tk.RIGHT)
            if self.user_role in ["programmer_manager", "user_manager"]:
                ttk.Button(frame, text="Remove", command=lambda name=subapp_name: self.remove_subapplication(name)).pack(side=tk.RIGHT)
    
    ### Environment-Specific Functionality ###
    
    def create_push_dev_to_test_ui(self):
        """Interface for a programmer in DEV to push a sub-application from DEV to TEST."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Push from DEV to TEST", font=("Arial", 14)).pack(pady=10)
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        subapp_names = self.get_subapplications_from_directory("DEV")
        if not subapp_names:
            tk.Label(scrollable_frame, text="No sub-applications found in DEV.").pack(pady=10)
        else:
            for subapp_name in subapp_names:
                frame = ttk.Frame(scrollable_frame, padding=10)
                frame.pack(fill=tk.X, pady=5)
                icon = self.get_icon_for_subapp(subapp_name)
                icon_label = tk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side=tk.LEFT, padx=5)
                details = ttk.Frame(frame)
                details.pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(details, text=f"Name: {subapp_name}").pack(anchor=tk.W)
                tk.Label(details, text=f"Filename: {subapp_name}.py").pack(anchor=tk.W)
                ttk.Button(frame, text="Push to TEST", command=lambda name=subapp_name: self.push_from_dev_to_test(name)).pack(side=tk.RIGHT)
        
        tk.Button(self.root, text="Back", command=self.create_environment_menu, width=30).pack(pady=5)
    
    def push_from_dev_to_test(self, subapp_name):
        """Copies a sub-application from DEV to TEST with a default header comment."""
        source = os.path.join("DEV", f"{subapp_name}.py")
        destination = os.path.join("TEST", f"{subapp_name}.py")
        if os.path.exists(source):
            try:
                with open(source, 'r') as f:
                    original_contents = f.read()
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                header = f"#Last push initiated on {timestamp} by {self.user_role.replace('_',' ').title()} from DEV -> TEST\n"
                new_contents = header + original_contents
                with open(destination, 'w') as f:
                    f.write(new_contents)
                messagebox.showinfo("Success", f"Sub-application '{subapp_name}' has been pushed from DEV to TEST with header.")
            except Exception as e:
                messagebox.showerror("Error", f"Error pushing '{subapp_name}': {e}")
            self.create_push_dev_to_test_ui()  # Refresh
        else:
            messagebox.showerror("Error", f"Sub-application '{subapp_name}' not found in DEV.")
    
    def create_request_push_ui(self):
        """Interface for a programmer in TEST to request a push from TEST to PROD."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Request Push from TEST to PROD", font=("Arial", 14)).pack(pady=10)
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        subapp_names = self.get_subapplications_from_directory("TEST")
        if not subapp_names:
            tk.Label(scrollable_frame, text="No sub-applications found in TEST.").pack(pady=10)
        else:
            for subapp_name in subapp_names:
                frame = ttk.Frame(scrollable_frame, padding=10)
                frame.pack(fill=tk.X, pady=5)
                icon = self.get_icon_for_subapp(subapp_name)
                icon_label = tk.Label(frame, image=icon)
                icon_label.image = icon
                icon_label.pack(side=tk.LEFT, padx=5)
                details = ttk.Frame(frame)
                details.pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(details, text=f"Name: {subapp_name}").pack(anchor=tk.W)
                tk.Label(details, text=f"Filename: {subapp_name}.py").pack(anchor=tk.W)
                ttk.Button(frame, text="Request Push", command=lambda name=subapp_name: self.request_push(name)).pack(side=tk.RIGHT)
        
        tk.Button(self.root, text="Back", command=self.create_environment_menu, width=30).pack(pady=5)
    
    def request_push(self, subapp_name):
        """Add a push request (TEST to PROD) for a given sub-application."""
        if subapp_name in self.push_requests:
            messagebox.showinfo("Info", f"A push request for '{subapp_name}' already exists.")
        else:
            self.push_requests.append(subapp_name)
            self.save_push_requests()
            messagebox.showinfo("Submitted", f"Push request for '{subapp_name}' submitted for manager approval.")
        self.create_request_push_ui()  # Refresh
    
    def create_approve_push_requests_ui(self):
        """Interface for managers to view and approve push requests (TEST to PROD)."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Approve Push Requests (TEST to PROD)", font=("Arial", 14)).pack(pady=10)
        if not self.push_requests:
            tk.Label(self.root, text="No pending push requests.").pack(pady=10)
        else:
            canvas = Canvas(self.root)
            scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            for subapp_name in list(self.push_requests):
                frame = ttk.Frame(scrollable_frame, padding=10)
                frame.pack(fill=tk.X, pady=5)
                tk.Label(frame, text=f"Sub-Application: {subapp_name}").pack(side=tk.LEFT, padx=5)
                ttk.Button(frame, text="Approve", command=lambda name=subapp_name: self.approve_push_request(name)).pack(side=tk.RIGHT)
        
        tk.Button(self.root, text="Back to Main Menu", command=self.main_menu, width=40).pack(pady=5)
    
    def approve_push_request(self, subapp_name):
        """Manager approves the push request: move sub-application from TEST to PROD with a header."""
        source = os.path.join("TEST", f"{subapp_name}.py")
        destination = os.path.join("PROD", f"{subapp_name}.py")
        if os.path.exists(source):
            try:
                with open(source, 'r') as f:
                    original_contents = f.read()
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                header = f"#Last push initiated on {timestamp} by {self.user_role.replace('_',' ').title()} from TEST -> PROD\n"
                new_contents = header + original_contents
                with open(destination, 'w') as f:
                    f.write(new_contents)
                os.remove(source)
                messagebox.showinfo("Approved", f"'{subapp_name}' has been pushed from TEST to PROD with header.")
                self.push_requests.remove(subapp_name)
                self.save_push_requests()
            except Exception as e:
                messagebox.showerror("Error", f"Error pushing '{subapp_name}': {e}")
        else:
            messagebox.showerror("Error", f"'{subapp_name}' not found in TEST.")
        self.create_approve_push_requests_ui()  # Refresh
    
    def create_remove_subapp_ui(self):
        """Interface to remove a sub-application from the current environment (managers only)."""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Remove Sub-Application", font=("Arial", 14)).pack(pady=10)
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        subapp_names = self.get_subapplications_from_directory(self.environment)
        for subapp_name in subapp_names:
            frame = ttk.Frame(scrollable_frame, padding=10)
            frame.pack(fill=tk.X, pady=5)
            icon = self.get_icon_for_subapp(subapp_name)
            icon_label = tk.Label(frame, image=icon)
            icon_label.image = icon
            icon_label.pack(side=tk.LEFT, padx=5)
            details = ttk.Frame(frame)
            details.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(details, text=f"Name: {subapp_name}").pack(anchor=tk.W)
            tk.Label(details, text=f"Filename: {subapp_name}.py").pack(anchor=tk.W)
            ttk.Button(frame, text="Remove", command=lambda name=subapp_name: self.remove_subapplication(name)).pack(side=tk.RIGHT)
        
        tk.Button(self.root, text="Back", command=self.create_environment_menu, width=30).pack(pady=5)
    
    def remove_subapplication(self, subapp_name):
        if messagebox.askyesno("Confirm Removal", f"Remove '{subapp_name}' from {self.environment}?"):
            subapp_path = os.path.join(self.environment, f"{subapp_name}.py")
            if os.path.exists(subapp_path):
                os.remove(subapp_path)
                messagebox.showinfo("Removed", f"'{subapp_name}' removed from {self.environment}.")
                self.create_remove_subapp_ui()
            else:
                messagebox.showerror("Error", f"'{subapp_name}' not found in {self.environment}.")
    
    def run_subapplication(self, subapp_name):
        """Run the selected sub-application from the current environment."""
        try:
            subapp_path = os.path.join(self.environment, f"{subapp_name}.py")
            if os.path.exists(subapp_path):
                with open(subapp_path) as f:
                    exec(f.read(), {"__name__": "__main__"})
            else:
                raise FileNotFoundError(f"'{subapp_name}' not found in {self.environment}.")
        except Exception as e:
            messagebox.showerror("Execution Error", f"Error running '{subapp_name}': {e}")

if __name__ == "__main__":
    CampfireApp()
