from log.log import get_logger
log=get_logger()

def enter_and_leave_log(func):
    def wrapper(*args, **kwargs):
        if args:
            if kwargs:
                log.info(f"Entering {func.__name__},args is {args},kwargs is {kwargs}")
            else:
                log.info(f"Entering {func.__name__},args is {args}")
        else:
            if kwargs:
                log.info(f"Entering {func.__name__},kwargs is {kwargs}")
            else:
                log.info(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            log_str=f"Leaving {func.__name__},result type is {type(result)}, and result is {result}"
            log.info(log_str)
            return result
        except Exception as e:
            log.error(f"{func.__name__} error: {e}")
            raise e
    return wrapper