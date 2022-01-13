class DoesNotExist(Exception):
    """Exception raised when trying to access non-existing objects
    """

    def __init__(self, obj, message="Object does not exist"):
        self.obj = obj
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.obj} -> {self.message}'

class UnsupportedActionForComment(Exception):
    """Exception raised when trying to access non-existing objects
    """

    def __init__(self, obj, message="Attempted to perform a non-existent action"):
        self.obj = obj
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.obj} -> {self.message}'