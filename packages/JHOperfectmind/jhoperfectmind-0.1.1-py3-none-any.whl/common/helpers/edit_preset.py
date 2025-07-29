from tkinter import ttk, messagebox
import pandas as pd


def edit_preset_func(frame, row, df, reload_callback=None):

    start_time_str = f"{frame.start_hour.get()}:{frame.start_minute.get()} {frame.start_ampm.get()}"
    end_time_str = f"{frame.end_hour.get()}:{frame.end_minute.get()} {frame.end_ampm.get()}"


    confirmation = confirm_deletion()
    if confirmation:
        # Find index of the row to edit
        mask = (
            (df['name'] == row.name) &
            (df['weekday'] == row.weekday) &
            (df['start_time'] == row.start_time) &
            (df['end_time'] == row.end_time) &
            (df['location'] == row.location)
        )

        # Update the matching row
        df.loc[mask, 'name'] = frame.event_name.get()
        df.loc[mask, 'weekday'] = frame.weekday.get()
        df.loc[mask, 'start_time'] = start_time_str
        df.loc[mask, 'end_time'] = end_time_str
        df.loc[mask, 'location'] = frame.event_location.get()

        df.to_csv(r'C:\Users\Justin Ho\Coding\perfectMind_webscraper\presets\presets.csv', index=False)

        if reload_callback:
            reload_callback()

def confirm_deletion():
    result = messagebox.askyesno("Confirm", "Do you want to proceed?")
    if result:
        return True
    else:
        return False

if __name__ == "__main__":
    confirm_deletion()