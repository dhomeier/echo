from . import CallbackProperty, HasCallbackProperties


class CallbackDict(dict):
    """
    A dictionary that calls a callback function when it is modified.

    The first argument should be the callback function (which takes no
    arguments), and subsequent arguments are passed to `dict`.
    """

    def __init__(self, callback, *args, **kwargs):
        super(CallbackDict, self).__init__(*args, **kwargs)
        self.callback = callback

    def clear(self):
        for value in self.values():
            if isinstance(value, HasCallbackProperties):
                value.remove_global_callback(self.callback)
        super().clear()
        self.callback()

    def popitem(self):
        result = super().popitem()
        if isinstance(result, HasCallbackProperties):
            result.remove_global_callback(self.callback)
        self.callback()
        return result

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if len(args) == 1:
            if hasattr(args[0], 'keys'):
                values = list(args[0].values())
            else:
                values = list(value for _, value in args[0])
        if len(kwargs) > 0:
            values.extend(list(kwargs.values()))
        for value in values:
            if isinstance(value, HasCallbackProperties):
                value.add_global_callback(self.callback)
        self.callback()

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        if isinstance(result, HasCallbackProperties):
            result.remove_global_callback(self.callback)
        self.callback()
        return result

    def __setitem__(self, key, value):
        if key in self:
            if isinstance(self[key], HasCallbackProperties):
                self[key].remove_global_callback(self.callback)
        super().__setitem__(key, value)
        if isinstance(value, HasCallbackProperties):
            value.add_global_callback(self.callback)
        self.callback()

    def __repr__(self):
        return f"<CallbackDict with {len(self)} elements>"


class DictCallbackProperty(CallbackProperty):
    """
    A dictionary property that calls callbacks when its contents are modified
    """
    def _default_getter(self, instance, owner=None):
        if instance not in self._values:
            self._default_setter(instance, {})
        return super()._default_getter(instance, owner)

    def _default_setter(self, instance, value):

        if not isinstance(value, dict):
            raise TypeError("Callback property should be a dictionary.")

        def callback(*args, **kwargs):
            self.notify(instance, wrapped_dict, wrapped_dict)

        wrapped_dict = CallbackDict(callback, value)

        super()._default_setter(instance, wrapped_dict)