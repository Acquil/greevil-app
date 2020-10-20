class ReturnDocument(object):

    def __init__(self, data, status):
        """
        Document structure returned by Greevil API
        :param data:   object
        :param status: str
        """
        self.data = data
        self.status = status

    def asdict(self):
        return {"data": self.data, "status": self.status}
