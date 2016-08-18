from pyparsing import Word, Literal, alphanums, OneOrMore, Optional, restOfLine, Group, NotAny
from configuration.server import Server
from configuration.location import Location

'''
Created on Mar 31, 2015

@author: root
'''


class ServerParser(object):
    def __init__(self):
        super(ServerParser, self).__init__()

        word = Word(alphanums + '-' + '_' + '.' + '/' + '$' + ':')
        server = Literal('server').suppress()
        location = Literal('location')
        lbrace = Literal('{').suppress()
        rbrace = Literal('}').suppress()

        config_line = NotAny(rbrace) + word + Group(OneOrMore(word)) + Literal(';').suppress()
        location_def = location + word + lbrace + Group(OneOrMore(Group(config_line))) + rbrace
        self.server_def = server + lbrace + OneOrMore(Group(location_def) | Group(config_line)) + rbrace

        comment = Literal('#') + Optional(restOfLine)
        self.server_def.ignore(comment)

    def parse(self, input_):
        parsed = self.server_def.parseString(input_)
        server_ = {}
        locations = []
        for part in parsed:
            k = part[0]
            if k.lower() == 'location':
                locations.append(self._build_location_dict(part))
            else:
                v = ' '.join(part[1])
                server_[k] = v

        server = Server(port=int(server_.pop('listen')),
                        server_names=server_.pop('server_name').split(' '),
                        params=server_)

        for location_ in locations:
            location = Location(location=location_.pop('location'), params=location_)
            server.add_location(location)

        return server

    def _build_location_dict(self, parsed_location):
        location = {'location': parsed_location[1]}
        for part in parsed_location[2]:
            k = part[0]
            v = ' '.join(part[1])
            location[k] = v
        return location
