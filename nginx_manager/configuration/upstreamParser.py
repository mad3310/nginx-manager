from pyparsing import Word, Literal, alphanums, Optional, restOfLine, ZeroOrMore

from configuration.upstream import UpStream

'''
Created on Mar 31, 2015

@author: root
'''


class UpstreamParser(object):
    def __init__(self):
        super(UpstreamParser, self).__init__()

        word = Word(alphanums + '-' + '_' + '.' + '/' + '$' + ':')
        upstream = Literal('upstream').suppress()
        lbrace = Literal('{').suppress()
        rbrace = Literal('}').suppress()
        semicolon = Literal(';').suppress()
        server = Literal('server').suppress()

        self.upstream_def = upstream + word

        self.server_def = upstream + word.suppress() + lbrace + ZeroOrMore(server + word + semicolon) + rbrace

        comment = Literal('#') + Optional(restOfLine)
        self.server_def.ignore(comment)

    def parse(self, input_):
        upstream_name = self.upstream_def.parseString(input_)
        servers_ = self.server_def.parseString(input_)

        upstream = UpStream(upstream=upstream_name, servers=servers_)
        return upstream
