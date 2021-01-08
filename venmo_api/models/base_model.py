class BaseModel(object):
    def __init__(self):
        self._json = None

    def __str__(self):
        return f"{type(self).__name__}:" \
               f" ({', '.join('%s=%s' % item for item in vars(self).items() if not item[0].startswith('_'))})"

    def to_json(self, original=True):
        if self._json and original:
            return self._json

        return dict(filter(lambda x: not x[0].startswith('_'), vars(self).items()))
