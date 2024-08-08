from functools import reduce

def print_execution_time(execution_time):
    days = execution_time.days
    seconds = execution_time.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        print(f"Execution time: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
    elif hours > 0:
        print(f"Execution time: {hours} hours, {minutes} minutes, {seconds} seconds")
    elif minutes > 0:
        print(f"Execution time: {minutes} minutes, {seconds} seconds")
    else:
        print(f"Execution time: {seconds} seconds")


# See here: https://stackoverflow.com/a/58037371
def join_slash(a, b):
    return a.rstrip('/') + '/' + b.lstrip('/')
def urljoin(*args):
    return reduce(join_slash, args) if args else ''