from observe import Observable


class Store(Observable):
    def __init__(self, reducer):
        self.state = {}
        self.reducer = reducer
        super().__init__()

    def dispatch(self, action):
        self.state = self.reducer(self.state, action)
        self.notify(self.state)
