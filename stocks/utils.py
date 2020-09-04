from concurrent.futures.thread import ThreadPoolExecutor


def get_change(current, previous, is_abs=True):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def run_async(func):
    """
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object
            E.g.:
            @run_async
            def task1():
                do_something
            @run_async
            def task2():
                do_something_too
            t1 = task1()
            t2 = task2()
            ...
            t1.join()
            t2.join()
    """
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = THREAD_POOL.submit(func, *args, **kwargs)
        return func_hl

    return async_func


THREAD_POOL = ThreadPoolExecutor(max_workers=10)