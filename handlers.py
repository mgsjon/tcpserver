def square(n):
    numbers_list = n.rstrip().split('\r\n')
    response = ""
    for number in numbers_list:
        try:
            val = int(number)
            response += "Got %s. My response is %s.\r\n" % (val, val ** 2)
        except ValueError:
            return "I accept only numbers or 'close' command to close connection.\r\n"
    return response
