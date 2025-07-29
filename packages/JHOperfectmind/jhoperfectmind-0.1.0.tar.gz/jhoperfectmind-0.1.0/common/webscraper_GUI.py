import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from common.helpers.find_date import next_weekday_date
from common.helpers.add_new_preset import add_new_preset
from common.helpers.delete_preset import delete_preset_func
from common.helpers.edit_preset import edit_preset_func
import pandas as pd

class ManualInputPage_Template(tk.Frame):
    def __init__(self, parent, choose_by_weekday=False):
        super().__init__(parent)
        current_date = datetime.now().strftime("%Y-%m-%d")

        # FIND A BETTER WAY FOR THIS LATER
        self.location_options = ["North Thornhill Community Centre", "Vellore Village Community Centre"]
        self.days_of_week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        
        # Create input fields with defaults
        tk.Label(self, text="Event Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.event_name = tk.Entry(self, width=30)
        self.event_name.insert(0, "Length Swim")
        self.event_name.grid(row=0, column=1, padx=5, pady=5)
        
        if choose_by_weekday:
            tk.Label(self, text="Weekday").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            self.weekday = ttk.Combobox(self, values=self.days_of_week,state="readonly", width=30)
            self.weekday.grid(row=1, column=1, padx=5, pady=5)
        else:
            tk.Label(self, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            self.event_date = tk.Entry(self, width=30)
            self.event_date.insert(0, current_date)
            self.event_date.grid(row=1, column=1, padx=5, pady=5)
        
        # Time frame section
        tk.Label(self, text="Start Time:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        
        # Start time frame
        self.start_time_frame = tk.Frame(self)
        self.start_time_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        self.start_hour = ttk.Combobox(self.start_time_frame, width=3, values=[f"{i:02d}" for i in range(1,13)])
        self.start_hour.set("07")
        self.start_hour.pack(side="left")
        
        tk.Label(self.start_time_frame, text=":").pack(side="left")
        
        self.start_minute = ttk.Combobox(self.start_time_frame, width=3, values=[f"{i:02d}" for i in range(0,60,5)])
        self.start_minute.set("00")
        self.start_minute.pack(side="left")
        
        self.start_ampm = ttk.Combobox(self.start_time_frame, width=3, values=["am", "pm"])
        self.start_ampm.set("am")
        self.start_ampm.pack(side="left", padx=(5,0))
        
        # End time frame
        tk.Label(self, text="End Time:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        
        self.end_time_frame = tk.Frame(self)
        self.end_time_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        self.end_hour = ttk.Combobox(self.end_time_frame, width=3, values=[f"{i:02d}" for i in range(1,13)])
        self.end_hour.set("08")
        self.end_hour.pack(side="left")
        
        tk.Label(self.end_time_frame, text=":").pack(side="left")
        
        self.end_minute = ttk.Combobox(self.end_time_frame, width=3, values=[f"{i:02d}" for i in range(0,60,5)])
        self.end_minute.set("00")
        self.end_minute.pack(side="left")
        
        self.end_ampm = ttk.Combobox(self.end_time_frame, width=3, values=["am", "pm"])
        self.end_ampm.set("am")
        self.end_ampm.pack(side="left", padx=(5,0))
        
        # Location
        tk.Label(self, text="Location:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.event_location = ttk.Combobox(self, values=self.location_options, width=30)
        self.event_location.set(self.location_options[0])
        self.event_location.grid(row=4, column=1, padx=5, pady=5)

class EventInputGUI:
    def __init__(self, master, preset_events):
        self.master = master
        self.event_data = {}
        self.preset_events = preset_events
        self.location_options = ["North Thornhill Community Centre", "Vellore Village Community Centre"]
        master.title("Event Information Input")

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack()
        
        # Create manual tab
        self.manual_tab = ManualInputPage_Template(self.notebook)
        self.manual_tab.submit_button = tk.Button(self.manual_tab, text="Submit", command=self.submit_event)
        self.manual_tab.submit_button.grid(row=5, column=1, pady=10, sticky="e")
        self.manual_tab.pack()


        # Create add_presets frame
        self.add_presets_frame = ManualInputPage_Template(master, choose_by_weekday=True)
        self.add_presets_frame.submit_button = tk.Button(self.add_presets_frame, text="Submit_stuff", command=lambda:add_new_preset(self.add_presets_frame, reload_callback=self.reload_presets))
        self.add_presets_frame.submit_button.grid(row=5, column=1, pady=10, sticky="e")
        # Back Button
        self.add_presets_frame.back_button = ttk.Button(self.add_presets_frame, text="Back",
                                 command=lambda:self.notebook.tkraise() )
        self.add_presets_frame.back_button.grid(row=5, column=0, pady=10, sticky="e")
        self.add_presets_frame.pack()


        #Create tabs within presets
        self.days_of_week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        self.nested_notebook = ttk.Notebook(self.notebook)
        self.nested_notebook.pack(expand=True, fill='both')

        self.notebook.add(self.manual_tab, text="Manual Input")
        self.notebook.add(self.nested_notebook, text="Presets") 

        self.weekday_tabs = []
        for i,weekday in enumerate(self.days_of_week):
            self.weekday_tabs.append(ttk.Frame(self.nested_notebook))
            self.weekday_tabs[i].pack(padx=5)
            self.nested_notebook.add(self.weekday_tabs[i], text=weekday)

        #Create NewPresetPage
        self.add_presets_frame.pack()
        self.add_presets_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Ensure it's layered properly

        self.notebook.pack_propagate(True)

        self.notebook.tkraise()
    
        # Initialize both tabs
        self.create_presets_tab()

    def delete_preset(self,row,df):
        df = delete_preset_func(row,df)
        if isinstance(df, pd.DataFrame):
            df.to_csv(r'C:\Users\Justin Ho\Coding\perfectMind_webscraper\presets\presets.csv', index=False)
            self.reload_presets()
    
    def edit_preset(self,row,df):
        #Create edit_presets frame
        self.edit_presets_frame = ManualInputPage_Template(self.master, choose_by_weekday=True)
        self.edit_presets_frame.submit_button = tk.Button(self.edit_presets_frame, text="Submit changes", command=lambda:edit_preset_func(self.edit_presets_frame, row, df, reload_callback=self.reload_presets))
        self.edit_presets_frame.weekday.config(state="disabled")
        self.edit_presets_frame.weekday.set(row.weekday)

        self.edit_presets_frame.submit_button.grid(row=5, column=1, pady=10, sticky="e")
        # Back Button
        self.edit_presets_frame.back_button = ttk.Button(self.edit_presets_frame, text="Back",
                                 command=lambda:self.notebook.tkraise() )
        self.edit_presets_frame.back_button.grid(row=5, column=0, pady=10, sticky="e")
        self.edit_presets_frame.pack()
        self.edit_presets_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Ensure it's layered properly

        self.edit_presets_frame.tkraise()


    def reload_presets(self):
        self.preset_events = pd.read_csv(r'C:\Users\Justin Ho\Coding\perfectMind_webscraper\presets\presets.csv')

        for tab in self.weekday_tabs:
            for widget in tab.winfo_children():
                widget.destroy()

        self.create_presets_tab()

        self.notebook.tkraise()

    def create_presets_tab(self):
        df = self.preset_events

        for i,weekday in enumerate(self.days_of_week):
            frame = tk.Frame(self.weekday_tabs[i], bd=2, relief=tk.GROOVE)
            frame.pack(fill=tk.X, padx=5, pady=5)

            r = 0
            for row in df[df["weekday"] == weekday].itertuples(index=False):     
                event_frame = tk.Frame(frame, bd=2, relief=tk.GROOVE)    
                event_frame.pack(fill=tk.X, padx=5, pady=5) 

                tk.Label(event_frame, text=row.name, font=('Arial', 10, 'bold')).grid(row=r, column=0, sticky='w', padx=20, pady=5)
                remove_button = tk.Button(event_frame, text="Remove", command=lambda e=row,d=df: self.delete_preset(e,d)).grid(row=r, column=1, sticky='w', padx=20)
                r+=1
                
                tk.Label(event_frame, text=f"Time: {row.start_time} to {row.end_time}").grid(row=r, column=0, sticky='w', padx=20)
                edit_button = tk.Button(event_frame, text="Edit", command=lambda e=row,d=df: self.edit_preset(e,d)).grid(row=r, column=1, sticky='w', padx=20)

                r+=1 
                tk.Label(event_frame, text=f"Location: {row.location}").grid(row=r, column=0, sticky='w', padx=20)
                r+=1

                btn = tk.Button(frame, text="Select", command=lambda e=row: self.select_preset(e))
                btn.pack(padx=5)
                r+=1

            ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)
            r+=1

            tk.Button(frame, text="add new preset", command=lambda: self.add_presets_frame.tkraise()).pack(fill=tk.X, padx=5, pady=5)

    def validate_inputs(self):
        information = self.manual_tab
        if not all([information.event_name.get(), information.event_date.get(), information.event_location.get()]):
            messagebox.showerror("Error", "All fields must be filled out")
            return False
        
        # Validate date
        try:
            datetime.strptime(information.event_date.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return False
            
        # Validate time components
        try:
            start_time_str = f"{information.start_hour.get()}:{information.start_minute.get()} {information.start_ampm.get()}"
            end_time_str = f"{information.end_hour.get()}:{information.end_minute.get()} {information.end_ampm.get()}"
            
            # Parse times to check validity
            start_time = datetime.strptime(start_time_str, "%I:%M %p")
            end_time = datetime.strptime(end_time_str, "%I:%M %p")
            
            if start_time >= end_time:
                messagebox.showerror("Error", "End time must be after start time")
                return False
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid time format: {str(e)}")
            return False
            
        return True
    # for preset registrations
    def select_preset(self, preset_event):

        # returns next weekends date
        current_date = next_weekday_date(preset_event.weekday)

        self.event_data = {
            "name": preset_event.name,
            "date": current_date,
            "start_time": preset_event.start_time,
            "end_time": preset_event.end_time,
            "location": preset_event.location
        }
        
        messagebox.showinfo("Preset Selected", 
                         f"Event '{self.event_data['name']}' created for {self.event_data['date']}\n"
                         f"From {self.event_data['start_time']} to {self.event_data['end_time']}\n"
                         f"At {self.event_data['location']}")
        
        self.master.destroy()

    def submit_event(self):
        information = self.manual_tab
        if self.validate_inputs():
            start_time_str = f"{information.start_hour.get()}:{information.start_minute.get()} {information.start_ampm.get()}"
            end_time_str = f"{information.end_hour.get()}:{information.end_minute.get()} {information.end_ampm.get()}"
            
            self.event_data = {
                "name": information.event_name.get(),
                "date": information.event_date.get(),
                "start_time": start_time_str,
                "end_time": end_time_str,
                "location": information.event_location.get(),
            }
            
            messagebox.showinfo("Event Submitted", 
                             f"Event '{self.event_data['name']}' created for {self.event_data['date']}\n"
                             f"From {start_time_str} to {end_time_str}\n"
                             f"At {self.event_data['location']}")
            
            self.master.destroy()