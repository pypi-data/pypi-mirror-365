import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import matplotlib.pyplot as plt


class SmartTransformer:    
    @staticmethod
    def transform(X, y):
        X = X.values
        y = y.values

        if X.ndim == 1:
            X = X.reshape(-1, 1)
        return X, y

class Linear_Regression_OLS:
    def __init__(self):
        self.coef_ = None

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)

        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.dot(np.linalg.inv(np.dot(X_train.T, X_train)), np.dot(X_train.T, y_train))

    def predict(self, X_test):
        pre = Predict_Return_Equation(X_test=X_test, coef_=self.coef_)
        return pre.predict()

    def returnScore(self, X_test, y_test):
        pre = Predict_Return_Equation(X_test=X_test, y_test=y_test, coef_=self.coef_)
        return pre.returnScore()

    def getEquation(self):
        pre = Predict_Return_Equation(coef_=self.coef_)
        return pre.getEquation()

class Linear_Regression_Elastic_BGD:
    def __init__(self, epochs, learning_rate, alpha=0.0, l1_ratio=0.0):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.alpha = alpha  # total regularization strength
        self.l1_ratio = l1_ratio  # mix: 1 = L1, 0 = L2, 0.5 = both
        self.coef_ = None

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.zeros(X_train.shape[1])
        n = X_train.shape[0]

        for _ in range(self.epochs):
            error = y_train - np.dot(X_train, self.coef_)
            grad = (-2 / n) * np.dot(X_train.T, error)
            l1_penalty = self.alpha * self.l1_ratio * np.sign(self.coef_)
            l2_penalty = self.alpha * (1 - self.l1_ratio) * 2 * self.coef_
            slope = grad + l1_penalty + l2_penalty
            self.coef_ -= self.learning_rate * slope

    def predict(self, X_test):
        pre = Predict_Return_Equation(X_test=X_test, coef_=self.coef_)
        return pre.predict()

    def returnScore(self, X_test, y_test):
        pre = Predict_Return_Equation(X_test=X_test, y_test=y_test, coef_=self.coef_)
        return pre.returnScore()

    def getEquation(self):
        pre = Predict_Return_Equation(coef_=self.coef_)
        return pre.getEquation()

class Linear_regression_SGD_ElasticNet:
    def __init__(self, epochs, learning_rate, alpha, l1_ratio):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.alpha = alpha  # Regularization strength
        self.l1_ratio = l1_ratio  # alpha=1 → L1 only, alpha=0 → L2 only
        self.coef_ = None

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.zeros(X_train.shape[1])

        for _ in range(self.epochs):
            for _ in range(X_train.shape[0]):
                idx = np.random.randint(0, X_train.shape[0])
                y_pred = np.dot(X_train[idx], self.coef_)
                error = y_train[idx] - y_pred
                grad = (-2) * np.dot(X_train[idx].T, error)
                l1 = self.alpha * self.l1_ratio * np.sign(self.coef_)
                l2 = self.alpha * (1 - self.l1_ratio) * 2 * self.coef_
                total_grad = grad + l1 + l2
                self.coef_ -= self.learning_rate * total_grad

    def predict(self, X_test):
        pre = Predict_Return_Equation(X_test=X_test, coef_=self.coef_)
        return pre.predict()

    def returnScore(self, X_test, y_test):
        pre = Predict_Return_Equation(X_test=X_test, y_test=y_test, coef_=self.coef_)
        return pre.returnScore()

    def getEquation(self):
        pre = Predict_Return_Equation(coef_=self.coef_)
        return pre.getEquation()


class Linear_regression_MBGD_Elastic:
    def __init__(self, epochs, learning_rate, batch_size, alpha=1.0, l1_ratio=0.5):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.alpha = alpha            # Overall strength
        self.l1_ratio = l1_ratio      # Mix between L1 and L2
        self.coef_ = None

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)

        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.zeros(X_train.shape[1])
        n = X_train.shape[0]

        for _ in range(self.epochs):
            for _ in range(n // self.batch_size):
                batch_idx = np.random.randint(0, n, self.batch_size)
                X_batch = X_train[batch_idx]
                y_batch = y_train[batch_idx]

                y_pred = np.dot(X_batch, self.coef_)
                error = y_batch - y_pred

                slope = (-2 / len(X_batch)) * np.dot(X_batch.T, error)
                l1_penalty = self.alpha * self.l1_ratio * np.sign(self.coef_)
                l2_penalty = self.alpha * (1 - self.l1_ratio) * 2 * self.coef_
                slope += l1_penalty + l2_penalty

                self.coef_ -= self.learning_rate * slope

    def predict(self, X_test):
        pre = Predict_Return_Equation(X_test=X_test, coef_=self.coef_)
        return pre.predict()

    def returnScore(self, X_test, y_test):
        pre = Predict_Return_Equation(X_test=X_test, y_test=y_test, coef_=self.coef_)
        return pre.returnScore()

    def getEquation(self):
        pre = Predict_Return_Equation(coef_=self.coef_)
        return pre.getEquation()

    
class Predict_Return_Equation:
    def __init__(self, X_test=None, y_test=None, coef_=None):
        self.coef_ = coef_
        self.X_test = X_test
        self.y_test = y_test

    def predict(self):
        self.X_test = np.hstack((np.ones((self.X_test.shape[0], 1)), self.X_test))
        return np.dot(self.X_test, self.coef_)

    def returnScore(self):
        y_pred = self.predict()
        ss_res = np.sum((self.y_test - y_pred) ** 2)
        ss_tot = np.sum((self.y_test - np.mean(self.y_test)) ** 2)
        return 1 - (ss_res / ss_tot)

    def getEquation(self):
        intercept = round(self.coef_[0], 5)
        coefs = np.round(self.coef_[1:], 5)
        return f"y_hat = {intercept} + {coefs} * X"


class Logistic_Regression_Sigmoid_BGD_Elastic:
    def __init__(self, epochs, learning_rate, alpha=0.0, l1_ratio=0.0):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.coef_ = None

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)

        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.zeros(X_train.shape[1])
        n = X_train.shape[0]

        for _ in range(self.epochs):
            z = np.dot(X_train, self.coef_)
            y_pred = self.sigmoid(z)
            error = y_pred - y_train
            gradient = (1 / n) * np.dot(X_train.T, error)

            l1_penalty = self.alpha * self.l1_ratio * np.sign(self.coef_)
            l2_penalty = self.alpha * (1 - self.l1_ratio) * self.coef_
            reg = l1_penalty + l2_penalty
            reg[0] = 0  # no reg for bias

            self.coef_ -= self.learning_rate * (gradient + reg)

    def predict(self, X_test):
        if X_test.ndim == 1:
            X_test = X_test.reshape(-1, 1)
        X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
        return self.sigmoid(np.dot(X_test, self.coef_))

    def returnScore(self, X_test, y_test):
        y_pred = (self.predict(X_test) >= 0.5).astype(int)
        return np.mean(y_pred == y_test)

    def getEquation(self):
        terms = [f"{round(c, 4)}*x{i}" for i, c in enumerate(self.coef_[1:], 1)]
        return f"sigmoid({round(self.coef_[0], 4)} + " + " + ".join(terms) + ")"

    def plot_decision_boundary(self, X, y):
        if X.shape[1] != 1:
            print("Plotting supported for 1 feature only.")
            return

        plt.scatter(X, y, c=y, cmap='bwr')
        x_vals = np.linspace(min(X[:, 0]), max(X[:, 0]), 100)
        X_plot = np.hstack((np.ones((100, 1)), x_vals.reshape(-1, 1)))
        y_vals = self.sigmoid(np.dot(X_plot, self.coef_))
        plt.plot(x_vals, y_vals, color='black')
        plt.title("Decision Boundary")
        plt.xlabel("Feature")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.show()

class Logistic_Regression_SGD_ElasticNet:
    def __init__(self, epochs=100, learning_rate=0.01, alpha=0.1, l1_ratio=0.5):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.alpha = alpha  # Regularization strength
        self.l1_ratio = l1_ratio  # Mix between L1 and L2
        self.coef_ = None

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X_train, y_train):
        if X_train.ndim == 1:
            X_train = X_train.reshape(-1, 1)

        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        self.coef_ = np.zeros(X_train.shape[1])

        for _ in range(self.epochs):
            for _ in range(X_train.shape[0]):
                i = np.random.randint(0, X_train.shape[0])
                xi = X_train[i].reshape(1, -1)
                yi = y_train[i]
                y_pred = self.sigmoid(np.dot(xi, self.coef_))
                error = y_pred - yi

                # Elastic Net penalty terms
                l1 = self.l1_ratio * np.sign(self.coef_)
                l2 = (1 - self.l1_ratio) * self.coef_
                penalty = self.alpha * (l1 + l2)
                
                gradient = xi.T * error + penalty.reshape(-1, 1)
                self.coef_ -= self.learning_rate * gradient.flatten()

    def predict(self, X_test):
        if X_test.ndim == 1:
            X_test = X_test.reshape(-1, 1)
        X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
        y_pred = self.sigmoid(np.dot(X_test, self.coef_))
        return (y_pred >= 0.5).astype(int)

    def returnScore(self, X_test, y_test):
        y_pred = self.predict(X_test)
        return np.mean(y_pred == y_test)
    
    def getEquation(self):
        terms = [f"{round(c, 4)}*x{i}" for i, c in enumerate(self.coef_[1:], 1)]
        return f"sigmoid({round(self.coef_[0], 4)} + " + " + ".join(terms) + ")"

    def plot_decision_boundary(self, X, y):
        if X.shape[1] != 1:
            print("Plotting supported for 1 feature only.")
            return

        plt.scatter(X, y, c=y, cmap='bwr')
        x_vals = np.linspace(min(X[:, 0]), max(X[:, 0]), 100)
        X_plot = np.hstack((np.ones((100, 1)), x_vals.reshape(-1, 1)))
        y_vals = self.sigmoid(np.dot(X_plot, self.coef_))
        plt.plot(x_vals, y_vals, color='black')
        plt.title("Decision Boundary")
        plt.xlabel("Feature")
        plt.ylabel("Probability")
        plt.grid(True)
        plt.show()

class Logistic_Regression_MBGD_Elastic:
            def __init__(self, epochs, learning_rate, batch_size, penalty='elasticnet', l1_ratio=0.5, alpha=0.01):
                self.epochs = epochs
                self.learning_rate = learning_rate
                self.batch_size = batch_size
                self.penalty = penalty  # 'l1', 'l2', 'elasticnet'
                self.l1_ratio = l1_ratio
                self.alpha = alpha
                self.coef_ = None

            def sigmoid(self, z):
                return 1 / (1 + np.exp(-z))

            def fit(self, X_train, y_train):
                if X_train.ndim == 1:
                    X_train = X_train.reshape(-1, 1)

                X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
                self.coef_ = np.zeros(X_train.shape[1])
                n = X_train.shape[0]

                for _ in range(self.epochs):
                    for _ in range(n // self.batch_size):
                        batch_idx = np.random.randint(0, n, self.batch_size)
                        X_batch = X_train[batch_idx]
                        y_batch = y_train[batch_idx]

                        y_pred = self.sigmoid(np.dot(X_batch, self.coef_))
                        error = y_batch - y_pred
                        gradient = -(1 / len(X_batch)) * np.dot(X_batch.T, error)

                        if self.penalty == 'l1':
                            gradient += self.alpha * np.sign(self.coef_)
                        elif self.penalty == 'l2':
                            gradient += self.alpha * 2 * self.coef_
                        elif self.penalty == 'elasticnet':
                            l1_grad = self.l1_ratio * np.sign(self.coef_)
                            l2_grad = (1 - self.l1_ratio) * 2 * self.coef_
                            gradient += self.alpha * (l1_grad + l2_grad)

                        self.coef_ -= self.learning_rate * gradient

            def predict(self, X_test):
                if X_test.ndim == 1:
                    X_test = X_test.reshape(-1, 1)
                X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
                probs = self.sigmoid(np.dot(X_test, self.coef_))
                return (probs >= 0.5).astype(int)

            def returnScore(self, X_test, y_test):
                preds = self.predict(X_test)
                return np.mean(preds == y_test)

            def getEquation(self):
                return f"Sigmoid({self.coef_})"

            def plot_decision_boundary(self, X, y):
                if X.shape[1] != 1:
                    print("Plotting supported for 1 feature only.")
                    return

                plt.scatter(X, y, c=y, cmap='bwr')
                x_vals = np.linspace(min(X[:, 0]), max(X[:, 0]), 100)
                X_plot = np.hstack((np.ones((100, 1)), x_vals.reshape(-1, 1)))
                y_vals = self.sigmoid(np.dot(X_plot, self.coef_))
                plt.plot(x_vals, y_vals, color='black')
                plt.title("Decision Boundary")
                plt.xlabel("Feature")
                plt.ylabel("Probability")
                plt.grid(True)
                plt.show()


class Decision_Tree_Classifier_Simple:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.tree = None

    def gini(self, y):
        probs = np.bincount(y) / len(y)
        return 1 - np.sum(probs**2)

    def best_split(self, X, y):
        best_feature, best_thresh, best_gain = None, None, -1
        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            for thresh in thresholds:
                left = y[X[:, feature] <= thresh]
                right = y[X[:, feature] > thresh]
                if len(left) == 0 or len(right) == 0:
                    continue
                gain = self.gini_gain(y, left, right)
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_thresh = thresh
        return best_feature, best_thresh

    def gini_gain(self, parent, left, right):
        p = len(left) / len(parent)
        return self.gini(parent) - (p * self.gini(left) + (1 - p) * self.gini(right))

    def build_tree(self, X, y, depth):
        if depth >= self.max_depth or len(set(y)) == 1:
            return np.bincount(y).argmax()

        feature, thresh = self.best_split(X, y)
        if feature is None:
            return np.bincount(y).argmax()

        left_idx = X[:, feature] <= thresh
        right_idx = ~left_idx

        left = self.build_tree(X[left_idx], y[left_idx], depth + 1)
        right = self.build_tree(X[right_idx], y[right_idx], depth + 1)

        return (feature, thresh, left, right)

    def fit(self, X, y):
        if isinstance(X, pd.DataFrame):
            X = X.values
        self.tree = self.build_tree(X, y, 0)

    def predict_row(self, row, node):
        if not isinstance(node, tuple):
            return node
        feature, thresh, left, right = node
        if row[feature] <= thresh:
            return self.predict_row(row, left)
        else:
            return self.predict_row(row, right)


    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        return np.array([self.predict_row(row, self.tree) for row in X])

    def score(self, X, y):
        y_pred = self.predict(X)
        return np.mean(y_pred == y)
    

    def plot_decision_boundary(self, X, y, steps=100):

        if isinstance(X, pd.DataFrame):
            X = X.values
        x1_range = np.linspace(X[:, 0].min(), X[:, 0].max(), steps)
        x2_range = np.linspace(X[:, 1].min(), X[:, 1].max(), steps)
        xx1, xx2 = np.meshgrid(x1_range, x2_range)
        grid = np.c_[xx1.ravel(), xx2.ravel()]
        preds = self.predict(grid).reshape(xx1.shape)

        plt.figure(figsize=(8, 6))
        plt.contourf(xx1, xx2, preds, alpha=0.3, cmap='bwr')
        plt.scatter(X[:, 0], X[:, 1], c=y, cmap='bwr', edgecolor='k')
        plt.title('Decision Tree Decision Boundary')
        plt.xlabel('x1')
        plt.ylabel('x2')
        plt.grid(True)
        plt.show()




class Lazy_Work:
    def __init__(self, df):
        self.dataframe = df.copy()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.target_column = None

    def fit_data(self, random_state=42, ratio=0.8, training_features=None, target_features=None, drop_features=None):
        # Ensure target_features is a list
        if target_features is None:
            raise ValueError("target_features cannot be None")
        elif isinstance(target_features, str):
            target_features = [target_features]
        elif not isinstance(target_features, list):
            target_features = list(target_features)
        
        # Validate only one target feature
        if len(target_features) > 1:
            raise ValueError("Only one target feature is allowed")
        
        self.target_column = target_features[0]
        
        # Set default training_features (all columns except target)
        if training_features is None:
            training_features = self.dataframe.columns.drop(self.target_column).tolist()
        # Convert training_features to list if not None
        elif isinstance(training_features, str):
            training_features = [training_features]
        else:
            training_features = list(training_features)
        
        # Remove features specified in drop_features
        if drop_features is not None:
            if isinstance(drop_features, str):
                drop_features = [drop_features]
            else:
                drop_features = list(drop_features)
            training_features = [f for f in training_features if f not in drop_features]
        
        # Filter columns (ensure target is included)
        df_filtered = self.dataframe[training_features + [self.target_column]]
        
        # Train-test split
        train = df_filtered.sample(frac=ratio, random_state=random_state)
        test = df_filtered.drop(train.index)
        
        # Assign features and target
        self.X_train = train[training_features]
        self.y_train = train[self.target_column]
        self.X_test = test[training_features]
        self.y_test = test[self.target_column]
        
        # Apply transformations
        self.X_train, self.y_train = SmartTransformer.transform(self.X_train, self.y_train)
        self.X_test, self.y_test = SmartTransformer.transform(self.X_test, self.y_test)


    def StandardScale(self, features=None):
        def standardized(X):
            mean = X.mean(axis=0)
            std = X.std(axis=0)
            return (X - mean) / std

        if features is None:
            features = self.dataframe.columns.tolist()

        self.dataframe[features] = standardized(self.dataframe[features])


    def save_model(self, model_obj, filename="model.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(model_obj, f)

    def load_model(self, filename="model.pkl"):
        with open(filename, "rb") as f:
            return pickle.load(f)
    
    def do_ml(self, get_equation=False, model=None, method=None, epochs=100, learning_rate=0.01, alpha=0.0, l1_ratio=0.0, batch_size=10, viz=False, degree=2, max_depth=3):
        if model is None or method is None:
            raise ValueError("Parameter can't be None")

        # Regression models
        if model == 'lr':
            if method == 'ols':
                model = Linear_Regression_OLS()
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                print(model.returnScore(self.X_test, self.y_test))
            elif method == 'bgd':
                model = Linear_Regression_Elastic_BGD(epochs=epochs, learning_rate=learning_rate, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                print(model.returnScore(self.X_test, self.y_test))

            elif method == 'sgd':
                model = Linear_regression_SGD_ElasticNet(epochs=epochs, learning_rate=learning_rate, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                print(model.returnScore(self.X_test, self.y_test))

            elif method == 'mbgd':
                model = Linear_regression_MBGD_Elastic(epochs=epochs, learning_rate=learning_rate, batch_size=batch_size, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                print(model.returnScore(self.X_test, self.y_test))

        elif model == 'lgr':
            if method == 'bgd':
                model = Logistic_Regression_Sigmoid_BGD_Elastic(epochs=epochs, learning_rate=learning_rate, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                if viz:
                    model.plot_decision_boundary(self.X_train, self.y_train)
                print(model.returnScore(self.X_test, self.y_test))

            elif method == 'sgd':
                model = Logistic_Regression_SGD_ElasticNet(epochs=epochs, learning_rate=learning_rate, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                if viz:
                    model.plot_decision_boundary(self.X_train, self.y_train)
                print(model.returnScore(self.X_test, self.y_test))

            elif method == 'mbgd':
                model = Logistic_Regression_MBGD_Elastic(epochs=epochs, learning_rate=learning_rate, batch_size=batch_size, alpha=alpha, l1_ratio=l1_ratio)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                if viz:
                    model.plot_decision_boundary(self.X_train, self.y_train)
                print(model.returnScore(self.X_test, self.y_test))

        elif model == 'dt':
            if method == 'simple':
                model = Decision_Tree_Classifier_Simple(max_depth=max_depth)
                model.fit(self.X_train, self.y_train)
                if get_equation:
                    print(model.getEquation())
                if viz:
                    model.plot_decision_boundary(self.X_train, self.y_train)
                print(model.score(self.X_test, self.y_test))
        
import logging
logging.basicConfig(level=logging.INFO)

class Encoder:
    def __init__(self, df):
        self.df = df
        self.sparse = []

    # def get_encoding_recommendation(self, )

    def label_encoding(self, columns):
        from sklearn.preprocessing import LabelEncoder
        label_encoder = LabelEncoder()
        for col in columns:
            self.df[col] = label_encoder.fit_transform(self.df[col])
        return self.df

    def one_hot_encoding(self, columns, sparse=None):
        from sklearn.preprocessing import OneHotEncoder
        import pandas as pd

        if sparse is None:
            sparse = [False] * len(columns)

        for i in range(len(columns)):
            encoder = OneHotEncoder(sparse_output=sparse[i], handle_unknown='ignore')
            encoded = encoder.fit_transform(self.df[[columns[i]]])
            encoded_df = pd.DataFrame(
                encoded if not sparse[i] else encoded.toarray(),
                columns=encoder.get_feature_names_out([columns[i]])
            )

            self.df = self.df.drop(columns[i], axis=1).join(encoded_df)
        return self.df
        
    def ordinal_encoding(self, columns):
        from sklearn.preprocessing import OrdinalEncoder
        ordinal_encoder = OrdinalEncoder()
        for col in columns:
            self.df[col] = ordinal_encoder.fit_transform(self.df[[col]])
        return self.df
    
    def target_encoding(self, columns, target):
        from sklearn.preprocessing import TargetEncoder
        target_encoder = TargetEncoder()
        for col in columns:
            self.df[col] = target_encoder.fit_transform(self.df[[col]], self.df[target])
        return self.df
    
    def binary_encoding(self, columns, mapping=None):
        for col in columns:
            if mapping and col in mapping:
                self.df[col] = self.df[col].map(mapping[col])
            else:
                uniques = self.df[col].dropna().unique()
                if len(uniques) == 2:
                    self.df[col] = self.df[col].map({uniques[0]: 0, uniques[1]: 1})
                else:
                    raise ValueError(f"Column '{col}' is not binary.")
        return self.df


    def encode_datetime_feature(self, datetime_cols):
        import logging
        from feature_engine.datetime import DatetimeFeatures

        formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y',
                '%m-%Y', '%d/%y', '%m/%y', '%d %b %Y', '%b %Y']

        for col in datetime_cols:
            parsed = False
            for fmt in formats:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], format=fmt, errors='raise')
                    parsed = True
                    break
                except:
                    continue

            if not parsed:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except:
                    logging.warning(f"Failed to parse {col}")
                    continue




            transformer = DatetimeFeatures(
                variables=[col],
                features_to_extract=[
                    'year', 'month', 'quarter', 'semester', 'week',
                    'day_of_week', 'day_of_month', 'day_of_year', 'weekend',
                    'month_start', 'month_end', 'quarter_start', 'quarter_end',
                    'year_start', 'year_end', 'leap_year', 'days_in_month',
                    'hour', 'minute', 'second'
                ]
            )

            try:
                self.df = transformer.fit_transform(self.df)
            except Exception as e:
                logging.warning(f"Encoding failed for {col}: {e}")

        return self.df




class AutoFeatureEngineer:

    def __init__(self, df):
        self.df = df
        self.ordinal_patterns = {
            # Numeric ranks
            'numeric_ranks': r'^\d{1,2}(st|nd|rd|th)$|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth',
            
            # Organizational hierarchies
            'org_hierarchy': r'\b(intern|trainee|apprentice|junior|assistant|associate|'
                            r'senior|staff|lead|principal|manager|supervisor|director|'
                            r'vp|vice president|executive|chief|head|president|ceo|cto|cfo)\b',
            
            # Education levels
            'education': r'\b(high school|secondary|ged|diploma|certificate|associate|'
                        r'bachelor|undergrad|graduate|master|m\.?sc|mba|phd|doctorate|postdoc)\b',
            
            # Military ranks
            'military': r'\b(private|corporal|sergeant|lieutenant|captain|major|'
                    r'colonel|brigadier|general|admiral|commander|commodore)\b',
            
            # Skill levels
            'skill': r'\b(novice|beginner|learner|intermediate|proficient|advanced|'
                    r'expert|specialist|professional|master|guru)\b',
            
            # Priority levels
            'priority': r'\b(trivial|low|minor|medium|moderate|normal|high|major|'
                    r'urgent|critical|blocker|p0|p1|p2|p3|p4)\b',
            
            # Size scales
            'size': r'\b(xxs|xs|s|m|l|xl|xxl|xxxl|xxxxl|tiny|small|compact|medium|'
                r'regular|large|big|huge|giant)\b',
            
            # Agreement scales
            'agreement': r'\b(strongly disagree|disagree|somewhat disagree|neutral|'
                        r'no opinion|agree|somewhat agree|strongly agree)\b',
            
            # Frequency scales
            'frequency': r'\b(never|rarely|occasionally|sometimes|periodically|regularly|'
                        r'often|frequently|usually|always|constantly)\b',
            
            # Quality ratings
            'quality': r'\b(awful|poor|below average|fair|average|acceptable|satisfactory|'
                    r'good|very good|great|excellent|superb|outstanding|premium|premier)\b',
            
            # Grade levels
            'grades': r'\b([ABCDEF][+-]?|fail|pass|merit|distinction|honors|with honors)\b',
            
            # Time periods
            'time': r'\b(dawn|early morning|morning|midday|noon|afternoon|evening|'
                r'night|midnight|spring|summer|fall|autumn|winter)\b',
            
            # Risk levels
            'risk': r'\b(negligible|low|moderate|medium|elevated|high|serious|severe|critical|extreme)\b',
            
            # Maturity levels
            'maturity': r'\b(initial|developing|defined|managed|optimizing)\b',
            
            # Satisfaction levels
            'satisfaction': r'\b(very dissatisfied|dissatisfied|neutral|satisfied|very satisfied)\b'
        }

    def detect_feature_type(self, column, ordinal_threshold):
        
        if len(column.unique()) == 2:
            return "binary"
        elif self.has_ordinal_terms(column, ordinal_threshold):
            return "ordinal"        
        else:
            return 'nominal'
    





    def has_datetime(self, col):
        import datefinder
        sample = self.df[col].dropna().astype(str).sample(min(50, len(self.df)))
        for val in sample:
            if list(datefinder.find_dates(val)):
                return True
        return False





    
    def get_encoding_recommendation(self, datetime_columns=None, ordinal_threshold=0.5):
        cat_list = list(self.df.select_dtypes(include=['object']).columns)
        if datetime_columns is not None:
            for col in datetime_columns:
                if (col in cat_list):
                    cat_list.remove(col)
        encoding_recommendation = {}
        for col in cat_list:
            encoding_recommendation[col] = self.detect_feature_type(self.df[col], ordinal_threshold)
        return encoding_recommendation
    
    def has_ordinal_terms(self, column_series, threshold=0.5):
        import pandas as pd
        import re
        if pd.api.types.is_numeric_dtype(column_series):
            return False
        
        unique_vals = column_series.dropna().astype(str).unique()
        if len(unique_vals) < 3:  # Need at least 3 values for ordinal
            return False
            
        match_count = 0
        total_vals = len(unique_vals)
        
        for val in unique_vals:
            val_clean = re.sub(r'[^a-z0-9\s]', '', val.lower()).strip()
            
            # Check all ordinal patterns
            for _, pattern in self.ordinal_patterns.items():
                if re.search(pattern, val_clean, flags=re.IGNORECASE):
                    match_count += 1
                    break
        
        # Check if enough values match ordinal patterns
        return (match_count / total_vals) >= threshold
    
    def is_high_cardinality(self, series, threshold=0.5, unique_limit=100):
        unique_ratio = series.nunique() / len(series)
        return unique_ratio > threshold or series.nunique() > unique_limit
    
    def get_datetime_columns(self):
        datetime_columns = []
        for col in self.df.columns:
            if (not pd.api.types.is_numeric_dtype(self.df[col])):
                if self.has_datetime(col):
                    datetime_columns.append(col)
        return datetime_columns

    def encode_features(self, logging_enabled=False, datetime_columns=[], mapping=None, sparse=None, cardinality_threshold = 0.5, cardinality_unique_limit = 100, ordinal_threshold = 0.5, target=None, encoding_recommendation_by_user={}):
        encoder = Encoder(self.df)
        

        encoding_recommendation = self.get_encoding_recommendation(datetime_columns, ordinal_threshold)
        if (len(datetime_columns) > 0):
            self.df = encoder.encode_datetime_feature(datetime_columns)
                
        for col, encoding_type in encoding_recommendation.items():
            if (col in encoding_recommendation_by_user.keys()):
                encoding_type = encoding_recommendation_by_user[col]
                if (encoding_type == 'binary'):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as binary")
                    self.df = encoder.binary_encoding([col], mapping)
                elif (encoding_type == 'ordinal'):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as ordinal, as it has ordinal terms")
                    self.df = encoder.ordinal_encoding([col])
                elif (encoding_type == 'nominal'):
                    if (self.is_high_cardinality(self.df[col], cardinality_threshold, cardinality_unique_limit)):
                        if logging_enabled:
                            logging.info(f"Encoding {col} as label, reason high cardinality")
                        self.df = encoder.label_encoding([col])
                    else:
                        if logging_enabled:
                            logging.info(f"Encoding {col} as one-hot, reason low cardinality")
                        self.df = encoder.one_hot_encoding([col], sparse)
                elif (encoding_type == 'label'):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as label")
                    self.df = encoder.label_encoding([col])
                elif (encoding_type == 'one-hot'):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as one-hot")
                    self.df = encoder.one_hot_encoding([col], sparse)
                elif (encoding_type == 'target'):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as target")
                    self.df = encoder.target_encoding([col], target)
                else:
                    raise ValueError(f"Invalid encoding type: {encoding_type}")
            elif (encoding_type == 'binary'):
                if logging_enabled:
                    logging.info(f"Encoding {col} as binary")
                self.df = encoder.binary_encoding([col], mapping)
           
            elif (encoding_type == 'ordinal'):
                if logging_enabled:
                    logging.info(f"Encoding {col} as ordinal, as it has ordinal terms")
                self.df = encoder.ordinal_encoding([col])
            else:
                if (self.is_high_cardinality(self.df[col], cardinality_threshold, cardinality_unique_limit)):
                    if logging_enabled:
                        logging.info(f"Encoding {col} as label, reason high cardinality")
                    self.df = encoder.label_encoding([col])
                else:
                    if logging_enabled:
                        logging.info(f"Encoding {col} as one-hot, reason low cardinality")
                    self.df = encoder.one_hot_encoding([col], sparse)
        return self.df
    
