import argparse
import random
def string_to_int_tuple(item):
    """
    convert a string to a tuple of integeers
    :param item: a string like so '(0,1,2,3)'
    :return: a tuple like so : (0,1,2,3)
    """
    item = item.split(',')
    numbers = []
    for number in item:
        number = number.strip('(')
        number = number.strip(')')
        numbers.append(number)
    numbers = tuple(numbers)
    return (numbers)

def parse():
    parser = argparse.ArgumentParser(description='get courses and clusters')
    parser.add_argument('-courses', nargs='+', type=str, default=False,
                        help='a course number')
    parser.add_argument('-cluster', type=str, nargs='+', action='append', default=[],
                        help='for each - group a group containing the courses will be added')
    parser.add_argument('-specific_windows', nargs='+', type=str, default=False,
                        help='for each specific window : add -spedific_window (day,period) like so (0,0) means:'
                             ' (yum aleph, 8:30-9:30)')
    parser.add_argument('-specific_days_off', nargs='+', type=str, default=False,
                        help='for each specific day off add: -specific_days_off day1 day2... like so -specific_days_off 0 4')
    parser.add_argument('-lecturer', nargs='+', type=str, default=False,
                        help='add specific prefered lecturer to a courses lectuer -lecturer (c_id,lect lype, name)'
                             ' like so (61132,practice,"שגיא אריאלי"), this hould only be used for courses and '
                             'not clusters')
    return parser.parse_args()


def decision(curent_generation):
    current = 0
    sum_of_objectives = sum(solution.score for solution in curent_generation)
    pick = random.uniform(0, sum_of_objectives)
    for solution in curent_generation:
        current += solution.score
        if current > pick:
            return(solution)