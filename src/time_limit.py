import signal

class timeout:
    '''
    http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish/22348885#22348885
    see also:
        https://stackoverflow.com/questions/15528939/python-3-timed-input
        http://stackoverflow.com/questions/492519/timeout-on-a-function-call
        http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
    '''
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class TimedExecution:
    def __init__(self, limit=1, error_message='Timeout'):
        self.limit = limit
        self.error_message = error_message

    def run(self, func, *args, **kwargs):
        with timeout(seconds=self.limit, error_message=self.error_message):
            return func(*args, **kwargs)
