import numpy as np

class EnsemblePredictor:
    def __init__(self, models, weights=None, meta_model=None):
        """
        Initializes the EnsemblePredictor.
        :param models: List of models to combine predictions.
        :param weights: Optional list of weights for weighted averaging.
        :param meta_model: Optional meta-model for stacking predictions.
        """
        self.models = models
        self.weights = weights if weights is not None else [1] * len(models)
        self.meta_model = meta_model

    def weighted_average(self, X):
        """
        Computes the weighted average of model predictions.
        :param X: Input features.
        :return: Weighted average of predictions.
        """
        predictions = np.array([model.predict(X) for model in self.models])
        weighted_preds = np.average(predictions, axis=0, weights=self.weights)
        return weighted_preds

    def fit_meta_model(self, X_meta, y_meta):
        """
        Fits the meta-model on the predictions of base models.
        :param X_meta: Input features for meta-model.
        :param y_meta: Target values for meta-model.
        """
        meta_predictions = np.array([model.predict(X_meta) for model in self.models]).T
        self.meta_model.fit(meta_predictions, y_meta)

    def predict(self, X):
        """
        Makes predictions using the weighted average and meta-model (if provided).
        :param X: Input features.
        :return: Final predictions from the ensemble.
        """
        if self.meta_model:
            meta_preds = self.meta_model.predict(np.array([model.predict(X) for model in self.models]).T)
            return meta_preds
        else:
            return self.weighted_average(X)