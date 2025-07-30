from heapq import heappop, heappush
from collections import deque
from typing import *
from functools import partial, wraps
import os

class EventInQueue: # the events can be sorted by the queue
    def __init__(self, time, func_ptr, func_args):
        self.time = time
        self.func_ptr = func_ptr
        self.func_args = func_args

    def __lt__(self, other):
        return self.time < other.time

class Environment:
    def __init__(self, initial_time:float=0):
        self.queue:List[EventInQueue] = [] # <-- heap
        self.now:float = initial_time
        self.processes:List["Process"] = []
        self._init=False
        self._num_insert=0
        self._num_pop=0
        self._until=0.

    def process(self, p):
        #if isinstance(p, Process): # TODO <-- to remove and replaced by Process2
        #    self.lps.append(p)
        #elif isinstance(p, Store):
        self.processes.append(p)


        self._init=False
    def _initialize(self):
        for p in self.processes:
            p.on_initialize(env=self)
        self._init = True

    def get_now(self)->float:
        """
        Common getter with EnvironmentMP, in envionmentMP getting this value is protected with mutex.
        :return:
        """
        return self.now

    def set_now(self, now: float):
        self.now=now

    def run(self, until:float):
        if not self._init:
            self._initialize()

        func_ptr="do_nothing"
        self._until = until

        while until > self.get_now():
            now, func_ptr, func_args=self.next_event(until)
            if until > now:
                # run it
                self.set_now(now)
                func_ptr(*func_args)
            else:
                # reschedule for future
                # Strategy 1: ex. simpn project, where we compute the event even if it is after "until"
                # event = EventInQueue(self.get_now(), func_ptr, func_args)
                # heappush(self.queue, event)
                # Strategy 2: ex. simpy project, where the event is re-scheduled
                if func_ptr != "do_nothing":
                    event = EventInQueue(now, func_ptr, func_args)
                    heappush(self.queue, event) # reschedule for a future Environment.run(until2) with until2 > current until
                self.set_now(until)  # exit

    def timeout(self, t, func_ptr, func_args):
        event=EventInQueue(self.get_now() + t, func_ptr, func_args)
        heappush(self.queue, event)
        self._num_insert+=1

    def next_event(self, until)->Tuple[float, Callable, Tuple[object]]:
        if not self.queue:
            #print(f"t:{until} STOP_EVENT pid:{os.getpid()}")
            return until, "do_nothing", tuple()
        event=heappop(self.queue)
        #print(event)
        self._num_pop+=1
        return event.time, event.func_ptr, event.func_args

class Process: # ABSTRACT CLASS
    def on_initialize(self, env:Environment):
        pass

class Store:
    def __init__(self, capacity=float('inf')):
        self.env = None
        self._capacity = capacity
        self.items=[]
        self.waiting=[]
    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def on_put(self, obj):
        if len(self.items) < self._capacity:
            self.items.append(obj)
            if self.waiting:
                while (self.waiting and self.items):
                    #self.env.timeout(10, self.waiting.pop(), tuple([self.items.pop()]))
                    self.waiting.pop()(self.items.pop())

    def on_get(self, pro):
        if self.items:
            pro(self.items.pop())
        else:
            self.waiting.append(pro)

# URL: https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/events.py?ref_type=heads#L51
class Event:
    def __init__(self, env: Environment):
        self.env = env
        self.callbacks = []
        self._ok = None

    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def add_callback(self, callback:Callable, args=tuple()):
        if self._ok:
            callback(*args)
        else:
            self.callbacks.append((callback, args))

    def _call_callbacks(self):
        while self.callbacks:
            callback, args = self.callbacks.pop()
            callback(*args)
            #self.env.timeout(0, callback, args)

    def on_trigger(self):
        """
        call in cascade the callbacks
        """
        self._ok = True
        self._call_callbacks()

    def succeed(self):
        """  ensure Simpy API compatibility """
        self._ok = True
        self._call_callbacks()
        return self

    def fail(self):
        self._ok = False
        self._call_callbacks()
        return self

    def __and__(self, other: 'Event') -> 'Condition':
        """Return a :class:`~simpy.events.Condition` that will be triggered if
        both, this event and *other*, have been processed."""
        return Condition(self.env, Condition.all_events, [self, other])

    def __or__(self, other: 'Event') -> 'Condition':
        """Return a :class:`~simpy.events.Condition` that will be triggered if
        either this event or *other* have been processed (or even both, if they
        happened concurrently)."""
        return Condition(self.env, Condition.any_events, [self, other])


class Condition(Event):
    def __init__(self, env:Environment, evaluate: Callable[[Tuple[Event, ...], int], bool], events: Iterable[Event]):
        super().__init__(env)
        self._evaluate=evaluate
        self._events=events
        self._count=0

        # Immediately succeed if no events are provided.
        if not self._events:
            self.succeed()
            return

        # Check if events belong to the same environment.
        for event in self._events:
            if self.env != event.env:
                raise ValueError(
                    'It is not allowed to mix events from different environments'
                )

        # Check if the condition is met for each processed event. Attach
        # _check() as a callback otherwise.
        for event in self._events:
            #if event.callbacks is None:
            #    self._check(event)
            #else:
            event.callbacks.append((self._check, (event,)))

        # Register a callback which will build the value of this condition
        # after it has been triggered.
        assert isinstance(self.callbacks, list)
        #self.callbacks.append(self._build_value)

    def _check(self, event: Event) -> None:
        """Check if the condition was already met and schedule the *event* if
        so."""
        #if self._value is not PENDING:
        #    return

        self._count += 1

        if self._evaluate(self._events, self._count):
            # The condition has been met. The _build_value() callback will
            # populate the ConditionValue once this condition is processed.
            self.succeed() # change its internal state
        else:
            pass # Neither `_ok` is still pending

    @staticmethod
    def all_events(events: Tuple[Event, ...], count: int) -> bool:
        """An evaluation function that returns ``True`` if all *events* have
        been triggered."""
        return len(events) == count

    @staticmethod
    def any_events(events: Tuple[Event, ...], count: int) -> bool:
        """An evaluation function that returns ``True`` if at least one of
        *events* has been triggered."""
        return count > 0 or len(events) == 0

class Resource:
    def __init__(self, env: Environment, capacity: int = 1):
        self.env = env
        self.capacity = capacity
        self.users = 0
        self.queue = deque()

    def on_initialize(self, env):
        self.env = env
        # Store object are passive and should not call callbacks

    def on_request(self, what_to_do_when_release: Callable, args:tuple = tuple()):
        if self.capacity > self.users:
            self.users += 1
            #self.users.append((what_to_do_when_release,args))
            what_to_do_when_release(*args)
        else:
            self.queue.append((what_to_do_when_release,args))


    def on_release(self, what_to_do_when_release: Callable, args:tuple = tuple()):
        self.users -= 1

        # Some objects in queues are transfered in users
        while self.queue and self.users<self.capacity:
            self.users += 1
            call, args = self.queue.pop()
            call(*args)

class Interruption:
    def __init__(self, env):
        self.env=env
        self.callbacks_to_interrupt=[]

    def on_init(self, env):
        self.env=env

    def add_interruption(self, callback_to_interupt):
        self.callbacks_to_interrupt.append(callback_to_interupt)

    def on_interruption(self):
        for c in self.callbacks_to_interrupt:
            for e in self.env.queue:
                if e.func_ptr==c:
                    self.env.queue.remove(e)

# URL: https://gitlab.com/team-simpy/simpy/-/blob/master/src/simpy/resources/container.py?ref_type=heads#L55
class Container:
    def __init__(self, env: Environment, capacity: float = float('inf'), initial: float = 0.0):
        self.env = env
        self.capacity = capacity
        self.level = initial
        self.put_waiters = []   # [(amount, callback)]
        self.get_waiters = []   # [(amount, callback)]

    def on_initialize(self, env):
        self.env = env

    def put(self, amount: float, callback: Callable = None):
        """Try to put 'amount' unités. If not possible, try later."""
        if self.level + amount <= self.capacity:
            self.level += amount
            if callback: # the producer if something after putting (if any callback)
                callback(amount)

            # Try to wake up waiters
            self._try_release_getters()
        else:
            self.put_waiters.append((amount, callback))

    def get(self, amount: float, callback: Callable):
        """Try to pull 'amount' units."""
        if self.level >= amount:
            self.level -= amount
            callback(amount)
            self._try_release_putters()
        else:
            self.get_waiters.append((amount, callback))

    def _try_release_getters(self):
        ready = []
        for amount, callback in list(self.get_waiters):
            if self.level >= amount:
                self.level -= amount
                ready.append((amount, callback))
                self.get_waiters.remove((amount, callback))
        for amount, callback in ready:
            callback(amount)

    def _try_release_putters(self):
        ready = []
        for amount, callback in list(self.put_waiters):
            if self.level + amount <= self.capacity:
                self.level += amount
                ready.append((amount, callback))
                self.put_waiters.remove((amount, callback))

        for amount, callback in ready:
            if callback:
                callback(amount)

import heapq

class PriorityResource:
    def __init__(self, env: "Environment", capacity: int = 1):
        self.env = env
        self.capacity = capacity
        self.users = 0
        self.queue = []  # heapq: (priority, order, callback, args)
        self._counter = 0  # tie-breaker for FIFO in same priority

    def on_initialize(self, env):
        self.env = env

    def on_request(self, callback: callable, args: tuple = tuple(), priority: int = 0):
        """Request the resource. Callback is executed when the resource is available."""
        if self.users < self.capacity:
            # Grant resource immediately
            self.users += 1
            callback(*args)
        else:
            # Put in priority queue
            heapq.heappush(self.queue, (priority, self._counter, callback, args))
            self._counter += 1

    def on_release(self):
        """Release the resource and wake up the highest-priority waiting request."""
        self.users -= 1
        while self.queue and self.users < self.capacity:
            # Get highest-priority request
            priority, _, callback, args = heapq.heappop(self.queue)
            self.users += 1
            callback(*args)

class PreemptiveResource:
    def __init__(self, env, capacity=1):
        self.env = env
        self.capacity = capacity
        self.users = []  # [(priority, order, name, preemptable, preempted_cb)]
        self.queue = []  # [(priority, order, preemptable, name, callback, args, preempted_cb)]
        self._counter = 0

    def on_initialize(self, env):
        self.env = env

    def on_request(self, name, callback, args=(), priority=0, preempt=True, on_preempted=None):
        """
        Request the resource.
        - Lower priority number means higher importance.
        - preempt=False means this user cannot be preempted and blocks later users.
        """
        if len(self.users) < self.capacity:
            # Resource is free
            self._grant(name, priority, preempt, callback, args, on_preempted)
        else:
            # Check if we can preempt an active user (only if no blocking queued requests)
            if preempt and self._can_preempt(priority):
                self._do_preempt(name, priority, preempt, callback, args, on_preempted)
            else:
                # Queue the request
                heapq.heappush(
                    self.queue,
                    (priority, self._counter, preempt, name, callback, args, on_preempted)
                )
                self._counter += 1

    def _grant(self, name, priority, preempt, callback, args, on_preempted):
        """Grant the resource to a user."""
        self.users.append((priority, self._counter, name, preempt, on_preempted))
        self._counter += 1
        callback(*args)

    def _can_preempt(self, priority):
        """Only preempt if we find a strictly lower-priority active user."""
        # If there is a non-preemptable user waiting in queue, we can't preempt anyone
        if any(not q[2] for q in self.queue):  # q[2] = preempt flag
            return False

        # Find the active user with the worst priority
        worst_user = max(self.users, key=lambda u: (u[0], u[1]))
        return priority < worst_user[0] and worst_user[3]  # user[3]=preemptable

    def _do_preempt(self, name, priority, preempt, callback, args, on_preempted):
        """Preempt the worst user."""
        worst_user = max(self.users, key=lambda u: (u[0], u[1]))
        self.users.remove(worst_user)
        _, _, preempted_name, _, preempted_cb = worst_user

        # Notify preempted user
        if preempted_cb:
            preempted_cb()

        # Grant resource to the new user
        self._grant(name, priority, preempt, callback, args, on_preempted)

    def on_release(self, name):
        """Release resource and assign it to the next waiting request."""
        # Remove the current user
        self.users = [u for u in self.users if u[2] != name]

        # Serve next in queue respecting priority and FIFO
        while self.queue and len(self.users) < self.capacity:
            priority, _, preempt, q_name, cb, args, preempted_cb = heapq.heappop(self.queue)
            self._grant(q_name, priority, preempt, cb, args, preempted_cb)

class FilterStore:
    def __init__(self, env, capacity=float('inf')):
        self.env = env
        self.capacity = capacity
        self.items = []  # Items currently in the store
        self.put_queue = deque()  # Waiting puts (if full)
        self.get_queue = deque()  # Waiting gets (with filters)

    def on_initialize(self, env):
        self.env = env

    def put(self, item, callback=None):
        """Insert an item into the store, or wait if the store is full."""
        if len(self.items) < self.capacity:
            self.items.append(item)
            if callback:
                callback(item)
            # Wake up any waiting getters
            self._try_release_getters()
        else:
            # Queue the put if store is full
            self.put_queue.append((item, callback))

    def get(self, filter_fn, callback):
        """
        Try to get an item that matches filter_fn.
        If no matching item is available, enqueue the request.
        """
        for idx, item in enumerate(self.items):
            if filter_fn(item):
                chosen = self.items.pop(idx)
                callback(chosen)
                # After removing, maybe unblock waiting puts
                self._try_release_putters()
                return

        # No item matches → enqueue this get
        self.get_queue.append((filter_fn, callback))

    def _try_release_getters(self):
        """Try to satisfy waiting gets if items available."""
        ready = []
        for filter_fn, callback in list(self.get_queue):
            for idx, item in enumerate(self.items):
                if filter_fn(item):
                    chosen = self.items.pop(idx)
                    ready.append((callback, chosen))
                    self.get_queue.remove((filter_fn, callback))
                    break

        for callback, chosen in ready:
            callback(chosen)
            self._try_release_putters()

    def _try_release_putters(self):
        """Try to satisfy waiting puts if space available."""
        while self.put_queue and len(self.items) < self.capacity:
            item, callback = self.put_queue.popleft()
            self.items.append(item)
            if callback:
                callback(item)
            self._try_release_getters()

class PriorityItem:
    """Wraps an item with a priority for PriorityStore."""
    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        return self.priority < other.priority

class PriorityStore:
    def __init__(self, env, capacity=float('inf')):
        self.env = env
        self.capacity = capacity
        self._heap = []  # Heap for priority order
        self.put_queue = []  # Waiting puts if store is full
        self.get_queue = []  # Waiting gets

    def on_initialize(self, env):
        self.env = env

    def put(self, item, callback=None):
        """Put an item in the store or wait if full."""
        if len(self._heap) < self.capacity:
            heapq.heappush(self._heap, item)
            if callback:
                callback(item)
            # Try to release waiting getters
            self._try_release_getters()
        else:
            self.put_queue.append((item, callback))

    def get(self, callback):
        """Get the highest-priority item or wait if empty."""
        if self._heap:
            item = heapq.heappop(self._heap)
            callback(item)
            # Try to release any waiting puts
            self._try_release_putters()
        else:
            self.get_queue.append(callback)

    def _try_release_getters(self):
        """Serve waiting getters if items are available."""
        while self._heap and self.get_queue:
            callback = self.get_queue.pop(0)
            item = heapq.heappop(self._heap)
            callback(item)
            self._try_release_putters()

    def _try_release_putters(self):
        """Serve waiting puts if there is capacity."""
        while self.put_queue and len(self._heap) < self.capacity:
            item, callback = self.put_queue.pop(0)
            heapq.heappush(self._heap, item)
            if callback:
                callback(item)
            self._try_release_getters()
