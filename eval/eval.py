class Eval:
    def __init__(self, annotations, extracted, original_text, clean_ann_fn=None, clean_ext_fn=None):
        self.annotations = annotations
        self.extracted = extracted
        self.original_text = original_text

        self.clean_ann_fn = clean_ann_fn
        self.clean_ext_fn = clean_ext_fn

        self.false_positives = None
        self.false_negatives = None
        self.true_positives = None

    def evaluate(self):
        """
        Main evaluation function that computes evaluation metrics.
        """
        raise NotImplementedError  # This will be implemented in subclasses

    def get_precision(self):
        return self.true_positives / (self.true_positives + self.false_positives)

    def get_recall(self):
        return self.true_positives / (self.true_positives + self.false_negatives)

    def get_f1_score(self):
        precision = self.get_precision() if self.get_precision() != 0 else 1e10 - 10
        recall = self.get_recall() if self.get_recall() != 0 else 1e10 - 10
        return 2 * (precision * recall) / (precision + recall)

    def get_metrics(self):
        """
        Calculate and return a dictionary of evaluation metrics.
        """
        metrics = {
            'precision': self.get_precision(),
            'recall': self.get_recall(),
            'f1_score': self.get_f1_score(),
        }
        return metrics


class ExactMatchEval(Eval):
    def __init__(self, annotations, extracted, original_text, clean_ann_fn=None, clean_ext_fn=None, map_ann=None):
        super().__init__(annotations, extracted, original_text, clean_ann_fn, clean_ext_fn)
        self.map_ann = map_ann

    def evaluate(self):
        """
        Main evaluation function that computes evaluation metrics.
        """
        keys = set(self.annotations[0].keys())
        self.false_positives = {key: 0 for key in keys}
        self.false_negatives = {key: 0 for key in keys}
        self.true_positives = {key: 0 for key in keys}

        for key in keys:
            key_ann = [self.map_ann(key, ann[key]) if self.map_ann else ann[key] for ann in self.annotations]
            key_ext = [self.map_ann(key, ext[key]) if self.map_ann else ext[key] for ext in self.extracted]
            for ann in key_ann:
                if ann in key_ext:
                    self.true_positives[key] += 1
                else:
                    self.false_negatives[key] += 1

            for ext in key_ext:
                if ext not in key_ann:
                    self.false_positives[key] += 1


class FullRowExactMatch(Eval):
    def __init__(self, annotations, extracted, original_text, clean_ann_fn=None, clean_ext_fn=None, join_ann=None):
        super().__init__(annotations, extracted, original_text, clean_ann_fn, clean_ext_fn)
        self.join_ann = join_ann

    def join(self, array):
        if self.join_ann:
            return self.join_ann(array)
        else:
            return ' '.join([v for k, v in ann.items()])

    def evaluate(self):
        """
        Main evaluation function that computes evaluation metrics.
        """
        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0
        anns = [self.join(ann) for ann in self.annotations]
        exts = [self.join(ext) for ext in self.extracted]

        for ann in anns:
            if ann in exts:
                self.true_positives += 1
            else:
                self.false_negatives += 1

        for ext in exts:
            if ext not in anns:
                self.false_positives += 1


class EmbeddingCosineDistance(Eval):
    def __init__(self, annotations, extracted, original_text, join_ann, embed_fn, clean_ann_fn=None, clean_ext_fn=None,
                 k_sim=0.9):
        super().__init__(annotations, extracted, original_text, clean_ann_fn, clean_ext_fn)
        self.join_ann = join_ann
        self.embed_fn = embed_fn
        self.k_sim = k_sim

    def join(self, array):
        if self.join_ann:
            return self.join_ann(array)
        else:
            return ' '.join([v for k, v in ann.items()])

    def evaluate(self):
        """
        Main evaluation function that computes evaluation metrics.
        """
        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0

        anns = [self.embed_fn(self.join(ann)) for ann in self.annotations]
        exts = [self.embed_fn(self.join(ext)) for ext in self.extracted]

        distances = []
        for i, ann in enumerate(anns):
            for j, ext in enumerate(exts):
                distances.append((i, j, 1 - cosine(ann, ext)))

        distances.sort(key=lambda x: x[2], reverse=True)
        matched_anns = []
        matched_anns_idx = []
        for dist in distances:
            if dist[0] not in matched_anns_idx:
                matched_anns.append(dist)
                matched_anns_idx.append(dist[0])

        matched_exts = []
        matched_exts_idx = []
        for dist in distances:
            if dist[1] not in matched_exts_idx:
                matched_exts.append(dist)
                matched_exts_idx.append(dist[1])

        matched_anns = [(ma[0], ma[1], ma[2] > self.k_sim) for ma in matched_anns]
        matched_exts = [(me[0], me[1], me[2] > self.k_sim) for me in matched_exts]

        self.true_positives = len([ma for ma in matched_anns if ma[2]])
        self.false_positives = len([me for me in matched_exts if not me[2]])
        self.false_negatives = len([ma for ma in matched_anns if not ma[2]])


class LLMEvaluation(Eval):
    def __init__(self, annotations, extracted, original_text, clean_ann_fn=None, clean_ext_fn=None):
        super().__init__(annotations, extracted, original_text, clean_ann_fn, clean_ext_fn)

    def evaluate(self):
        """
        Main evaluation function that computes evaluation metrics.
        """
        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0

        for ann in self.annotations:
            if ann in self.extracted:
                self.true_positives += 1
            else:
                self.false_negatives += 1

        for ext in self.extracted:
            if ext not in self.annotations:
                self.false_positives += 1

