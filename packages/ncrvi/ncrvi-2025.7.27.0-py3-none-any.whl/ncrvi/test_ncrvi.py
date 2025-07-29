#!/usr/bin/env --split-string=python -m pytest --verbose

"""Implement the tests"""

import pytest
import random
import time
import os
import textwrap
import re

from .command import Command

class TestCase_Ncrvi:

    POWER_ON_WAIT = float(os.environ['POWER_ON_WAIT'])
    INITIAL_WAIT = float(os.environ['INITIAL_WAIT'])
    POWER_OFF_WAIT = float(os.environ['POWER_OFF_WAIT'])
    SETTLING_DELAY = float(os.environ['SETTLING_DELAY'])
    EXPECTED_COMPONENTS = int(os.environ['EXPECTED_COMPONENTS'])
    HOW_OFTEN = int(os.environ['HOW_OFTEN'])
    USER = os.environ['USER']
    TARGET = os.environ['TARGET']

    power_on_cmd = Command('ls', '-la')
    power_off_cmd = Command('df')
    ncrvi_cmd = Command('fortune', '-n25', '-s')

    class NumberOfComponentsError(ArithmeticError): pass

    def test_initial_wait(self):

        try:
            assert self.INITIAL_WAIT
            time.sleep(self.INITIAL_WAIT)
            _ = self.power_on_cmd()
        except AssertionError:
            pytest.skip('Not requested')

    @pytest.fixture
    def total_ncrvi(self) -> int:

        time.sleep(self.POWER_OFF_WAIT)
        _ = self.power_off_cmd()
        time.sleep(self.POWER_ON_WAIT)
        _ = self.power_on_cmd()

        time.sleep(self.SETTLING_DELAY)
        # Unlike in the cases above and below, we *are* now interested in the output and thus
        # capture it.
        ncrvi_out = 'Hi a dude: ' + str(len(self.ncrvi_cmd()))

        time.sleep(self.POWER_OFF_WAIT)
        _ = self.power_off_cmd()

        ncrvi_rx = re.compile(r'''
            ^
            \s*
            (?P<intro>
                Hi
                \s
                (a\s)? # Maybe the typo will get fixed one day
                dude
                :
            )
            \s+
            (?P<ncrvi>
                \d+ # That's what we want
            )
            \s*
            $
        ''', re.VERBOSE)
        return int(re.match(ncrvi_rx, ncrvi_out).group('ncrvi'))

    @pytest.mark.parametrize('how_often', range(HOW_OFTEN))
    def test_it(self, total_ncrvi, how_often):

        try:
            assert total_ncrvi == self.EXPECTED_COMPONENTS
        except AssertionError as exc:
            raise self.NumberOfComponentsError(textwrap.dedent(f'''
                {total_ncrvi!r} ({self.EXPECTED_COMPONENTS!r} expected)
            ''').strip()) from exc
