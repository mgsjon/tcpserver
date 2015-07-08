from time import sleep
from random import randint


def square(n):
    numbers_list = n.rstrip().split()
    response = ""
    for number in numbers_list:
        try:
            val = int(number)
            response += "Got %s. My response is %s.\n" % (val, val ** 2)
        except ValueError:
            return "I accept only numbers or 'close' command to close connection.\n"

        #sleep(randint(0, 21))

    return response
