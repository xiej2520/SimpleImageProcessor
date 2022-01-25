
def clamp(minvalue, value, maxvalue):
    return max(minvalue, min(value, maxvalue))


class BoundedDouble():

    def __init__(self, value, min, max, step=0.01):
        self._value = value
        self._min = min
        self._max = max
        self._step = step

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = clamp(value, self._min, self._max)

    def _get_min(self):
        return self._min

    def _set_min(self, min):
        self._min = min

    def _get_max(self):
        return self._max

    def _set_max(self, max):
        self._max = max

    def _get_step(self):
        return self._step

    def _set_step(self, step):
        self._step = step

    value = property(_get_value, _set_value)
    min = property(_get_min, _set_min)
    max = property(_get_max, _set_max)
    step = property(_get_step, _set_step)


class BoundedInteger(BoundedDouble):

    def __init__(self, value, min, max, step=1):
        super().__init__(int(value), int(min), int(max), step)

    def _set_value(self, value):
        super()._set_value(int(value))

    def _set_min(self, min):
        super()._set_min(int(min))

    def _set_max(self, max):
        super()._set_max(int(max))

    def _set_step(self, step):
        super()._set_step(int(step))


class RadioSelect():

    def __init__(self, values, default=None):
        if default != None:
            self._value = default
        else:
            self._value = values[0]
        self.settings = dict.fromkeys(values, False)
        self.settings[self._value] = True

    def _set_value(self, value):
        self.settings[self._value] = False
        self.settings[value] = True
        self._value = value

    def _get_value(self):
        return self._value

    value = property(_get_value, _set_value)