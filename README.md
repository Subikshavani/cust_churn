# Telco Customer Churn Intelligence Platform

A complete end-to-end customer churn prediction and retention optimization intelligence platform built with Python, scikit-learn, LightGBM, Plotly, SHAP, and Streamlit.

This application is designed as a premium, commercial-grade SaaS product suitable for hackathon demonstrations and executive presentations.

## Features

- **🏠 Executive Dashboard**: CEO-level metrics (Health Index, CLV, Churn Rate) and KPI charts.
- **🔮 Churn Prediction**: Real-time scoring form with probability gauges, risk badges, and confidence metrics.
- **🧠 Explainable AI**: Attributions (Global SHAP & local waterfall attribution charts) explaining the model decisions.
- **👥 Customer Segmentation**: 5 distinct clusters mapping tenure vs monthly spend (Premium, Loyal, High-Value, New, At-Risk).
- **💰 Revenue Risk Analysis**: Monthly/Annual exposure tracking and 12-month projections across Pessimistic, Target, and Optimistic scenarios.
- **🎯 Retention Simulator**: What-If adjustments of contracts and plans with live risk change feedback.
- **📈 Business Insights**: Automated campaigns (Loyalty Discounts, Contract upgrades) based on risk category.
- **⚙ Settings**: Model metrics comparison matrices and one-click model retraining studio.

## Project Structure

- `app.py` - Streamlit entry point & navigation mapping
- `src/modeling.py` - model training, evaluation, and pipeline selection
- `src/predict.py` - inference and explanation logic
- `src/charts.py` - Plotly visualizers (clusters, forecasts, waterfalls, timeline)
- `src/pages.py` - 8-page implementations
- `src/styles.py` - CSS premium styling system
- `src/utils.py` - metric reports and dashboard dataset predictions
- `data/` - folder for the Telco dataset
- `models/` - saved pipeline artifact (`model.pkl`) and metrics json
- `docs/` - architecture diagrams and presentation content

## Setup & Running

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the model manually (Optional)**:
   ```bash
   python -m src
   ```
   *Note: If the model is missing, the application will automatically train the pipelines and select the best one on startup.*

3. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

## Model Selection

The training pipeline compares:
- **Logistic Regression**
- **Random Forest**
- **LightGBM**

It automatically selects the best model based on ROC-AUC on a test split, writes performance to `models/metrics.json` and serializes the winning pipeline to `models/model.pkl`.
