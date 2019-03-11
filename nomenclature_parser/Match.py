class Match:
    def __init__(self, w1, w2, key, delta):
        self.w1 = w1
        self.w2 = w2
        self.key = key
        self.delta = delta

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return 'Match{ key: ' + str(self.key) + ', words: <' + str(self.w1.word) + ', ' + str(
            self.w2.word) + '>, delta: ' + str(self.delta) + '}'
