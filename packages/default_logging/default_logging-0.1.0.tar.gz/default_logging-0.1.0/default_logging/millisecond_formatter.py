import logging
import time

class MillisecondFormatter(logging.Formatter):
    """
    A logging formatter that adds milliseconds to the log time.
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        temp = time.strftime('%z')
        if temp and len(temp) == 5 and (temp[0] == '+' or temp[0] == '-'):
            self.tz_str = f"{temp[0]}{temp[1:3]}:{temp[3:5]}"
        else:
            self.tz_str = temp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
            datefmt = datefmt.replace('%z', self.tz_str)
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s

class UtcTimezoneFormatter(MillisecondFormatter):
    """
    A logging formatter that formats log times in UTC (GMT) with 'Z' offset.
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.tz_str = 'Z'

        # Set the converter to gmtime for UTC
        self.converter = time.gmtime
