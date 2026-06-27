# Presentation Slides Content: Customer Retention Intelligence Platform

## Slide 1: Title & Vision
- **Product Name**: Telco Churn Intelligence Platform
- **Subtitle**: AI-Powered Customer Health and Revenue Risk Optimization
- **Target Audience**: Telecom Executives, Retention Managers, and Marketing Teams
- **Core Value Proposition**: Predict churn risk, understand driving factors, simulate interventions, and secure contract revenues.

## Slide 2: The Core Business Problem
- **Customer Churn**: Subscriber losses bleed telecom margins silently.
- **Unaware Leakage**: Dashboards identify who has left, but not who is *about* to leave.
- **Inactionable Analytics**: Standalone prediction models lack direct translation to targeted save campaigns or pricing intervention forecasts.

## Slide 3: Unified Platform Solution
- **Machine Learning**: Compare Logistic Regression, Random Forest, and LightGBM models automatically, selecting the winner based on ROC-AUC.
- **Executive Visibility**: Instant readouts on total customers, CLV, Health Indexes, and cumulative revenue loss projections.
- **Actionable Save Campaigns**: Automatically generated campaign recommendations and an interactive what-if simulator to optimize retention rates.

## Slide 4: Premium Dark SaaS Architecture
- **Tech Stack**: Python, Scikit-learn, LightGBM, Streamlit, Plotly, SHAP, and Joblib.
- **Glassmorphism Design**: High-fidelity dark mode visual styling.
- **Seamless Data Flow**: CSV upload/demo data $\rightarrow$ Feature Engineering $\rightarrow$ Automated Pipeline Selection $\rightarrow$ Saved to `model.pkl` $\rightarrow$ Real-time Dashboards.

## Slide 5: The 8-Page Navigation Map
1. **🏠 Executive Dashboard**: CEO-level metrics (Health, CLV, Revenue Risk, Trends).
2. **🔮 Churn Prediction**: Real-time scoring form with probability gauges.
3. **🧠 Explainable AI**: Feature attributions (Global SHAP & local waterfall attribution charts).
4. **👥 Customer Segmentation**: 5 distinct clusters mapping tenure vs monthly spend.
5. **💰 Revenue Risk Analysis**: 12-month projections across Pessimistic, Target, and Optimistic scenarios.
6. **🎯 Retention Simulator**: What-If adjustments of contracts and plans with live risk change feedback.
7. **📈 Business Insights**: Risk-targeted save recommendation campaign cards.
8. **⚙ Settings**: Model metrics performance tables and one-click retraining triggers.

## Slide 6: Machine Learning Comparison Results
- **Auto-Winner Selected**: Logistic Regression (Winner on demo set with ROC-AUC of 0.81).
- **Comparison Matrix**: Tracks Accuracy, Precision, Recall, F1, and ROC-AUC.
- **Pipeline Architecture**: Combines scaling, imputation, and classification.

## Slide 7: Business Outcomes & ROI
- **Revenue Protection**: Target and retain up to 60% of high-risk customers, protecting thousands of dollars in monthly revenue.
- **Precision Marketing**: Spend retention budget on subscribers with high probability and CLV, minimizing promotional waste on stable customers.
- **Proactive Interventions**: Move subscribers from Month-to-month contracts to 1-year agreements before they churn.
