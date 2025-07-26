
from datetime import datetime, timezone
from textwrap import wrap
import json 
from decimal import Decimal
from datetime import date, time, datetime


def get_current_utc_datetime():
    now_utc = datetime.now(timezone.utc)
    current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    return current_time_utc

def check_for_content(var):
    if var:
        try:
            var = var.content
            return var.content
        except:
            return var
    else:
        var

def custom_print(message, stdscr=None, scroll_pos=0):
    if stdscr:
        max_y, max_x = stdscr.getmaxyx()
        max_y -= 2 
        wrapped_lines = []
        for line in message.split("\n"):
            wrapped_lines.extend(wrap(line, max_x))

        num_lines = len(wrapped_lines)
        visible_lines = wrapped_lines[scroll_pos:scroll_pos + max_y]

        stdscr.clear()
        for i, line in enumerate(visible_lines):
            stdscr.addstr(i, 0, line[:max_x])

        stdscr.addstr(max_y, 0, f"Lines {scroll_pos + 1} - {scroll_pos + len(visible_lines)} of {num_lines}")
        stdscr.refresh()

        return num_lines
    else:
        print(message)
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        return super().default(obj)
    
def serialize_record(row):
    record = dict(row._mapping)
    return json.loads(json.dumps(record, cls=CustomJSONEncoder))
