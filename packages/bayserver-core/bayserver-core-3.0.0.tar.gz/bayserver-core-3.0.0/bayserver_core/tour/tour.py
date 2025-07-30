import threading
from typing import Optional, List

from bayserver_core import bayserver as bs
from bayserver_core.bay_log import BayLog
from bayserver_core.common import inbound_ship as isip
from bayserver_core.http_exception import HttpException
from bayserver_core.ship.ship import Ship
from bayserver_core.sink import Sink
from bayserver_core.tour import tour_req
from bayserver_core.tour import tour_res
from bayserver_core.tour.tour_req import TourReq
from bayserver_core.tour.tour_res import TourRes
from bayserver_core.util.counter import Counter
from bayserver_core.util.http_status import HttpStatus
from bayserver_core.util.reusable import Reusable


class Tour(Reusable):

    class TourState:
        UNINITIALIZED = 0
        PREPARING = 1
        READING = 2
        RUNNING = 3
        ABORTED = 4
        ENDED = 5
        ZOMBIE = 6

    # class variables
    oid_counter: Counter = Counter()
    tour_id_counter: Counter = Counter()

    TOUR_ID_NOCHECK = -1
    INVALID_TOUR_ID = 0

    ship: "isip.InboundShip"
    ship_id: int
    obj_id: int

    req: TourReq
    res: TourRes
    lock: threading.Lock
    tour_id: int
    error_handling: bool
    town: "Town"
    city: "City"
    club: "Club"
    interval: int
    is_secure: bool
    error: Optional[BaseException]
    stack: Optional[List[str]]
    state: int

    def __init__(self):
        self.ship = None
        self.ship_id = None
        self.obj_id = Tour.oid_counter.next() # object id
        self.req = tour_req.TourReq(self)
        self.res = tour_res.TourRes(self)
        self.lock = threading.RLock()
        self.tour_id = Tour.INVALID_TOUR_ID
        self.error_handling = None
        self.town = None
        self.city = None
        self.club = None
        self.interval = None
        self.is_secure = None
        self.error = None
        self.state = None

        self.reset()


    def id(self):
        return self.tour_id

    def __str__(self):
        return f"{self.ship} tour#{self.tour_id}/{self.obj_id} [key={self.req.key}]";

    ######################################################
    # implements Reusable
    ######################################################
    def reset(self):
        self.city = None
        self.town = None
        self.club = None
        self.error_handling = False
        self.change_state(Tour.TOUR_ID_NOCHECK, Tour.TourState.UNINITIALIZED)
        self.tour_id = Tour.INVALID_TOUR_ID
        self.interval = 0
        self.is_secure = False
        self.error = None
        self.req.reset()
        self.res.reset()



    ######################################################
    # other methods
    ######################################################
    def init(self, key, sip):
        if self.is_initialized():
            raise Sink("%s Tour already initialized: state=%d", self, self.state)

        self.ship = sip
        self.ship_id = sip.ship_id
        if self.ship_id == Ship.INVALID_SHIP_ID:
            raise Sink()

        self.tour_id = Tour.tour_id_counter.next()
        self.change_state(Tour.TOUR_ID_NOCHECK, Tour.TourState.PREPARING)

        self.req.init(key)
        self.res.init()

        BayLog.debug("%s initialized", self)

    def go(self):
        city = self.ship.port_docker.find_city(self.req.req_host)
        if city is None:
            city = bs.BayServer.find_city(self.req.req_host)

        if self.req.headers.content_length() > 0:
            BayLog.info("Set state reading")
            self.change_state(Tour.TOUR_ID_NOCHECK, Tour.TourState.READING)
        else:
            BayLog.info("Set state running")
            self.change_state(Tour.TOUR_ID_NOCHECK, Tour.TourState.RUNNING)

        BayLog.debug("%s GO TOUR! ...( ^_^)/: city=%s url=%s", self, self.req.req_host, self.req.uri)

        if city is None:
            raise HttpException(HttpStatus.NOT_FOUND, self.req.uri)
        else:
            city.enter(self)

    def is_valid(self):
        return self.state == Tour.TourState.PREPARING or self.state == Tour.TourState.READING or self.state == Tour.TourState.RUNNING

    def is_preparing(self):
        return self.state == Tour.TourState.PREPARING

    def is_reading(self):
        return self.state == Tour.TourState.READING

    def is_running(self):
        return self.state == Tour.TourState.RUNNING

    def is_zombie(self):
        return self.state == Tour.TourState.ZOMBIE

    def is_aborted(self):
        return self.state == Tour.TourState.ABORTED

    def is_ended(self):
        return self.state == Tour.TourState.ENDED

    def is_initialized(self):
        return self.state != Tour.TourState.UNINITIALIZED

    def change_state(self, chk_id, new_state):
        BayLog.trace("%s change state: %s", self, new_state)
        self.check_tour_id(chk_id)
        self.state = new_state

    def check_tour_id(self, chk_id):
        if chk_id == Tour.TOUR_ID_NOCHECK:
            return

        if not self.is_initialized():
            raise Sink("%s Tour not initialized", self)

        if chk_id != self.tour_id:
            raise Sink("%s Invalid tour id: %s", self, "" if chk_id is None else str(chk_id))

