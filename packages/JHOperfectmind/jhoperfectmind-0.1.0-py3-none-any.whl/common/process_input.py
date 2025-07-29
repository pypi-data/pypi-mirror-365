from datetime import datetime

#Processes data from GUI and makes it usable to find correct perfectmind session
class EventHandler:
    def __init__(self):
        self.event_data = None
    
    def handle_event(self, event_data: dict):
        self.event_data = event_data
        
        #date: str(YYYY-MM-DD) -> Weekday(prefixed), Month(prefixed) #, YYYY
        self.event_data['date'] = format_event_date(event_data['date'])
        
        self.event_data['desired_event'] = event_data['name']
        self.event_data['desired_date'] = "Events for " + event_data['date']
        self.event_data['desired_time'] = event_data['start_time'] + ' - ' + event_data['end_time']
        self.event_data['desired_location'] = event_data['location']

        print("\n=== EVENT DETAILS ===")
        print(f"Event Name: {self.event_data['name']}")
        print(f"Date: {self.event_data['date']}")
        print(f"Start Time: {self.event_data['start_time']}")
        print(f"End Time: {self.event_data['end_time']}")
        print(f"Location: {self.event_data['location']}")

        # This will be directly compared to HTMl elements on perfectmind
        print("\n======================")
        print(f"Desired Event: {self.event_data['desired_event']}")
        print(f"Desired Date: {self.event_data['desired_date']}")
        print(f"Desired Time: {self.event_data['desired_time']}")
        print(f"Desired Location: {self.event_data['desired_location']}")


def get_day_suffix(day: datetime):
    if 11 <= day <= 13:
        return 'th'
    #if last digit != 1/2/3, default suffix with 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_event_date(date_str:str):
    try:
        #take datestr and casts it to datetime
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day = date_obj.day
        suffix = get_day_suffix(day)

        # return date object as a string
        return date_obj.strftime(f"%a, %b {day}{suffix}, %Y")
    except ValueError:
        return date_str


if __name__ == "__main__":
    ev = EventHandler()
    a = {'name': 'Length Swim', 'date': '2025-05-24', 'start_time': '07:00 am', 'end_time': '08:00 am', 'location': 'North Thornhill Community Centre - Pool - Large'}
    ev.handle_event(a)
