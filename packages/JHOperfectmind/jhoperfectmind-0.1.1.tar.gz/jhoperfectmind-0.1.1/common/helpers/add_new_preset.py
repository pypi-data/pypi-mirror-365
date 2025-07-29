from tkinter import ttk, messagebox
from common.helpers.find_date import next_weekday_date
from datetime import datetime
import pandas as pd


def add_new_preset(preset_frame, reload_callback=None):

    start_time_str = f"{preset_frame.start_hour.get()}:{preset_frame.start_minute.get()} {preset_frame.start_ampm.get()}"
    end_time_str = f"{preset_frame.end_hour.get()}:{preset_frame.end_minute.get()} {preset_frame.end_ampm.get()}"

    event_data = {
        'weekday': preset_frame.weekday.get(),
        "name": preset_frame.event_name.get(),
        "start_time": start_time_str,
        "end_time": end_time_str,
        "location": preset_frame.event_location.get(),
    }
    
    messagebox.showinfo("Event Submitted", 
                        f"Event '{event_data['name']}' created for {event_data['weekday']}\n"
                        f"From {start_time_str} to {end_time_str}\n"
                        f"At {event_data['location']}")
    
    df = pd.DataFrame([event_data])

    df.to_csv(r'C:\Users\Justin Ho\Coding\perfectMind_webscraper\presets\presets.csv', mode='a', header=False, index=False)

    if reload_callback:
        reload_callback()