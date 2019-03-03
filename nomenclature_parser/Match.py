class Match:
    def __init__(self, t1, t2, delta):
        self.t1 = t1
        self.t2 = t2
        self.delta = delta
        self.key = '#'

    def to_string(self):
        return 'Match{ key: ' + str(self.key) + ', words: <' + str(self.t1.words) + ', ' + str(
            self.t2.words) + '>, delta: ' + str(self.delta) + '}'
