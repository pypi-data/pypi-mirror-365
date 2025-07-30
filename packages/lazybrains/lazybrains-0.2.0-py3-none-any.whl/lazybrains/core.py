import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import matplotlib.pyplot as plt
from rich import print
from rich.panel import Panel
from rich.table import Table
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, StackingRegressor, StackingClassifier
from sklearn.linear_model import LinearRegression
import time

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
    

class Regression_Fitting:
    def __init__(self, df, target, alpha=0.5, l1_ratio=0.5):
        self.df = df
        self.target = target
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.elastic_net_model = None
        self.random_forest_regressor_model = None


    def fit_data(self, ratio=0.8):
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.df.drop(self.target, axis=1), self.df[self.target], test_size=ratio, random_state=42)

    def get_data(self):
        return self.X_train, self.X_test, self.y_train, self.y_test

    def elastic_net(self):


        from skopt import BayesSearchCV
        from skopt.space import Real

        param_dist = {
            'alpha': Real(0.01, 100, prior='log-uniform'),
            'l1_ratio': Real(0.1, 0.9)
        }

        model = ElasticNet()
        random_search = BayesSearchCV(
            model, search_spaces=param_dist,
            n_iter=10, scoring='r2', cv=5, random_state=42
        )

        random_search.fit(self.X_train, self.y_train)
        self.elastic_net_model = random_search.best_estimator_

        table = Table(title="[bold cyan]ElasticNet Tuning Summary[/bold cyan]")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="bold white")
        table.add_row("Best Parameters", str(random_search.best_params_))
        table.add_row("Best Score (R² CV)", f"{random_search.best_score_:.4f}")
        table.add_row("Best Index", str(random_search.best_index_))

        print(Panel.fit(table, title="[bold green]Model Optimization Results[/bold green]"))

        return self.elastic_net_model

    def random_forest_regressor(self, n_estimators_list=None, max_depth_list=None):
        from skopt import BayesSearchCV
        from skopt.space import Integer, Categorical
        from sklearn.ensemble import RandomForestRegressor


        if n_estimators_list is None:
            n_estimators_list = Integer(100, 500)
        else:
            n_estimators_list = Integer(*n_estimators_list)
        if max_depth_list is None:
            max_depth_list = Categorical([None, 10, 20, 30, 40, 50])
        else:
            max_depth_list = Categorical(max_depth_list)

        param_dist = {
            'n_estimators': n_estimators_list,
            'max_depth': max_depth_list,
            'min_samples_split': Integer(2, 10),
            'min_samples_leaf': Integer(1, 4),
            'max_features': Categorical(['sqrt', 'log2', None])
        }

        model = RandomForestRegressor()
        random_search = BayesSearchCV(
            model, search_spaces=param_dist,
            n_iter=10, scoring='r2', cv=5, random_state=42
        )

        random_search.fit(self.X_train, self.y_train)
        self.random_forest_regressor_model = random_search.best_estimator_

        table = Table(title="[bold cyan]Random Forest Regressor Tuning Summary[/bold cyan]")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="bold white")
        table.add_row("Best Parameters", str(random_search.best_params_))
        table.add_row("Best Score (R² CV)", f"{random_search.best_score_:.4f}")
        table.add_row("Best Index", str(random_search.best_index_))

        print(Panel.fit(table, title="[bold green]Model Optimization Results[/bold green]"))

        return self.random_forest_regressor_model


    def stacking_regressor(self, n_estimators_list=None, max_depth_list=None):
        from sklearn.ensemble import StackingRegressor
        from sklearn.linear_model import LinearRegression
        print("[INFO] Training Elastic Net Regressor...")
        self.elastic_net_model = self.elastic_net()

        print("[INFO] Training Random Forest Regressor...")
        self.random_forest_regressor_model = self.random_forest_regressor(n_estimators_list, max_depth_list)

        print("[INFO] Fitting Stacking Regressor...")
        stack_model = StackingRegressor(
            estimators=[
                ('elastic', self.elastic_net_model),
                ('rf', self.random_forest_regressor_model)
            ],
            final_estimator=LinearRegression()
        )

        stack_model.fit(self.X_train, self.y_train)
        print("[SUCCESS] Stacking Regressor fitted successfully ✅")
        return stack_model


    def evaluate_model(self, n_estimators_list=None, max_depth_list=None):
        from sklearn.metrics import mean_squared_error, r2_score

        start_time = time.time()
        print("[TIMER] Training started...")

        y_pred = self.stacking_regressor(n_estimators_list, max_depth_list).predict(self.X_test)

        mse = mean_squared_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)

        end_time = time.time()
        duration = end_time - start_time

        print(f"Mean Squared Error: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")
        print(f"[TIMER] Training completed in {duration:.2f} seconds ⏱")






class Classification_Fitting:
    def __init__(self, df, target, alpha=0.5, l1_ratio=0.5):
        self.df = df
        self.target = target
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.logistic_regression_model = None
        self.random_forest_classifier_model = None


    def fit_data(self, ratio=0.8):
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.df.drop(self.target, axis=1), self.df[self.target], test_size=ratio, random_state=42)

    def logistic_regression(self, C=None, penalty=None, solver=None):
        from sklearn.linear_model import LogisticRegression

        from skopt.space import Real, Categorical

        if C is None:
            C = Real(1e-4, 100.0, prior='log-uniform')
        elif isinstance(C, list) and len(C) == 2:
            C = Real(*C, prior='log-uniform')  # if user gives a range
        else:
            C = Categorical(C if isinstance(C, list) else [C])

        if penalty is None:
            penalty = Categorical(['l1', 'l2'])
        else:
            penalty = Categorical(penalty if isinstance(penalty, list) else [penalty])

        if solver is None:
            solver = Categorical(['liblinear', 'saga'])
        else:
            solver = Categorical(solver if isinstance(solver, list) else [solver])


        param_dist = {
            'C': C,
            'penalty': penalty,
            'solver': solver
        }

        model = LogisticRegression(random_state=42, max_iter=1000)

        search = BayesSearchCV(
            model, param_dist,
            n_iter=10, cv=5, scoring='accuracy', random_state=42
        )

        search.fit(self.X_train, self.y_train)
        self.logistic_regression_model = search.best_estimator_

        table = Table(title="[bold cyan]Logistic Regression Tuning Summary[/bold cyan]")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="bold white")
        table.add_row("Best Parameters", str(search.best_params_))
        table.add_row("Best Score (Accuracy CV)", f"{search.best_score_:.4f}")
        table.add_row("Best Index", str(search.best_index_))

        print(Panel.fit(table, title="[bold green]Model Optimization Results[/bold green]"))
        return self.logistic_regression_model


    def random_forest_classifier(self, n_estimators_list=None, max_depth_list=None):
        from sklearn.ensemble import RandomForestClassifier

        if n_estimators_list is None:
            n_estimators_list = Integer(100, 500)
        else:
            n_estimators_list = Integer(*n_estimators_list)

        if max_depth_list is None:
            max_depth_list = Categorical([None, 10, 20, 30, 40, 50])
        else:
            max_depth_list = Categorical(max_depth_list)

        param_dist = {
            'n_estimators': n_estimators_list,
            'max_depth': max_depth_list,
            'min_samples_split': Integer(2, 10),
            'min_samples_leaf': Integer(1, 4),
            'max_features': Categorical(['sqrt', 'log2', None])
        }

        model = RandomForestClassifier()
        random_search = BayesSearchCV(
            model, search_spaces=param_dist,
            n_iter=10, scoring='accuracy', cv=5, random_state=42
        )

        random_search.fit(self.X_train, self.y_train)
        self.random_forest_classifier_model = random_search.best_estimator_

        table = Table(title="[bold cyan]Random Forest Classifier Tuning Summary[/bold cyan]")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="bold white")
        table.add_row("Best Parameters", str(random_search.best_params_))
        table.add_row("Best Score (Accuracy CV)", f"{random_search.best_score_:.4f}")
        table.add_row("Best Index", str(random_search.best_index_))

        print(Panel.fit(table, title="[bold green]Model Optimization Results[/bold green]"))

        return self.random_forest_classifier_model

    def stacking_classifier(self, n_estimators_list=None, max_depth_list=None):
        from sklearn.ensemble import StackingClassifier
        from sklearn.linear_model import LogisticRegression
        print("[INFO] Training Logistic Regression...")
        self.logistic_regression_model = self.logistic_regression()

        print("[INFO] Training Random Forest Classifier...")
        self.random_forest_classifier_model = self.random_forest_classifier(n_estimators_list, max_depth_list)

        print("[INFO] Fitting Stacking Classifier...")
        stack_model = StackingClassifier(
            estimators=[
                ('logreg', self.logistic_regression_model),
                ('rf', self.random_forest_classifier_model)
            ],
            final_estimator=LogisticRegression()
        )

        stack_model.fit(self.X_train, self.y_train)
        print("[SUCCESS] Stacking Classifier fitted successfully ✅")
        return stack_model

    def evaluate_model(self, n_estimators_list=None, max_depth_list=None):
        from sklearn.metrics import accuracy_score

        start_time = time.time()
        print(f"[TIMER] Training started...")

        y_pred = self.stacking_classifier(n_estimators_list, max_depth_list).predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)

        end_time = time.time()
        duration = end_time - start_time

        print(f"[INFO] Accuracy: {accuracy:.4f}")
        print(f"[TIMER] Training completed in {duration:.2f} seconds ⏱")
        return accuracy
