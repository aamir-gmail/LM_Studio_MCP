import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Generate sample data
n_samples = 1000
X = np.random.randn(n_samples, 5)
y = 2*X[:, 0] + 3*X[:, 1] - 1.5*X[:, 2] + 0.5*X[:, 3] + 0.1*X[:, 4] + np.random.randn(n_samples)*0.5

# Create DataFrame
feature_names = [f'Feature_{i+1}' for i in range(5)]
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

print("Dataset Info:")
print(f"Shape: {df.shape}")
print("\nFirst 5 rows:")
print(df.head())

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = xgb.XGBRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate metrics
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\nModel Performance:")
print(f"R² Score: {r2:.3f}")
print(f"Mean Squared Error: {mse:.3f}")
print(f"Mean Absolute Error: {mae:.3f}")

# Feature importance
importance = model.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importance
}).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
for idx, row in feature_importance_df.iterrows():
    print(f"{row['Feature']}: {row['Importance']:.4f}")

# Create visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Actual vs Predicted
plt.subplot(2, 3, 1)
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title(f'Actual vs Predicted (R² = {r2:.3f})')

# Plot 2: Residuals
plt.subplot(2, 3, 2)
residuals = y_test - y_pred
plt.scatter(y_pred, residuals, alpha=0.6)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residuals Plot')

# Plot 3: Feature Importance
plt.subplot(2, 3, 3)
sns.barplot(data=feature_importance_df, x='Importance', y='Feature')
plt.title('Feature Importance')

# Plot 4: Residuals Distribution
plt.subplot(2, 3, 4)
plt.hist(residuals, bins=30, alpha=0.7)
plt.xlabel('Residuals')
plt.ylabel('Frequency')
plt.title('Distribution of Residuals')

# Plot 5: Learning Curve (simplified)
plt.subplot(2, 3, 5)
train_scores = []
val_scores = []
for n in [10, 25, 50, 75, 100]:
    model_temp = xgb.XGBRegressor(n_estimators=n, random_state=42)
    model_temp.fit(X_train, y_train)
    train_pred = model_temp.predict(X_train)
    val_pred = model_temp.predict(X_test)
    train_scores.append(r2_score(y_train, train_pred))
    val_scores.append(r2_score(y_test, val_pred))

plt.plot([10, 25, 50, 75, 100], train_scores, 'o-', label='Training')
plt.plot([10, 25, 50, 75, 100], val_scores, 'o-', label='Validation')
plt.xlabel('Number of Estimators')
plt.ylabel('R² Score')
plt.title('Learning Curve')
plt.legend()

# Plot 6: Prediction Error Distribution
plt.subplot(2, 3, 6)
errors = np.abs(y_test - y_pred)
plt.hist(errors, bins=30, alpha=0.7)
plt.xlabel('Absolute Error')
plt.ylabel('Frequency')
plt.title('Distribution of Prediction Errors')

plt.tight_layout()
plt.savefig('xgboost_regression_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nAnalysis Complete!")