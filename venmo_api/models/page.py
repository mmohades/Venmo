class Page(list):

    def __init__(self):
        super().__init__()
        self.method = None
        self.kwargs = {}
        self.current_offset = -1

    def set_method(self, method, kwargs, current_offset=-1):
        """
        set the method and kwargs for paging. current_offset is provided for routes that require offset.
        :param method:
        :param kwargs:
        :param current_offset:
        :return:
        """
        self.method = method
        self.kwargs = kwargs
        self.current_offset = current_offset
        return self

    def get_next_page(self):
        """
        Get the next page of data. Returns empty Page if none exists
        :return:
        """
        if not self.kwargs or not self.method or len(self) == 0:
            return self.__init__()

        # use offset or before_id for paging, depending on the route
        if self.current_offset > -1:
            self.kwargs['offset'] = self.current_offset + len(self)
        else:
            self.kwargs['before_id'] = self[-1].id

        return self.method(**self.kwargs)
