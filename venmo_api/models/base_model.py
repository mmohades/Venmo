class BaseModel(object):
    def __str__(self):
        return f"{type(self).__name__}:" \
               f" ({', '.join('%s=%s' % item for item in vars(self).items() if not item[0].startswith('_'))})"
