import shap
import pandas as pd

def get_shap_values(model, X_sample):
    """
    Explain model prediction using SHAP
    """

    # Extract trained model inside pipeline
    clf = model.named_steps['model']

    explainer = shap.TreeExplainer(clf)

    shap_values = explainer.shap_values(X_sample)

    return explainer, shap_values