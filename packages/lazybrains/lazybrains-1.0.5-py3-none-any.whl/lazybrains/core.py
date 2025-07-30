import argparse
import time
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap
from pathlib import Path

# --- Scikit-learn Imports ---
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, roc_curve, auc, RocCurveDisplay,
                             ConfusionMatrixDisplay, r2_score, mean_squared_error)
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest

# --- Model Imports ---
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor, StackingClassifier, StackingRegressor,
                              GradientBoostingClassifier, GradientBoostingRegressor, AdaBoostClassifier, AdaBoostRegressor)
from xgboost import XGBClassifier, XGBRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB

# --- Parallel Processing ---
from joblib import Parallel, delayed

# --- Rich CLI Library ---
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax

# Ignore common warnings for a cleaner output
warnings.filterwarnings('ignore')

# Initialize Rich Console
console = Console()

# --- Core Functions ---

def detect_problem_type(target_series: pd.Series) -> str:
    """
    Automatically detects if the problem is classification or regression.
    """
    if target_series.dtype in ['object', 'category', 'bool']:
        return 'classification'

    unique_values = target_series.nunique()
    if unique_values < 2:
         raise ValueError("Target column has less than 2 unique values. Cannot perform modeling.")
    # Heuristic: If low cardinality integer feature, treat as classification
    if pd.api.types.is_integer_dtype(target_series) and unique_values < 50 and (unique_values / len(target_series)) < 0.05:
        return 'classification'

    return 'regression'

def get_models(problem_type: str) -> dict:
    """Returns a dictionary of diverse models suitable for the problem type."""
    n_jobs = -1  # Use all available cores for models that support it
    random_state = 42

    if problem_type == 'classification':
        # Base estimators for Stacking
        estimators_clf = [
            ('rf', RandomForestClassifier(random_state=random_state, n_jobs=n_jobs)),
            ('gb', GradientBoostingClassifier(random_state=random_state))
        ]
        models = {
            "Logistic Regression": LogisticRegression(random_state=random_state, n_jobs=n_jobs, max_iter=1000),
            "Decision Tree": DecisionTreeClassifier(random_state=random_state),
            "Random Forest": RandomForestClassifier(random_state=random_state, n_jobs=n_jobs),
            "Gradient Boosting": GradientBoostingClassifier(random_state=random_state),
            "AdaBoost": AdaBoostClassifier(random_state=random_state),
            "Support Vector Machine": SVC(random_state=random_state, probability=True),
            "K-Nearest Neighbors": KNeighborsClassifier(n_jobs=n_jobs),
            "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=random_state, n_jobs=n_jobs),
            "Stacking": StackingClassifier(estimators=estimators_clf, final_estimator=LogisticRegression(), n_jobs=n_jobs)
        }
    else:  # regression
        # Base estimators for Stacking
        estimators_reg = [
            ('rf', RandomForestRegressor(random_state=random_state, n_jobs=n_jobs)),
            ('ridge', Ridge(random_state=random_state))
        ]
        models = {
            "Linear Regression": LinearRegression(n_jobs=n_jobs),
            "Ridge": Ridge(random_state=random_state),
            "Lasso": Lasso(random_state=random_state),
            "Decision Tree": DecisionTreeRegressor(random_state=random_state),
            "Random Forest": RandomForestRegressor(random_state=random_state, n_jobs=n_jobs),
            "Gradient Boosting": GradientBoostingRegressor(random_state=random_state),
            "Support Vector Machine": SVR(),
            "K-Nearest Neighbors": KNeighborsRegressor(n_jobs=n_jobs),
            "XGBoost": XGBRegressor(random_state=random_state, n_jobs=n_jobs),
            "Stacking": StackingRegressor(estimators=estimators_reg, final_estimator=Ridge(), n_jobs=n_jobs)
        }
    return models

def build_preprocessor(X: pd.DataFrame, problem_type: str, n_features: int = None, pca_components: int = None) -> ColumnTransformer:
    """Builds a scikit-learn ColumnTransformer for preprocessing."""
    numeric_features = X.select_dtypes(include=np.number).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    # Define pipelines for numeric and categorical features
    numeric_transformer_steps = [
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]
    if pca_components and pca_components > 0:
        numeric_transformer_steps.append(('pca', PCA(n_components=pca_components)))
        console.print(f"🔩 [cyan]Applying PCA with {pca_components} components.[/cyan]")

    numeric_transformer = Pipeline(steps=numeric_transformer_steps)

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Create the main preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough',
        n_jobs=-1 # Parallelize the transformation
    )
    return preprocessor

def train_and_evaluate_model(name, model, preprocessor, X_train, y_train, X_test, y_test, problem_type):
    """A helper function to train one model, used for parallel execution."""
    start_time = time.time()

    # Create the full pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    # Train model
    pipeline.fit(X_train, y_train)

    # Evaluate model
    y_pred = pipeline.predict(X_test)

    metric1, metric2 = (0, 0)
    if problem_type == 'classification':
        metric1 = accuracy_score(y_test, y_pred)
        metric2 = f1_score(y_test, y_pred, average='weighted')
    else: # regression
        metric1 = r2_score(y_test, y_pred)
        metric2 = np.sqrt(mean_squared_error(y_test, y_pred))

    elapsed_time = time.time() - start_time

    return {
        "Model": name,
        "Metric1": metric1,
        "Metric2": metric2,
        "Time (s)": elapsed_time,
        "pipeline": pipeline # Return the trained pipeline
    }

def generate_visuals(pipeline, X_test, y_test, problem_type, model_name, output_dir):
    """Generates and saves relevant plots for the best model."""
    console.print(f"🎨 [bold]Generating visuals for {model_name}...[/bold]")
    plt.style.use('seaborn-v0_8-whitegrid')

    if problem_type == 'classification':
        # Confusion Matrix
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ConfusionMatrixDisplay.from_estimator(pipeline, X_test, y_test, ax=ax, cmap='Blues', colorbar=False)
            ax.set_title(f'Confusion Matrix: {model_name}')
            plt.tight_layout()
            cm_path = output_dir / f"confusion_matrix_{model_name}.png"
            plt.savefig(cm_path)
            plt.close()
            console.print(f"  ✅ Confusion Matrix saved to [cyan]{cm_path}[/cyan]")
        except Exception as e:
            console.print(f"  ⚠️ Could not generate Confusion Matrix: {e}")

        # ROC Curve
        try:
            if hasattr(pipeline.named_steps['model'], "predict_proba"):
                fig, ax = plt.subplots(figsize=(8, 6))
                RocCurveDisplay.from_estimator(pipeline, X_test, y_test, ax=ax)
                ax.set_title(f'ROC Curve: {model_name}')
                plt.tight_layout()
                roc_path = output_dir / f"roc_curve_{model_name}.png"
                plt.savefig(roc_path)
                plt.close()
                console.print(f"  ✅ ROC Curve saved to [cyan]{roc_path}[/cyan]")
        except Exception as e:
            console.print(f"  ⚠️ Could not generate ROC Curve (possibly not a binary problem or model lacks predict_proba): {e}")

    else: # Regression
        y_pred = pipeline.predict(X_test)

        # Predicted vs. Actual Plot
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(y_test, y_pred, alpha=0.6, edgecolors='k')
            ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            ax.set_xlabel('Actual Values')
            ax.set_ylabel('Predicted Values')
            ax.set_title(f'Predicted vs. Actual: {model_name}')
            plt.tight_layout()
            pvsa_path = output_dir / f"predicted_vs_actual_{model_name}.png"
            plt.savefig(pvsa_path)
            plt.close()
            console.print(f"  ✅ Predicted vs. Actual plot saved to [cyan]{pvsa_path}[/cyan]")
        except Exception as e:
            console.print(f"  ⚠️ Could not generate Predicted vs. Actual plot: {e}")

        # Residuals Plot
        try:
            residuals = y_test - y_pred
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.residplot(x=y_pred, y=residuals, lowess=True, scatter_kws={'alpha': 0.5}, line_kws={'color': 'red', 'lw': 2}, ax=ax)
            ax.set_xlabel('Predicted Values')
            ax.set_ylabel('Residuals')
            ax.set_title(f'Residuals Plot: {model_name}')
            plt.tight_layout()
            res_path = output_dir / f"residuals_{model_name}.png"
            plt.savefig(res_path)
            plt.close()
            console.print(f"  ✅ Residuals plot saved to [cyan]{res_path}[/cyan]")
        except Exception as e:
            console.print(f"  ⚠️ Could not generate Residuals plot: {e}")


def generate_shap_plot(pipeline, X_train, X_test, problem_type, model_name, output_dir):
    """Generates and saves a SHAP summary plot for any model."""
    console.print(f"🤔 [bold]Generating SHAP interpretability plot for {model_name}...[/bold]")
    try:
        model = pipeline.named_steps['model']
        preprocessor = pipeline.named_steps['preprocessor']

        # Transform data and get feature names
        X_test_transformed = preprocessor.transform(X_test)

        try:
            # Works for ColumnTransformer with OneHotEncoder
            ohe_feature_names = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(
                X.select_dtypes(include=['object', 'category', 'bool']).columns
            )
            all_feature_names = X.select_dtypes(include=np.number).columns.tolist() + list(ohe_feature_names)
            X_test_transformed_df = pd.DataFrame(X_test_transformed, columns=all_feature_names)
        except Exception:
             # Fallback if feature names can't be extracted
            all_feature_names = None
            X_test_transformed_df = pd.DataFrame(X_test_transformed)


        # For complex models like Stacking, SHAP works best with a prediction function
        if problem_type == 'classification' and hasattr(model, 'predict_proba'):
            predict_fn = lambda x: pipeline.predict_proba(pd.DataFrame(x, columns=X_test.columns))
        else:
            predict_fn = lambda x: pipeline.predict(pd.DataFrame(x, columns=X_test.columns))

        # Use the appropriate explainer
        if isinstance(model, (DecisionTreeClassifier, DecisionTreeRegressor, RandomForestClassifier, RandomForestRegressor,
                              GradientBoostingClassifier, GradientBoostingRegressor, XGBClassifier, XGBRegressor)):
             explainer = shap.TreeExplainer(model, data=preprocessor.transform(X_train), feature_perturbation="interventional")
        else:
             # KernelExplainer is a model-agnostic fallback, requires a function and background data
             explainer = shap.KernelExplainer(predict_fn, shap.sample(X_train, 50))

        shap_values = explainer(X_test_transformed_df)

        # For classifiers with predict_proba, shap_values can be a list of arrays (one per class)
        if isinstance(shap_values, list):
             shap_values_to_plot = shap_values[1] # Plot for the positive class
        else:
             shap_values_to_plot = shap_values

        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values_to_plot, X_test_transformed_df, show=False, plot_type="bar")
        plt.title(f"SHAP Feature Importance: {model_name}")
        plt.tight_layout()
        
        shap_filename = output_dir / f"shap_summary_{model_name}.png"
        plt.savefig(shap_filename)
        plt.close()
        console.print(f"  ✅ SHAP summary plot saved to [cyan]'{shap_filename}'[/cyan]")

    except Exception as e:
        console.print(f"  [bold yellow]⚠️ Warning: Could not generate SHAP plot. Reason: {e}[/bold yellow]")


def main(args, save_artifacts=False):
    """Main function to run the enhanced ML pipeline."""
    # --- 1. Setup & Introduction ---
    start_run_time = time.time()
    output_dir = Path(args.output_dir) / f"results_{time.strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel("🧠 [bold magenta]Universal ML Model Explorer Pro[/bold magenta] is Starting!", title="🚀 Launching", border_style="green"))
    console.print(f"📂 All artifacts will be saved in: [cyan]{output_dir}[/cyan]")

    # --- 2. Dataset Loading ---
    try:
        df = pd.read_csv(args.dataset_path)
    except Exception as e:
        console.print(f"[bold red]❌ Error loading dataset: {e}[/bold red]")
        return

    if args.target_column not in df.columns:
        console.print(f"[bold red]❌ Error: Target column '{args.target_column}' not found.[/bold red]")
        return

    df = df.dropna(subset=[args.target_column]) # Drop rows where target is NaN
    console.print(f"✅ Dataset loaded successfully. Shape: {df.shape}")

    # --- 3. Data Preparation & Problem Detection ---
    X = df.drop(args.target_column, axis=1)
    y = df[args.target_column]

    problem_type = detect_problem_type(y)
    console.print(Panel(f"🤖 [bold]Detected Problem Type: [cyan]{problem_type.capitalize()}[/cyan][/bold]", title="🔍 Analysis", border_style="cyan"))

    if problem_type == 'classification':
        le = LabelEncoder()
        y = pd.Series(le.fit_transform(y), name=y.name)
        console.print(f"🏷️ Target variable encoded. Classes: {list(le.classes_)}")

    # --- 4. Preprocessing & Feature Engineering ---
    preprocessor = build_preprocessor(X, problem_type, args.pca_components)

    # The full pipeline will now include feature selection after preprocessing
    # We define the model step later

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if problem_type == 'classification' else None)

    # --- 5. Parallel Model Training ---
    models = get_models(problem_type)

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        console.print("\n[bold green]🏋️ Training all models in parallel... Please wait![/bold green]\n")

        results = Parallel(n_jobs=-1)(
            delayed(train_and_evaluate_model)(
                name, model, preprocessor, X_train, y_train, X_test, y_test, problem_type
            )
            for name, model in models.items()
        )


    # --- 6. Model Comparison & Best Model Selection ---
    metric1_name = "Accuracy" if problem_type == 'classification' else "R-squared"
    metric2_name = "F1-Score" if problem_type == 'classification' else "RMSE"
    sort_key, reverse_sort = ("Metric1", True) if problem_type == 'classification' else ("Metric1", True)

    results.sort(key=lambda x: x[sort_key], reverse=reverse_sort)
    best_model_result = results[0]
    best_model_name = best_model_result["Model"]
    best_pipeline = best_model_result["pipeline"]

    # Display results table
    table = Table(title=f"📊 [bold]Model Performance Comparison ({problem_type.capitalize()})[/bold]")
    table.add_column("Rank", style="blue")
    table.add_column("Model", style="cyan")
    table.add_column(metric1_name, style="green")
    table.add_column(metric2_name, style="magenta")
    table.add_column("Time (s)", justify="right", style="yellow")

    for i, res in enumerate(results):
        is_best = "👑 " if i == 0 else ""
        table.add_row(f"{i+1}", f"{is_best}{res['Model']}", f"{res['Metric1']:.4f}", f"{res['Metric2']:.4f}", f"{res['Time (s)']:.2f}")

    console.print(table)
    console.print(f"🏆 [bold green]Best Model Identified: {best_model_name}[/bold green]")

    # --- 7. Generate and Save Artifacts ---
    if save_artifacts:
        console.print("\n[bold blue]--- 💾 Generating Final Artifacts ---[/bold blue]")

        # a) Save best model
        model_filename = output_dir / "best_model.pkl"
        joblib.dump(best_pipeline, model_filename)
        console.print(f"✅ Best model saved as [cyan]'{model_filename}'[/cyan]")

        # b) Generate visuals for the best model
        generate_visuals(best_pipeline, X_test, y_test, problem_type, best_model_name, output_dir)

    # c) Generate SHAP plot for the best model
    if not args.no_shap and save_artifacts:
        generate_shap_plot(best_pipeline, X_train, X_test, problem_type, best_model_name, output_dir)

    # d) Save full report
    if save_artifacts:
        report_filename = output_dir / "model_report.txt"
        with open(report_filename, "w") as f:
            f.write(f"--- Universal ML Model Explorer Report ---\n\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dataset: {args.dataset_path}\n")
            f.write(f"Target Variable: {args.target_column}\n")
            f.write(f"Problem Type: {problem_type.capitalize()}\n\n")
            f.write(f"--- Best Model: {best_model_name} ---\n")
            f.write(f"  - {metric1_name}: {best_model_result['Metric1']:.4f}\n")
            f.write(f"  - {metric2_name}: {best_model_result['Metric2']:.4f}\n")
            f.write(f"  - Training Time (s): {best_model_result['Time (s)']:.2f}\n\n")
            f.write("--- Full Model Comparison ---\n")
            header = f"{'Rank':<5} {'Model':<25} {metric1_name:<15} {metric2_name:<15} {'Time (s)':<10}\n"
            f.write(header + "-"*len(header) + "\n")
            for i, res in enumerate(results):
                f.write(f"{i+1:<5} {res['Model']:<25} {res['Metric1']:<15.4f} {res['Metric2']:<15.4f} {res['Time (s)']:.2f}\n")
        console.print(f"📋 Full report saved to [cyan]'{report_filename}'[/cyan]")

    # --- 8. Conclusion ---
    total_runtime = time.time() - start_run_time
    console.print(Panel(f"✅ [bold green]Pipeline finished successfully in {total_runtime:.2f} seconds![/bold green]", title="🏁 Complete", border_style="green"))

def run_pipeline_in_notebook(dataset_path: str, target_column: str, save_artifacts: bool = False, **kwargs):
    """
    A helper to run the pipeline from a Jupyter Notebook or another script.

    Args:
        dataset_path (str): Path to the dataset.
        target_column (str): Name of the target column.
        **kwargs: Additional arguments like pca_components, no_shap, etc.
    """
    class Args:
        def __init__(self, dataset_path, target_column, **kwargs):
            self.dataset_path = dataset_path
            self.target_column = target_column
            self.output_dir = kwargs.get("output_dir", "results")
            self.pca_components = kwargs.get("pca_components", None)
            self.no_shap = kwargs.get("no_shap", False)

    args = Args(dataset_path, target_column, **kwargs)
    main(args)

if __name__ == "__main__":
    # Only run the argparse block if the script is executed directly
    # This prevents it from running when imported in a notebook
    import sys
    if 'ipykernel' not in sys.modules:
        parser = argparse.ArgumentParser(description="Universal ML Model Explorer Pro 🧠")
        parser.add_argument("dataset_path", type=str, help="Path to the input CSV dataset.")
        parser.add_argument("target_column", type=str, help="Name of the target variable column.")
        parser.add_argument("--output_dir", type=str, default="results", help="Directory to save all output artifacts.")
        parser.add_argument("--pca_components", type=int, default=None, help="Number of PCA components to use for numeric features.")
        parser.add_argument("--no_shap", action="store_true", help="Disable SHAP plot generation to save time.")

        args = parser.parse_args()
        main(args)