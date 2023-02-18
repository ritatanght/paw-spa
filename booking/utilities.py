from datetime import datetime, timedelta
from .models import Appointment

# used to check free time slot when booking form is submitted
def list_diff(l1: list, l2: list):
    """ Return a list of elements that are present in l1
        or in l2 but not in both l1 & l2.
        IE: list_diff([1, 2, 3, 4], [2,4]) => [1, 3] 
    """
    return [i for i in l1 + l2 if i not in l1 or i not in l2]


def check_free_time(time_slot: list, exist_list: list):
    """ Return the list of available time slot if exist,
        according to a given exist slot list.
        Return the remained time slot, or empty list if all are used
        IE: ([7, 12], [7, 8, 9, 10, 11, 12]) => [8, 9, 10, 11]
    """

    remain_slot = list_diff(time_slot, exist_list)
    return remain_slot

# convert date in urls
class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)


# load the schedule dict to be sent to javascript for showing the preview schedule
def load_preview_dict(start):
    today = datetime.today().date()
    date_list = [start + timedelta(days=x) for x in range(7)]

    slot_dict = {}
    for date in date_list:
        if date.weekday() == 0:
            slot_dict[datetime.strftime(date, '%Y-%m-%d-%a')] = 'Closed'
        else:
            time_list = [10, 13, 15]
            time_slot_list = list(Appointment.objects.filter(
                date=date).values_list('time', flat=True))

            for i in range(len(time_list)):
                if time_list[i] in time_slot_list or (date == today and datetime.now().hour > time_list[i]):
                    time_list[i] = 'x'
            slot_dict[datetime.strftime(date, '%Y-%m-%d-%a')] = time_list
    return slot_dict
