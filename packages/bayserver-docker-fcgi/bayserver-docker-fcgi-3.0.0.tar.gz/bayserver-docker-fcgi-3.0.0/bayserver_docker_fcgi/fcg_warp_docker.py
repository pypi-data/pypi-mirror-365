from bayserver_core.agent.grand_agent import GrandAgent
from bayserver_core.agent.multiplexer.plain_transporter import PlainTransporter
from bayserver_core.bay_log import BayLog

from bayserver_core.protocol.packet_store import PacketStore
from bayserver_core.protocol.protocol_handler_store import ProtocolHandlerStore
from bayserver_core.rudder.socket_rudder import SocketRudder
from bayserver_core.ship.ship import Ship
from bayserver_core.util.io_util import IOUtil

from bayserver_core.docker.base.warp_base import WarpBase

from bayserver_docker_fcgi.fcg_docker import FcgDocker
from bayserver_docker_fcgi.fcg_packet_factory import FcgPacketFactory
from bayserver_docker_fcgi.fcg_warp_handler import FcgWarpHandler

class FcgWarpDocker(WarpBase, FcgDocker):

    def __init__(self):
        super().__init__()
        self.script_base = None
        self.doc_root = None


    ######################################################
    # Implements Docker
    ######################################################
    def init(self, elm, parent):
        super().init(elm, parent)

        if self.script_base is None:
            BayLog.warn("FCGI: docRoot is not specified")

    ######################################################
    # Implements DockerBase
    ######################################################

    def init_key_val(self, kv):
        key = kv.key.lower()
        if key == "scriptbase":
            self.script_base = kv.value
        elif key == "docroot":
            self.doc_root = kv.value
        else:
            return super().init_key_val(kv)

        return True

    ######################################################
    # Implements WarpDocker
    ######################################################
    def secure(self):
        return False

    ######################################################
    # Implements WarpDockerBase
    ######################################################
    def protocol(self):
        return FcgDocker.PROTO_NAME

    def new_transporter(self, agt: GrandAgent, rd: SocketRudder, sip: Ship):
        return PlainTransporter(
            agt.net_multiplexer,
            sip,
            False,
            IOUtil.get_sock_recv_buf_size(rd.key()),
            False)

    ######################################################
    # Class initializer
    ######################################################
    PacketStore.register_protocol(
        FcgDocker.PROTO_NAME,
        FcgPacketFactory())
    ProtocolHandlerStore.register_protocol(
        FcgDocker.PROTO_NAME,
        False,
        FcgWarpHandler.WarpProtocolHandlerFactory())
