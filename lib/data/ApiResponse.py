class ApiResponse(object):
    def __init__(self, message, data, error):
        self.message = message
        self.data = data
        self.error = error

    def __str__(self):
        return''

    def __repr__(self):
        return ''

