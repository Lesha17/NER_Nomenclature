from nomenclature_parser.fuzzy_logic import predict


class WordsTuple:
    def __init__(self):
        self.words = []
        self.pcs = []
        self.predicts = []

    def avrg_pcs(self):
        t_pcs = [0] * self.pcs[0].shape[0]
        for pc in self.pcs:
            t_pcs = t_pcs + pc
        t_pcs = t_pcs / len(self.pcs)
        return t_pcs

    def avrg_predict(self):
        t_predict = [0] * self.predicts[0].shape[0]
        for predict in self.predicts:
            t_predict = t_predict + predict
        t_predict = t_predict / len(self.predicts)
        return t_predict

    def total_predict(self, cntr):
        return predict(self.avrg_pcs(), cntr)
