from datetime import date, timedelta
from common.Register import registration_process
from common.process_input import EventHandler
import pandas as pd
import os

def start():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print(os.getcwd())

    #take the current day, find the next week version of it (add 7? use prexisting scripts)
    reference_date = date.today()
    print(reference_date, reference_date.weekday())

    df = pd.read_csv('C:/Users/Justin Ho/Coding/perfectMind_webscraper/presets/scheduled_presets.csv')

    target_date = reference_date + timedelta(days=7)
    target_weekday = target_date.strftime("%A")

    for row in df.itertuples(index=False):
        if row.weekday == target_weekday:
            event_data = {
                "name": row.name,
                "date": str(target_date),
                "start_time": row.start_time,
                "end_time": row.end_time,
                "location": row.location,
            }

    handler = EventHandler()
    handler.handle_event(event_data)

    print(event_data)

    registration_process(event_data)

#grab all predetermined time slots and use them as inputs to the registration script