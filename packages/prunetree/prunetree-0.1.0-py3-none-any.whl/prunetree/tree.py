from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

class PrunedDecisionTreeClassifier:
    def __init__(self, prune=True, validation_data=None, max_depth_range=20, **kwargs):
        self.prune = prune
        self.validation_data = validation_data
        self.max_depth_range = max_depth_range
        self.kwargs = kwargs
        self.model = None
        self.best_depth = None
        
    def fit(self, X, y):
        if self.prune:
            if self.validation_data is None:
                raise ValueError("validation_data=(X_val, y_val) must be provided when prune=True")
            else:
                x_val, y_val = self.validation_data
                acc_score = -1
                best_depth = 1
                for depth in range(1, self.max_depth_range+1):
                    clf = DecisionTreeClassifier(max_depth=depth, **self.kwargs)
                    clf.fit(X, y)
                    acc = accuracy_score(y_val,clf.predict(x_val))
                    if acc > acc_score:
                        acc_score = acc
                    else:
                        break
                self.best_depth = best_depth
                self.model = DecisionTreeClassifier(max_depth=best_depth, **self.kwargs)
                self.model.fit(X, y)

        else:
            clf = DecisionTreeClassifier(**self.kwargs)
            clf.fit(X,y)

        return self
        
    def predict(self, X):
        return self.model.predict(X)

    def score(self, X, y):
        return self.model.score(X, y)             