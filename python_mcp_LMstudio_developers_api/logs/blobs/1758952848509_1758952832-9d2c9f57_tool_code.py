import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.datasets import make_regression
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("Step 1: Generate sample data")
# Create a synthetic dataset with 1000 samples and 5 features
X, y = make_regression(n_samples=1000, n_features=5, noise=0.1, random_state=42, 
                       effective_rank=3, n_informative=3)

# Convert to DataFrame for easier handling
feature_names = [f'Feature_{i+1}' for i in range(X.shape[1])]
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

print(f"Dataset shape: {df.shape}")
print("\nFirst few rows of the dataset:")
print(df.head())

print("\nStep 2: Split data into training and testing sets")
# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set size: {X_train.shape[0]}")
print(f"Testing set size: {X_test.shape[0]}")

print("\nStep 3: Train XGBoost regression model")
# Create and train the model
xgb_model = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train, y_train)

print("Model training completed!")

print("\nStep 4: Make predictions and evaluate")
# Make predictions
y_pred_train = xgb_model.predict(X_train)
y_pred_test = xgb_model.predict(X_test)

# Calculate metrics
train_mse = mean_squared_error(y_train, y_pred_train)
test_mse = mean_squared_error(y_test, y_pred_test)
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
train_mae = mean_absolute_error(y_train, y_pred_train)
test_mae = mean_absolute_error(y_test, y_pred_test)

print("Model Performance Metrics:")
print(f"Training MSE: {train_mse:.4f}")
print(f"Testing MSE:  {test_mse:.4f}")
print(f"Training R²:  {train_r2:.4f}")
print(f"Testing R²:   {test_r2:.4f}")
print(f"Training MAE: {train_mae:.4f}")
print(f"Testing MAE:  {test_mae:.4f}")

print("\nStep 5: Create comprehensive visualizations")

# Create a figure with multiple subplots
fig = plt.figure(figsize=(18, 16))

# 1. Actual vs Predicted plot (testing set)
plt.subplot(2, 3, 1)
plt.scatter(y_test, y_pred_test, alpha=0.6, color='blue')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title(f'Actual vs Predicted (R² = {test_r2:.3f})')

# 2. Residuals plot
plt.subplot(2, 3, 2)
residuals = y_test - y_pred_test
plt.scatter(y_pred_test, residuals, alpha=0.6, color='green')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residuals Plot')

# 3. Feature importance plot
plt.subplot(2, 3, 3)
feature_importance = xgb_model.feature_importances_
indices = np.argsort(feature_importance)[::-1]
plt.bar(range(len(feature_importance)), feature_importance[indices])
plt.xlabel('Feature Index')
plt.ylabel('Importance')
plt.title('Feature Importance')
plt.xticks(range(len(feature_importance)), [feature_names[i] for i in indices], rotation=45)

# 4. Distribution of residuals
plt.subplot(2, 3, 4)
plt.hist(residuals, bins=30, alpha=0.7, color='orange', edgecolor='black')
plt.xlabel('Residual Value')
plt.ylabel('Frequency')
plt.title('Distribution of Residuals')

# 5. Learning curve (training vs validation scores)
plt.subplot(2, 3, 5)
train_scores = []
val_scores = []

for n_est in range(10, 101, 10):
    temp_model = XGBRegressor(n_estimators=n_est, max_depth=6, learning_rate=0.1, random_state=42)
    temp_model.fit(X_train, y_train)
    
    train_pred = temp_model.predict(X_train)
    val_pred = temp_model.predict(X_test)
    
    train_scores.append(r2_score(y_train, train_pred))
    val_scores.append(r2_score(y_test, val_pred))

plt.plot(range(10, 101, 10), train_scores, label='Training Score', marker='o')
plt.plot(range(10, 101, 10), val_scores, label='Validation Score', marker='s')
plt.xlabel('Number of Estimators')
plt.ylabel('R² Score')
plt.title('Learning Curve')
plt.legend()

# 6. Prediction error distribution
plt.subplot(2, 3, 6)
prediction_errors = np.abs(y_test - y_pred_test)
plt.hist(prediction_errors, bins=30, alpha=0.7, color='purple', edgecolor='black')
plt.xlabel('Absolute Prediction Error')
plt.ylabel('Frequency')
plt.title('Distribution of Prediction Errors')

plt.tight_layout()
plt.savefig('xgboost_regression_analysis.png', dpi=300, bbox_inches='tight')
print("Plot saved as 'xgboost_regression_analysis.png'")

# Print feature importance in a readable format
print("\nFeature Importance Ranking:")
for i, idx in enumerate(indices):
    print(f"{i+1}. {feature_names[idx]}: {feature_importance[idx]:.4f}")

plt.show()
