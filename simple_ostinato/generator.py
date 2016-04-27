import os
from jinja2 import Environment, PackageLoader
from . import constants


class _Generator(object):

    class Attribute(object):

        def __init__(self, name, offset, default_value, mask, ext_name, computed, doc):
            self.name = name
            self.offset = offset
            self.default_value = default_value
            self.mask = mask
            self.ext_name = ext_name
            if computed is True:
                doc = '{}. By default, this attribute is computed automatically.'.format(doc)
            self.doc = doc

    def __init__(self, attributes, class_name=None, protocol_id=None, extension=None, doc=None):
        self.class_name = class_name
        self.protocol_id = protocol_id
        self.extension = extension
        self.doc = doc
        self.attributes = []
        for attribute_name, attribute in attributes.iteritems():
            self.attributes.append(self.Attribute(attribute_name, *attribute))


def generate_classes():
    protocols = [
        {
            'class_name':   'Mac',
            'doc':          'Represent the MAC layer. Since we make a distiction between the MAC layer and the Ethernet layer, this layer defines the source and destination MAC addresses.',
            'protocol_id':  constants._Protocols.MAC,
            'extension':    'mac_pb2.mac',
            'attributes': {
                'destination': (0, '00:00:00:00:00:00', 0xffffffffffff, 'dst_mac', False, 'Destination MAC address'),
                'source':      (6, 'FF:FF:FF:FF:FF:FF', 0xffffffffffff, 'src_mac', False, 'Source MAC address'),
            },
        },
        {
            'class_name':   'Ethernet',
            'doc':          'Represent the ethernet layer. Since we make a distinction between the MAC layer and the Ethernet layer, this layer only defines the ethernet type',
            'protocol_id':  constants._Protocols.ETHERNET_II,
            'extension':    'eth2_pb2.eth2',
            'attributes': {
                'ether_type': (0, '0x0800', 0xffff, 'type', False, 'Ethernet type field. 0x800 is for IPv4 inner packets.'),
            },
        },
        {
            'class_name':   'IPv4',
            'doc':          'Represent the IPv4 layer.',
            'protocol_id':  constants._Protocols.IP4,
            'extension':    'ip4_pb2.ip4',
            'attributes': {
                'version':          (0,  4,           '0xf0',       'ver_hdrlen', False, 'Version of the protocol (usually 4 or 6)'),
                'header_length':    (0,  5,           '0x0f',       'ver_hdrlen', True,  'Internet Header Length (IHL): number of 4 bytes words in the header. The minimum valid value is 5, and maximum valid value is 15.'),
                'tos':              (1,  0,           '0xff',       'tos'       , False, 'Type Of Service (TOS) field. This field is now the Differentiated Services Code Point (DSCP) field.'),
                'dscp':             (1,  0,           '0xff',       'tos'       , False, 'Differentiated Services Code Point (DSCP) field (previously known as Type Of Service (TOS) field'),
                'total_length':     (2,  0,           '0xffff',     'totlen'    , True,  'Total length of the IP packet in bytes. The minimum valid value is 20, and the maxium is 65,535'),
                'identification':   (2,  0,           '0xffff',     'id'        , False, 'Identification field. This is used to identify packet fragments'),
                'flags':            (6,  0,           '0xe0',       'flags'     , False, 'A three bits field: bit 0 is reserved, bit 1 is the Don\'t Fragment (DF) flag, and bit 2 is the More Fragments (MF) flags'),
                'fragments_offset': (6,  0,           '0x1fff',     'frag_ofs'  , False, 'The Fragment Offset field indicates the offset of a packet fragment in the original IP packet'),
                'ttl':              (8,  127,         '0xff',       'ttl'       , False, 'Time To Live (TTL) field.'),
                'protocol':         (9,  0,           '0xff',       'proto'     , False, 'Indicates the protocol that is encapsulated in the IP packet.'),
                'checksum':         (10, 0,           '0xffff',     'cksum'     , True,  'Header checksum'),
                'source':           (12, '127.0.0.1', '0xffffffff', 'src_ip'    , False, 'Source IP address'),
                'destination':      (16, '127.0.0.1', '0xffffffff', 'dst_ip'    , False, 'Destination IP address'),
            },
        },
        {
            'class_name':   'Udp',
            'doc':          'Represent an UDP datagram',
            'protocol_id':  constants._Protocols.UDP,
            'extension':    'udp_pb2.udp',
            'attributes': {
                'source':       (0, 49152, 0xffff, 'src_port', False, 'Source port number'),
                'destination':  (2, 49153, 0xffff, 'dst_port', False, 'Destination port number'),
                'length':       (4, 0,     0xffff, 'totlen',   True,  'Length of the UDP datagram (header and payload).'),
                'checksum':     (6, 0,     0xffff, 'cksum',    True,  'Checksum of the datagram, calculated based on the IP pseudo-header.')
            },
        },
        {
            'class_name':   'Tcp',
            'doc':          'Represent an TCP datagram',
            'protocol_id':  constants._Protocols.TCP,
            'extension':    'tcp_pb2.tcp',
            'attributes': {
                'source':           (0,  49152, 0xffff,      'src_port',    False, 'Source port number'),
                'destination':      (2,  49153, 0xffff,      'dst_port',    False, 'Destination port number'),
                'sequence_num':     (4,  0,     0xffffffff,  'seq_num',     False, 'Sequence number of the datagram. Its meaning depends on the :attr:`syn` flag value.'),
                'ack_num':          (8,  0,     0xffffffff,  'ack_num',     False, 'Acknowledgement number'),
                'header_length':    (12, 0,     0xf0,        'hdrlen_rsvd', False,  'Size of the TCP header in 4 bytes words. This field is also known as "Data offset"'),
                'reserved':         (12, 0,     0x0e,        'hdrlen_rsvd', False,  'Reserved for future use and must be set to 0'),
                'flag_ns':          (12, 0,     0x01,        'hdrlen_rsvd', False, 'ECN-nonce concealment protection (experimental)'),
                'flag_cwr':         (13, 0,     0x01 << 7,   'flags',       False, 'Congestion Window Reduced flag'),
                'flag_ece':         (13, 0,     0x01 << 6,   'flags',       False, 'ECN-Echo flag. Its meaning depends on the :attr:`syn` field value.'),
                'flag_urg':         (13, 0,     0x01 << 5,   'flags',       False, 'Urgent pointer flag.'),
                'flag_ack':         (13, 0,     0x01 << 4,   'flags',       False, 'ACK flag'),
                'flag_psh':         (13, 0,     0x01 << 3,   'flags',       False, 'Push function'),
                'flag_rst':         (13, 0,     0x01 << 2,   'flags',       False, 'Reset the connection'),
                'flag_syn':         (13, 0,     0x01 << 1,   'flags',       False, 'Synchronize sequence numbers'),
                'flag_fin':         (13, 0,     0x01,        'flags',       False, 'No more data from sender'),
                'window_size':      (14, 0,     0xffff,      'window',      False, 'Size of the receive window, which specifies the number of window size units that the sender of this segment is currently willing to receive'),
                'checksum':         (16, 0,     0xffff,      'cksum',       True,  'Checksum of the datagram, calculated based on the IP pseudo-header. Its meaning depends on the value og the :attr:`ack` flag.'),
                'urgent_pointer':   (18, 0,     0xffff,      'urg_ptr',     False, 'Urgent pointer.')
            },
        },
        {
            'class_name': 'Payload',
            'doc':        'Represent the payload. This layer can be encapsulated in any other layer',
            'protocol_id': constants._Protocols.PAYLOAD,
            'extension': 'payload_pb2.payload',
            'attributes': {
                'mode':     (None, 'FIXED_WORD',  None,   'pattern_mode', False, 'Mode to generate the payload content'),
                'pattern':  (0,    '00 00 00 00', 0xffff, 'pattern',      False, 'Payload initial word. Depending on the chosen mode, this word will be repeated unchanged, incremented/decremented, or randomized'),
            },
        },
    ]
    data = []
    for protocol in protocols:
        data.append(_Generator(**protocol))
    env = Environment(loader=PackageLoader('simple_ostinato', 'templates'))
    template = env.get_template('protocols.tpl')
    pkg_dir = os.path.dirname(os.path.realpath(__file__))
    target = os.path.join(pkg_dir, 'protocols', 'autogenerates.py')
    with open(target, 'w') as file_:
        file_.write(template.render(classes=data))

if __name__ == '__main__':
    generate_classes()
