from tkinter import ttk, messagebox
import pandas as pd


def delete_preset_func(row, df):

    confirmation = confirm_deletion()
    if confirmation:
        df = df[~(
            (df['name'] == row.name) &
            (df['weekday'] == row.weekday) &
            (df['start_time'] == row.start_time) &
            (df['end_time'] == row.end_time) &
            (df['location'] == row.location)
        )]

        return df 
    
    return confirmation

def confirm_deletion():
    result = messagebox.askyesno("Confirm", "Do you want to proceed?")
    if result:
        return True
    else:
        return False

if __name__ == "__main__":
    confirm_deletion()