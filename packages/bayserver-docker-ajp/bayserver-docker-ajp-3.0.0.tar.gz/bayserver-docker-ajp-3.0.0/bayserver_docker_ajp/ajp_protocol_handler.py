from bayserver_core.protocol.protocol_handler import ProtocolHandler
from bayserver_core.protocol.packet_packer import PacketPacker
from bayserver_core.protocol.command_packer import CommandPacker

from bayserver_docker_ajp.ajp_command_unpacker import AjpCommandUnPacker
from bayserver_docker_ajp.ajp_docker import AjpDocker
from bayserver_docker_ajp.ajp_handler import AjpHandler
from bayserver_docker_ajp.ajp_packet_unpacker import AjpPacketUnPacker
from bayserver_docker_ajp.ajp_command_handler import AjpCommandHandler
from bayserver_docker_ajp.command.cmd_data import CmdData
from bayserver_docker_ajp.command.cmd_send_body_chunk import CmdSendBodyChunk


class AjpProtocolHandler(ProtocolHandler):

    def __init__(self,
                 h1_handler: AjpHandler,
                 packet_unpacker: AjpPacketUnPacker,
                 packet_packer: PacketPacker,
                 command_unpacker: AjpCommandUnPacker,
                 command_packer: CommandPacker,
                 svr_mode: bool):
        super().__init__(
            packet_unpacker,
            packet_packer,
            command_unpacker,
            command_packer,
            h1_handler,
            svr_mode
        )

    def __str__(self):
        return f"pch[{self.ship}]"


    ######################################################
    # Implements ProtocolHandler
    ######################################################

    def protocol(self):
        return AjpDocker.PROTO_NAME

    def max_req_packet_data_size(self):
        return CmdData.MAX_DATA_LEN

    def max_res_packet_data_size(self):
        return CmdSendBodyChunk.MAX_CHUNKLEN

