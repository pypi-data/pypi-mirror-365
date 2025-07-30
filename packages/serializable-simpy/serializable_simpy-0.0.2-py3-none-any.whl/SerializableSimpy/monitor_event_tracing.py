from SerializableSimpy.core import Environment, Process, Event
from functools import wraps
from typing import Callable

# URL: simpy equivalent https://simpy.readthedocs.io/en/latest/topical_guides/monitoring.html#event-tracing
def trace(env: Environment, callback: Callable):
    def get_wrapper(env_step, callback: Callable):

        @wraps(env_step)
        def tracing_step(until):
            t, f, a = env_step(until)
            callback(t, env._num_pop - 1, f)
            return t, f, a
        return tracing_step

    env.next_event = get_wrapper(env.next_event, callback)


""" `event` is a function that updates the simulation state. 
It is generally what we want to trace to understand what happens in the simulation. 

The logging is either:
* a dict: aggregation of events (#events -> occurrence) to get a coarse-grain view.
* a list or a file: to get a chronological view. WARNING: this may dramatically slow down and flood the memory.

The event loop (in SerializableSimpy.core) calls events.
Let's take the usual example of a Class named Clock containing 2 attributes: on_tick() and name (e.g., "fast").
The event processed is clock.on_tick with clock an instance of Clock.
There are 3 modes to display the event in the monitoring:
* the class name: here "Clock".
* the function name: "clock.on_tick".
* the object name: "fast". If the `name` is missing, it is the default "noname".
"""

def _from_func2func_name(event: Callable) -> str:
    """Return function name from event (e.g., on_tick)."""
    return event.__func__.__qualname__

def _from_func2class_name(event: Callable) -> str:
    """Return class name from event (e.g., Clock)."""
    return type(event.__self__).__name__

def _from_func2object_name(event: Callable) -> str:
    """Return object name (e.g., clock.name if exists, else "noname")."""
    obj = event.__self__
    return getattr(obj, "name", "noname")


# When log is a list

def monitor_list_class(data: list, t: float, eid: int, event: Callable):
    txt = _from_func2class_name(event)
    data.append((t, eid, txt))

def monitor_list_object(data: list, t: float, eid: int, event: Callable):
    txt = _from_func2object_name(event)
    data.append((t, eid, txt))

def monitor_list_func(data: list, t: float, eid: int, event: Callable):
    txt = _from_func2func_name(event)
    data.append((t, eid, txt))


# When log is a dict

def _plus_one(data, k):
    data[k] = data.get(k, 0) + 1

def monitor_dict_class(data: dict, t: float, eid: int, event: Callable):
    txt = _from_func2class_name(event)
    _plus_one(data, txt)

def monitor_dict_object(data: dict, t: float, eid: int, event: Callable):
    txt = _from_func2object_name(event)
    _plus_one(data, txt)

def monitor_dict_func(data: dict, t: float, eid: int, event: Callable):
    txt = _from_func2func_name(event)
    _plus_one(data, txt)


# When log is a file

def monitor_file_class(file, t: float, eid: int, event: Callable):
    txt = _from_func2class_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")

def monitor_file_object(file, t: float, eid: int, event: Callable):
    txt = _from_func2object_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")

def monitor_file_func(file, t: float, eid: int, event: Callable):
    txt = _from_func2func_name(event)
    file.write(f"{t}\t{eid}\t{txt}\n")
