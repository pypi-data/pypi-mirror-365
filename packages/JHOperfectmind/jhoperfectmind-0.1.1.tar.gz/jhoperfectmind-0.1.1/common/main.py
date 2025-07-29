from common.process_input import EventHandler
from common.webscraper_GUI import EventInputGUI
from common.Register import registration_process
from common.Register_volleyball import registration_process_v

from tkinter import Tk
import pandas as pd

#Create TK instance as base for GUI
root = Tk()

# Read CSV into DataFrame
df = pd.read_csv('presets/presets.csv')

#Create GUI instance
app = EventInputGUI(root,df)

#Run GUI
root.mainloop()

print(app.event_data)
#Create handler to process user input
data_processor = EventHandler()
data_processor.handle_event(app.event_data)

#register for perfectmind session
import asyncio

if app.event_data['desired_event'] == 'Length Swim':
    asyncio.run(registration_process(app.event_data))
elif app.event_data['desired_event'] == 'Volleyball':
    asyncio.run(registration_process_v(app.event_data))

