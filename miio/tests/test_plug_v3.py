from unittest import TestCase
from miio import PlugV3
from .dummies import DummyDevice
import pytest


class DummyPlugV3(DummyDevice, PlugV3):
    def __init__(self, *args, **kwargs):
        self.state = {
            'on': True,
            'usb_on': True,
            'temperature': 32,
            'wifi_led': 'off'
        }
        self.return_values = {
            'get_prop': self._get_state,
            'get_power': self._get_load_power,
            'set_power': lambda x: self._set_state_basic("on", x == ["on"]),
            'set_usb_on': lambda x: self._set_state_basic("usb_on", True),
            'set_usb_off': lambda x: self._set_state_basic("usb_on", False),
            'set_wifi_led': lambda x: self._set_state("wifi_led", x),
        }
        self.start_state = self.state.copy()

    def _set_state_basic(self, var, value):
        """Set a state of a variable"""
        self.state[var] = value

    def _get_load_power(self, props=None):
        """Return load power"""
        return [300]


@pytest.fixture(scope="class")
def plugv3(request):
    request.cls.device = DummyPlugV3()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("plugv3")
class TestPlugV3(TestCase):
    def is_on(self):
        return self.device.status().is_on

    def state(self):
        return self.device.status()

    def test_on(self):
        self.device.off()  # ensure off
        assert self.is_on() is False

        self.device.on()
        assert self.is_on() is True

    def test_off(self):
        self.device.on()  # ensure on
        assert self.is_on() is True

        self.device.off()
        assert self.is_on() is False

    def test_status(self):
        self.device._reset_state()

        assert self.is_on() is True
        assert self.state().usb_power is True
        assert self.state().temperature == self.device.start_state[
            "temperature"]
        assert self.state().load_power == self.device._get_load_power().pop(0)

    def test_usb_on(self):
        self.device.usb_off()  # ensure off
        assert self.device.status().usb_power is False

        self.device.usb_on()
        assert self.device.status().usb_power is True

    def test_usb_off(self):
        self.device.usb_on()  # ensure on
        assert self.device.status().usb_power is True

        self.device.usb_off()
        assert self.device.status().usb_power is False

    def test_set_wifi_led(self):
        def wifi_led():
            return self.device.status().wifi_led

        self.device.set_wifi_led(True)
        assert wifi_led() is True

        self.device.set_wifi_led(False)
        assert wifi_led() is False
