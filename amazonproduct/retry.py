import math
import time

def retry(ExceptionToRetry, tries=5, delay=3, logger=None):
    """Retry decorator
    original from http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """
    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")
    if delay <= 0:
        raise ValueError("delay must be greater than 0")
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except ExceptionToRetry, e:
                    if mtries == 1:
                        msg = "%s, retry maxed, gave up" % str(e)
                    else:
                        msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    if mtries == 1:
                        break
                    time.sleep(mdelay)
                    mtries -= 1
            raise e
        return f_retry # true decorator
    return deco_retry
