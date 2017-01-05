import traceback
from multiprocessing.pool import Pool
import multiprocessing
from time import sleep

def defaultExceptionHandler(e, *args, **kwargs):
    multiprocessing.log_to_stderr()
    multiprocessing.get_logger().error(traceback.format_exc())
    if isinstance(e, KeyboardInterrupt):
        raise Exception("KeyboardInterrupt")

class LogExceptions(object):
    def __init__(self, callable, exceptionHandler):
        self.__callable = callable
        self.exceptionHandler = exceptionHandler

    def __call__(self, *args, **kwargs):
        result = None
        try:
            result = self.__callable(*args, **kwargs)

        except BaseException as e:
            if self.exceptionHandler is not None:
                self.exceptionHandler(e, *args, **kwargs)

        return result

class LoggingPool(Pool):
    def __init__(self, processes=None, initializer=None, initargs=(), exceptionHandler=defaultExceptionHandler):
        Pool.__init__(self, processes, initializer, initargs)
        self.exceptionHandler = exceptionHandler

    def map_async(self, func, iterable, chunksize=None, callback=None):
        return Pool.map_async(self, LogExceptions(func, self.exceptionHandler), iterable, chunksize=chunksize, callback=callback)

    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(self, LogExceptions(func), args=args, kwds=kwds, callback=callback)

def go(additive):
    print "{0} started: ".format(additive)
    sleep(2)
    if additive == 1:
        raise Exception()
    print "{0} ended: ".format(additive)
    return additive

if __name__ == "__main__":
    p = LoggingPool(processes=2)

    res = p.map_async(go, [i for i in range(3)])
    try:
        print res.get()
        # sleep(10)
    except KeyboardInterrupt:
        print "Halt gracefully"
        p.terminate()
    except Exception as e:
        print "exception: " + str(e)
        p.terminate()
    else:
        p.close()
    finally:
        p.join()
