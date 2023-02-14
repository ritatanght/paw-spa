from datetime import datetime

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


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)
