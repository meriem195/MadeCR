#
# Copyright 2009 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import receive_path
from gnuradio import eng_notation
from uhd_interface import uhd_receiver

def add_freq_option(parser):
    """
    Hackery that has the -f / --freq option set both tx_freq and rx_freq
    """
    def freq_callback(option, opt_str, value, parser):
        parser.values.rx_freq = value
        parser.values.tx_freq = value

    if not parser.has_option('--freq'):
        parser.add_option('-f', '--freq', type="eng_float",
                          action="callback", callback=freq_callback,
                          help="set Tx and/or Rx frequency to FREQ [default=%default]",
                          metavar="FREQ")

def add_options(parser, expert):
    add_freq_option(parser)
 
    uhd_receiver.add_options(parser)
    receive_path.receive_path.add_options(parser, expert)
    expert.add_option("", "--rx-freq", type="eng_float", default=None,
                          help="set Rx frequency to FREQ [default=%default]", metavar="FREQ")
    parser.add_option("-v", "--verbose", action="store_true", default=False)

class usrp_receive_path(gr.hier_block2):

    def __init__(self, demod_class, rx_callback, options):
        '''
        See below for what options should hold
        '''
        gr.hier_block2.__init__(self, "usrp_receive_path",
                gr.io_signature(0, 0, 0),                    # Input signature
                gr.io_signature(0, 0, 0)) # Output signature
        rx_path = receive_path.receive_path(demod_class, rx_callback, options)
        for attr in dir(rx_path): #forward the methods
            if not attr.startswith('_') and not hasattr(self, attr):
                setattr(self, attr, getattr(rx_path, attr))
        #setup usrp
        args = demod_class.extract_kwargs_from_options(options)
        symbol_rate = options.bitrate / demod_class(**args).bits_per_symbol()
        self.source = uhd_receiver(options.args, symbol_rate,
            options.samples_per_symbol,
            options.rx_freq, options.rx_gain,
            options.spec, options.antenna,
            options.verbose)
        #connect
        self.connect(self.source, rx_path)

