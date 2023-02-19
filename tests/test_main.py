#  test_main.py
#
#  Copyright (c)2018 Shane Ambler <Develop@ShaneWare.biz>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

import asyncio
import os
import sys
import logging
import unittest
from unittest.mock import MagicMock, patch

import sawsc

# enable logging to simplify debugging
log = logging.getLogger('sawsc_testing_log')
#log.setLevel(logging.ERROR)
log.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
log.addHandler(stream_handler)


# experimenting with aim of getting 100% coverage.
# testing what is required to get full coverage
# and welcome opinions on whether this is a worthwhile or effective approach

#@patch('sys.platform', 'freebsd') # force testing non osx/win on osx/win platforms
class test_Sawsc(unittest.TestCase):
    #async def _start_app(self):
    #    self.app.mainloop()

    #@patch('sys.platform', 'freebsd') # why does a class patch not affect SawscApp.__init__ ?
    def setUp(self):
        self.app = sawsc.SawscApp()
        self.app.title('Sawsc test')
        # using loop gives warning on 3.10/3.11
        # running mainloop appears to make no difference to tests
        #loop = asyncio.get_event_loop()
        #loop.create_task(self._start_app())

    def tearDown(self):
        try:
            sawsc.APP_WIN = None
            self.app.destroy()
        except:
            # testing quit destroys before this call
            pass

    def test_01_start(self):
        title = self.app.winfo_toplevel().title()
        self.assertEqual(title, 'Sawsc test')

    def test_02_bindmousewheel(self):
        self.app._list._bindwheel()
        self.app._list._unbindwheel()
        # TODO no error in calls, how do I verify the bind and unbind?

    def test_03_mousewheel_num(self):
        evnt = MagicMock(name='mousewheel')
        evnt.num = 4
        self.app._list._on_mousewheel(evnt)
        evnt.num = 5
        self.app._list._on_mousewheel(evnt)
        # TODO can we verify that the contents scrolled?

    def test_04_mousewheel_delta(self):
        evnt = MagicMock(name='mousewheel')
        evnt.delta = 120
        self.app._list._on_mousewheel(evnt)
        evnt.delta = -120
        self.app._list._on_mousewheel(evnt)

    def test_05_production(self):
        for w in self.app._list._scrollable_frame.winfo_children():
            if hasattr(w, 'dev_opt'):
                w.dev_opt.invoke()

    # about box displays but requires user input to close - rename to test
    def no_test_98_about_me(self):
        self.app.about_me()

    def test_99_quit(self):
        self.app.quitkey()


## subclass to patch for multi platform code tests
@patch('sys.platform', 'osx')
class test_Sawsc_osx(test_Sawsc):
    @patch('sys.platform', 'osx')
    def setUp(self):
        super().setUp()

@patch('sys.platform', 'windows')
class test_Sawsc_windows(test_Sawsc):
    @patch('sys.platform', 'windows')
    def setUp(self):
        super().setUp()
