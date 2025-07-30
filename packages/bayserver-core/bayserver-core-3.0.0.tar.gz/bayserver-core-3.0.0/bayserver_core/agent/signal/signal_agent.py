import socket
import signal
import threading
import traceback
from typing import ClassVar, List, Dict

from bayserver_core.bay_log import BayLog
from bayserver_core.bay_message import BayMessage
from bayserver_core.symbol import Symbol

from bayserver_core.agent.monitor.grand_agent_monitor import GrandAgentMonitor
from bayserver_core.agent.signal.signal_proxy import SignalProxy

from bayserver_core.util.sys_util import SysUtil
from bayserver_core.util.exception_util import ExceptionUtil

class SignalAgent:

    COMMAND_RELOAD_CERT = "reloadcert"
    COMMAND_MEM_USAGE = "memusage"
    COMMAND_RESTART_AGENTS = "restartagents"
    COMMAND_SHUTDOWN = "shutdown"
    COMMAND_ABORT = "abort"

    commands: ClassVar[List[str]] = [
        COMMAND_RELOAD_CERT,
        COMMAND_MEM_USAGE,
        COMMAND_RESTART_AGENTS,
        COMMAND_SHUTDOWN,
        COMMAND_ABORT
    ]

    signal_agent: ClassVar["SignalAgent"] = None
    signal_map: ClassVar[Dict[int, str]] = {}



    ######################################################
    # class methods
    ######################################################
    @classmethod
    def init(cls, bay_port):

        if bay_port > 0:
            threading.Thread(target=cls.run_signal_agent, args=[bay_port]).start()

        else:
            for cmd in cls.commands:
                sig = cls.get_signal_from_command(cmd)

                # create new scope
                def dummy():
                    cmd2 = cmd
                    SignalProxy.register(sig, lambda : cls.handle_command(cmd2))

                dummy()


    @classmethod
    def handle_command(cls, cmd):
        BayLog.debug("handle command: %s", cmd)
        if cmd.lower() == cls.COMMAND_RELOAD_CERT:
          GrandAgentMonitor.reload_cert_all()
        elif cmd.lower() ==  cls.COMMAND_MEM_USAGE:
          GrandAgentMonitor.print_usage_all()
        elif cmd.lower() == cls.COMMAND_RESTART_AGENTS:
          GrandAgentMonitor.restart_all()
        elif cmd.lower() == cls.COMMAND_SHUTDOWN:
          GrandAgentMonitor.shutdown_all()
        elif cmd.lower() == cls.COMMAND_ABORT:
          GrandAgentMonitor.abort_all()
        else:
          BayLog.error("Unknown command: %s", cmd)
        BayLog.debug("HANDLED: %s", cmd)

    @classmethod
    def get_signal_from_command(cls, command):
        cls.init_signal_map()
        for sig in cls.signal_map.keys():
            if cls.signal_map[sig].lower() == command.lower():
                return sig;

        return None

    @classmethod
    def init_signal_map(cls):
        if len(cls.signal_map) > 0:
          return

        if SysUtil.run_on_windows():
          # Available signals on Windows
          #    SIGABRT
          #    SIGFPE
          #    SIGILL
          #    SIGINT
          #    SIGSEGV
          #    SIGTERM
          print("WINDOWS REGIST")
          cls.signal_map[signal.SIGSEGV] = cls.COMMAND_RELOAD_CERT
          cls.signal_map[signal.SIGILL] = cls.COMMAND_MEM_USAGE
          cls.signal_map[signal.SIGINT] = cls.COMMAND_RESTART_AGENTS
          cls.signal_map[signal.SIGTERM] = cls.COMMAND_SHUTDOWN
          cls.signal_map[signal.SIGABRT] = cls.COMMAND_ABORT

        else:
          cls.signal_map[signal.SIGALRM] = cls.COMMAND_RELOAD_CERT
          cls.signal_map[signal.SIGTRAP] = cls.COMMAND_MEM_USAGE
          cls.signal_map[signal.SIGHUP] = cls.COMMAND_RESTART_AGENTS
          cls.signal_map[signal.SIGTERM] = cls.COMMAND_SHUTDOWN
          cls.signal_map[signal.SIGABRT] = cls.COMMAND_ABORT

    @classmethod
    def run_signal_agent(cls, port):
        server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not SysUtil.run_on_windows():
            server_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server_skt.bind(("0.0.0.0", port))
        except OSError as e:
            BayLog.error_e(e, traceback.format_stack(), BayMessage.get(Symbol.INT_CANNOT_OPEN_PORT, "0.0.0.0", port, ExceptionUtil.message(e)))

        server_skt.listen(0)
        BayLog.info(BayMessage.get(Symbol.MSG_OPEN_CTL_PORT, port))

        skt: socket.socket = None
        try:
            while True:
                skt, adr = server_skt.accept()
                skt.settimeout(5)

                f = skt.makefile("rw")
                line = f.readline().strip()
                BayLog.info(BayMessage.get(Symbol.MSG_COMMAND_RECEIVED, line))
                SignalAgent.handle_command(line)
                f.write("OK\r\n")
                f.flush()
        except BaseException as e:
            BayLog.error_e(e, traceback.format_stack())

        finally:
            if skt:
                skt.close()



