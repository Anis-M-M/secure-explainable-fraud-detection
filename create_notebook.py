"""
Generates Fraud_Detection_Presentation.ipynb
Run: .venv/Scripts/python create_notebook.py
"""
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

cells = []

# Title
cells.append(new_markdown_cell("""\
# Secure and Explainable Fraud Detection System
**Anis Mohammed Metkari & Sharwari Rajendra Nimbalkar**
Supervisor: Irina Tal | MSc Computing, Dublin City University

**RQ1:** How do rule-based, Logistic Regression, XGBoost and Neural Network models compare on
imbalanced fraud data?
**RQ2:** How do SHAP and LIME differ in explanation stability and consistency?

Dataset: Kaggle Credit Card Fraud Detection — 284,807 transactions, 0.17% fraud
"""))

# ---- 1. Setup ---------------------------------------------------------------
cells.append(new_markdown_cell("## 1. Setup"))

cells.append(new_code_cell("""\
import warnings
warnings.filterwarnings('ignore')
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score,
    f1_score, accuracy_score, precision_score, recall_score,
)
from imblearn.over_sampling import SMOTE

import xgboost as xgb
import shap
import lime
import lime.lime_tabular

DATA_PATH  = r"C:\\Users\\metka\\Desktop\\FRAUD DETECTION\\data\\creditcard.csv"
OUTPUT_DIR = r"C:\\Users\\metka\\Desktop\\FRAUD DETECTION\\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

plt.rcParams.update({
    'figure.dpi': 110,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
sns.set_palette('husl')

MODEL_COLORS = {
    'Rule-Based':    '#9C27B0',
    'Logistic Reg.': '#2196F3',
    'XGBoost':       '#FF9800',
    'Neural Network':'#4CAF50',
}

print("Libraries loaded.")
print(f"NumPy {np.__version__}, pandas {pd.__version__}, XGBoost {xgb.__version__}, SHAP {shap.__version__}")
"""))

# ---- 2. Data ----------------------------------------------------------------
cells.append(new_markdown_cell("## 2. Loading the Dataset"))

cells.append(new_code_cell("""\
df = pd.read_csv(DATA_PATH)

n_total = len(df)
n_fraud = int(df['Class'].sum())
n_legit = n_total - n_fraud

print(f"Total rows:   {n_total:,}")
print(f"Legitimate:   {n_legit:,}  ({n_legit/n_total*100:.2f}%)")
print(f"Fraud:        {n_fraud:,}  ({n_fraud/n_total*100:.3f}%)")
print(f"Imbalance:    {n_legit/n_fraud:.0f}:1")
print(f"Features:     {len(df.columns)-1}")
print(f"Missing vals: {df.isnull().sum().sum()}")

print("\\nAmount stats by class:")
print(df.groupby('Class')['Amount']
      .describe()[['mean','std','min','50%','max']]
      .round(2)
      .rename(index={0:'Legitimate', 1:'Fraud'})
      .to_string())
"""))

# ---- 3. EDA -----------------------------------------------------------------
cells.append(new_markdown_cell("## 3. Exploratory Data Analysis"))

cells.append(new_code_cell("""\
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('EDA — Credit Card Fraud Dataset', fontsize=14, fontweight='bold', y=1.02)

# Class distribution
ax = axes[0]
bars = ax.bar(['Legitimate\\n(Class=0)', 'Fraud\\n(Class=1)'],
              [n_legit, n_fraud],
              color=['#2196F3', '#F44336'], edgecolor='black', linewidth=0.8, width=0.5)
ax.set_title('Class Distribution', fontweight='bold')
ax.set_ylabel('Number of Transactions')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))
for bar, v in zip(bars, [n_legit, n_fraud]):
    ax.text(bar.get_x()+bar.get_width()/2, v + n_total*0.008,
            f'{v:,}\\n({v/n_total*100:.2f}%)', ha='center', fontsize=9, fontweight='bold')
ax.set_ylim(0, max(n_legit, n_fraud) * 1.25)

# Amount distribution (log-transformed)
ax = axes[1]
ax.hist(np.log1p(df[df['Class']==0]['Amount']), bins=60,
        alpha=0.65, color='#2196F3', label='Legitimate', density=True)
ax.hist(np.log1p(df[df['Class']==1]['Amount']), bins=60,
        alpha=0.65, color='#F44336', label='Fraud', density=True)
ax.set_title('Transaction Amount\\n(log(1+Amount))', fontweight='bold')
ax.set_xlabel('log(1 + Amount)')
ax.set_ylabel('Density')
ax.legend()

# V14 distribution
ax = axes[2]
ax.hist(df[df['Class']==0]['V14'], bins=60, alpha=0.65,
        color='#2196F3', label='Legitimate', density=True)
ax.hist(df[df['Class']==1]['V14'], bins=60, alpha=0.65,
        color='#F44336', label='Fraud', density=True)
ax.set_title('V14 Feature Distribution\\n(Strongest Fraud Discriminator)', fontweight='bold')
ax.set_xlabel('V14')
ax.set_ylabel('Density')
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '01_eda_overview.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_code_cell("""\
# Feature discrimination using t-test
feature_cols_v = [f'V{i}' for i in range(1, 29)]
t_stats = {
    col: abs(stats.ttest_ind(df[df['Class']==0][col],
                             df[df['Class']==1][col]).statistic)
    for col in feature_cols_v
}
sep_series = pd.Series(t_stats).sort_values(ascending=False)
top10 = sep_series.head(10).index.tolist()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Feature Discrimination Analysis', fontsize=14, fontweight='bold')

ax = axes[0]
bar_colors = ['#F44336' if i < 5 else '#FF9800' if i < 10 else '#4CAF50'
              for i in range(len(sep_series))]
ax.barh(sep_series.index[::-1], sep_series.values[::-1],
        color=bar_colors[::-1], edgecolor='white', linewidth=0.3)
ax.set_title('Feature Discrimination Power\\n(|t-statistic|)', fontweight='bold')
ax.set_xlabel('|t-statistic|')
ax.legend(handles=[
    mpatches.Patch(color='#F44336', label='Top 5'),
    mpatches.Patch(color='#FF9800', label='Top 6-10'),
    mpatches.Patch(color='#4CAF50', label='Remaining'),
], loc='lower right')

ax = axes[1]
corr_data = df[top10 + ['Amount', 'Class']].corr()
diag_mask = np.eye(len(corr_data), dtype=bool)
sns.heatmap(corr_data, ax=ax, cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            annot=True, fmt='.2f', linewidths=0.5, annot_kws={'size': 7},
            mask=diag_mask, cbar_kws={'shrink': 0.8})
ax.set_title('Correlation Matrix (Top-10 Features + Amount)', fontweight='bold')
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '02_feature_analysis.png'), bbox_inches='tight', dpi=150)
plt.show()

print("Top 5 discriminative features:", sep_series.head(5).index.tolist())
"""))

# ---- 4. Preprocessing -------------------------------------------------------
cells.append(new_markdown_cell("""\
## 4. Preprocessing

- Features: V1-V28 (already PCA-scaled by Kaggle) + Amount (StandardScaled separately)
- Time column dropped
- Split: 70% train / 10% val / 20% test (stratified)
- SMOTE applied on training set only to handle the 577:1 class imbalance
"""))

cells.append(new_code_cell("""\
FEATURE_COLS = [f'V{i}' for i in range(1, 29)] + ['Amount']
AMOUNT_IDX   = FEATURE_COLS.index('Amount')

X = df[FEATURE_COLS].values
y = df['Class'].values

X_tv, X_test, y_tv, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(
    X_tv, y_tv, test_size=0.125, random_state=RANDOM_STATE, stratify=y_tv)

# Scale Amount only — V1-V28 are already PCA-scaled
scaler = StandardScaler()
X_train_s = X_train.copy()
X_val_s   = X_val.copy()
X_test_s  = X_test.copy()
X_train_s[:, AMOUNT_IDX] = scaler.fit_transform(X_train[:, AMOUNT_IDX].reshape(-1,1)).ravel()
X_val_s  [:, AMOUNT_IDX] = scaler.transform(X_val  [:, AMOUNT_IDX].reshape(-1,1)).ravel()
X_test_s [:, AMOUNT_IDX] = scaler.transform(X_test [:, AMOUNT_IDX].reshape(-1,1)).ravel()

smote = SMOTE(random_state=RANDOM_STATE)
X_train_sm, y_train_sm = smote.fit_resample(X_train_s, y_train)

print(f"{'Split':>26} | {'Samples':>10} | {'Fraud':>8} | {'Fraud %':>8}")
print("-"*60)
for name, Xd, yd in [
    ("Train (before SMOTE)", X_train_s,  y_train),
    ("Train (after SMOTE)",  X_train_sm, y_train_sm),
    ("Validation",           X_val_s,    y_val),
    ("Test",                 X_test_s,   y_test),
]:
    print(f"  {name:>24} | {len(Xd):>10,} | {int(yd.sum()):>8,} | {yd.mean()*100:>7.3f}%")
"""))

# ---- 5. Models --------------------------------------------------------------
cells.append(new_markdown_cell("## 5. Model Training"))

cells.append(new_markdown_cell("### 5a. Rule-Based Detector"))

cells.append(new_code_cell("""\
class RuleBasedDetector:
    # Simple rule system — learns thresholds from fraud distribution in training data
    def fit(self, X, y):
        fraud_X = X[y == 1]
        self._rules = [
            (13, np.percentile(fraud_X[:, 13], 8),  'lt', 0.35),  # V14
            (11, np.percentile(fraud_X[:, 11], 8),  'lt', 0.20),  # V12
            (9,  np.percentile(fraud_X[:, 9],  8),  'lt', 0.20),  # V10
            (10, np.percentile(fraud_X[:, 10], 8),  'lt', 0.15),  # V11
            (3,  np.percentile(fraud_X[:, 3],  92), 'gt', 0.10),  # V4
        ]
        return self

    def _score(self, x):
        s = sum(w for col, thr, d, w in self._rules
                if (d == 'lt' and x[col] < thr) or (d == 'gt' and x[col] > thr))
        return min(s, 1.0)

    def predict_proba(self, X):
        p = np.array([self._score(x) for x in X])
        return np.column_stack([1 - p, p])

    def predict(self, X, threshold=0.35):
        return (self.predict_proba(X)[:, 1] >= threshold).astype(int)

rule_model = RuleBasedDetector().fit(X_train_s, y_train)

feat_names = ['V14', 'V12', 'V10', 'V11', 'V4']
print("Rule thresholds:")
for (col_idx, thresh, direction, weight), fname in zip(rule_model._rules, feat_names):
    print(f"  {fname}  {direction}  {thresh:.4f}  (weight={weight})")
"""))

cells.append(new_markdown_cell("### 5b. Logistic Regression"))

cells.append(new_code_cell("""\
lr_model = LogisticRegression(
    class_weight='balanced', max_iter=1000, C=1.0,
    solver='lbfgs', random_state=RANDOM_STATE
)
lr_model.fit(X_train_sm, y_train_sm)

print("Logistic Regression trained.")
lr_imp = pd.Series(np.abs(lr_model.coef_[0]), index=FEATURE_COLS).sort_values(ascending=False)
print("Top 5 coefficients:")
print(lr_imp.head(5).round(4).to_string())
"""))

cells.append(new_markdown_cell("### 5c. XGBoost"))

cells.append(new_code_cell("""\
xgb_model = xgb.XGBClassifier(
    n_estimators=300, max_depth=6, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    scale_pos_weight=1,
    eval_metric='aucpr',
    random_state=RANDOM_STATE, n_jobs=-1, verbosity=0,
)
xgb_model.fit(X_train_sm, y_train_sm, verbose=False)

print("XGBoost trained (300 trees, depth 6).")
xgb_imp = pd.Series(xgb_model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
print("Top 5 by built-in importance:")
print(xgb_imp.head(5).round(4).to_string())
"""))

cells.append(new_markdown_cell("### 5d. Neural Network"))

cells.append(new_code_cell("""\
import tensorflow as tf
from tensorflow import keras

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.random.set_seed(RANDOM_STATE)

nn_model = keras.Sequential([
    keras.layers.Input(shape=(X_train_sm.shape[1],)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.BatchNormalization(),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid'),
], name='FraudDetector_NN')

nn_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['AUC'],
)

history = nn_model.fit(
    X_train_sm, y_train_sm,
    epochs=60, batch_size=512,
    validation_data=(X_val_s, y_val),
    callbacks=[
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=7,
                                      restore_best_weights=True, verbose=0),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                          patience=4, verbose=0),
    ],
    verbose=0
)
print(f"Neural Network trained ({len(history.history['loss'])} epochs).")
nn_model.summary()
"""))

cells.append(new_code_cell("""\
# Training curves
auc_key     = [k for k in history.history if 'auc' in k.lower() and 'val' not in k][0]
val_auc_key = 'val_' + auc_key

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle('Neural Network Training', fontsize=13, fontweight='bold')

r = range(1, len(history.history['loss']) + 1)
axes[0].plot(r, history.history['loss'],       'b-', lw=2, label='Train')
axes[0].plot(r, history.history['val_loss'],   'r-', lw=2, label='Val')
axes[0].set_title('Loss', fontweight='bold')
axes[0].set_xlabel('Epoch'); axes[0].legend()

axes[1].plot(r, history.history[auc_key],     'b-', lw=2, label='Train')
axes[1].plot(r, history.history[val_auc_key], 'r-', lw=2, label='Val')
axes[1].set_title('AUC', fontweight='bold')
axes[1].set_xlabel('Epoch'); axes[1].legend()

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '03_nn_training.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

# ---- 6. RQ1 -----------------------------------------------------------------
cells.append(new_markdown_cell("""\
## 6. RQ1 — Model Performance Comparison

How do the four models compare when evaluated on the imbalanced test set?
"""))

cells.append(new_code_cell("""\
def evaluate(name, model, X, y, threshold=0.5, is_nn=False):
    y_prob = model.predict(X, verbose=0).ravel() if is_nn else model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    return {
        'Model':     name,
        'Precision': precision_score(y, y_pred, zero_division=0),
        'Recall':    recall_score(y, y_pred, zero_division=0),
        'F1':        f1_score(y, y_pred, zero_division=0),
        'ROC-AUC':   roc_auc_score(y, y_prob),
        'PR-AUC':    average_precision_score(y, y_prob),
        '_prob': y_prob,
        '_pred': y_pred,
        '_cm':   confusion_matrix(y, y_pred),
    }

results = {
    'Rule-Based':    evaluate('Rule-Based',    rule_model,  X_test_s, y_test, threshold=0.35),
    'Logistic Reg.': evaluate('Logistic Reg.', lr_model,   X_test_s, y_test),
    'XGBoost':       evaluate('XGBoost',       xgb_model,  X_test_s, y_test),
    'Neural Network':evaluate('Neural Network',nn_model,   X_test_s, y_test, is_nn=True),
}

KEY_METRICS = ['Precision', 'Recall', 'F1', 'ROC-AUC', 'PR-AUC']
metrics_df = (
    pd.DataFrame([{k: v for k, v in r.items() if k in KEY_METRICS + ['Model']}
                  for r in results.values()])
      .set_index('Model')
)

print("RQ1 — Test set results")
print(metrics_df[KEY_METRICS].round(4).to_string())
print()
print(f"Best F1:      {metrics_df['F1'].idxmax()} ({metrics_df['F1'].max():.4f})")
print(f"Best ROC-AUC: {metrics_df['ROC-AUC'].idxmax()} ({metrics_df['ROC-AUC'].max():.4f})")
print(f"Best PR-AUC:  {metrics_df['PR-AUC'].idxmax()} ({metrics_df['PR-AUC'].max():.4f})")
"""))

cells.append(new_code_cell("""\
model_names = list(results.keys())

fig, axes = plt.subplots(1, len(KEY_METRICS), figsize=(18, 5))
fig.suptitle('RQ1: Model Performance Comparison (Test Set)', fontsize=14, fontweight='bold')

for ax, metric in zip(axes, KEY_METRICS):
    vals = [results[m][metric] for m in model_names]
    bars = ax.bar(range(len(model_names)), vals,
                  color=[MODEL_COLORS[n] for n in model_names],
                  edgecolor='white', linewidth=0.5)
    ax.set_title(metric, fontweight='bold')
    ax.set_xticks(range(len(model_names)))
    ax.set_xticklabels([n.replace(' ', '\\n') for n in model_names], fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.axhline(1.0, color='gray', ls='--', lw=0.5, alpha=0.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, v+0.01,
                f'{v:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '04_metrics_comparison.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_code_cell("""\
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('RQ1: ROC and Precision-Recall Curves', fontsize=14, fontweight='bold')

ax = axes[0]
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res['_prob'])
    ax.plot(fpr, tpr, label=f"{name} (AUC={res['ROC-AUC']:.3f})",
            color=MODEL_COLORS[name], lw=2.5)
ax.plot([0,1],[0,1], 'k--', lw=1, alpha=0.4, label='Random')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curves', fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
axins = ax.inset_axes([0.38, 0.06, 0.55, 0.45])
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res['_prob'])
    axins.plot(fpr, tpr, color=MODEL_COLORS[name], lw=1.5)
axins.set_xlim(0, 0.02); axins.set_ylim(0.6, 1.0)
axins.set_title('Zoom FPR < 0.02', fontsize=8)
ax.indicate_inset_zoom(axins, edgecolor='black')

ax = axes[1]
for name, res in results.items():
    prec, rec, _ = precision_recall_curve(y_test, res['_prob'])
    ax.plot(rec, prec, label=f"{name} (AP={res['PR-AUC']:.3f})",
            color=MODEL_COLORS[name], lw=2.5)
ax.axhline(y_test.mean(), color='k', ls='--', lw=1, alpha=0.4,
           label=f"Random ({y_test.mean():.3f})")
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curves', fontweight='bold')
ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '05_roc_pr_curves.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_code_cell("""\
fig, axes = plt.subplots(1, 4, figsize=(17, 4))
fig.suptitle('Confusion Matrices — Test Set', fontsize=14, fontweight='bold')

for ax, (name, res) in zip(axes, results.items()):
    tn, fp, fn, tp = res['_cm'].ravel()
    sns.heatmap([[tn, fp], [fn, tp]], ax=ax,
                annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Legit', 'Fraud'], yticklabels=['Legit', 'Fraud'],
                linewidths=1)
    ax.set_title(f"{name}\\nF1={res['F1']:.3f}  Recall={res['Recall']:.3f}",
                 fontweight='bold', fontsize=10)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '06_confusion_matrices.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

# ---- 7. RQ2 Explainability --------------------------------------------------
cells.append(new_markdown_cell("""\
## 7. RQ2 — Explainability Analysis (SHAP & LIME)

Focus model: XGBoost (best F1/PR-AUC, supports exact TreeSHAP).
"""))

cells.append(new_markdown_cell("### 7a. SHAP — Global Feature Importance"))

cells.append(new_code_cell("""\
print("Computing SHAP values...")
explainer_xgb = shap.TreeExplainer(xgb_model)

rng_shap = np.random.default_rng(RANDOM_STATE)
fraud_idx_test = np.where(y_test == 1)[0]
legit_idx_test = np.where(y_test == 0)[0]
n_each = 200
sample_idx = np.concatenate([
    rng_shap.choice(legit_idx_test, n_each, replace=False),
    rng_shap.choice(fraud_idx_test, min(n_each, len(fraud_idx_test)), replace=False),
])
X_shap = X_test_s[sample_idx]
y_shap = y_test[sample_idx]

shap_values = explainer_xgb.shap_values(X_shap)
print(f"SHAP values shape: {np.array(shap_values).shape}")
print(f"Sample: {(y_shap==1).sum()} fraud / {(y_shap==0).sum()} legitimate")

mean_shap = np.abs(shap_values).mean(axis=0)
shap_imp_series = pd.Series(mean_shap, index=FEATURE_COLS).sort_values(ascending=False)
print("\\nTop 5 by mean |SHAP|:")
print(shap_imp_series.head(5).round(5).to_string())
"""))

cells.append(new_code_cell("""\
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_shap, feature_names=FEATURE_COLS,
                  show=False, max_display=15)
plt.title('SHAP Beeswarm — Feature impact on fraud probability',
          fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '07_shap_beeswarm.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_code_cell("""\
shap_sorted = shap_imp_series.sort_values()
bar_clrs = plt.cm.RdYlGn_r(np.linspace(0.05, 0.9, len(shap_sorted)))

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(shap_sorted.index, shap_sorted.values, color=bar_clrs,
        edgecolor='white', linewidth=0.3)
ax.set_title('Mean |SHAP Value| — XGBoost', fontsize=13, fontweight='bold')
ax.set_xlabel('Mean |SHAP Value|')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '08_shap_importance_bar.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_markdown_cell("### 7b. SHAP — Individual Prediction"))

cells.append(new_code_cell("""\
fraud_mask  = y_shap == 1
fraud_probs = xgb_model.predict_proba(X_shap[fraud_mask])[:, 1]
best_local  = fraud_mask.nonzero()[0][np.argmax(fraud_probs)]
fraud_prob_val = fraud_probs.max()

sv_single    = shap_values[best_local]
top_feat_idx = np.argsort(np.abs(sv_single))[-12:][::-1]
feats_shown  = [FEATURE_COLS[i] for i in top_feat_idx]
vals_shown   = [sv_single[i]    for i in top_feat_idx]

fig, ax = plt.subplots(figsize=(11, 5))
bar_clrs = ['#F44336' if v > 0 else '#2196F3' for v in vals_shown]
ax.barh(range(len(feats_shown)), vals_shown[::-1],
        color=bar_clrs[::-1], edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(feats_shown)))
ax.set_yticklabels(feats_shown[::-1])
ax.axvline(0, color='black', lw=0.8)
ax.set_title(f'SHAP — Fraud Transaction  (P(fraud) = {fraud_prob_val:.3f})',
             fontweight='bold')
ax.set_xlabel('SHAP value (positive = pushes toward fraud)')
ax.legend(handles=[
    mpatches.Patch(color='#F44336', label='Increases fraud probability'),
    mpatches.Patch(color='#2196F3', label='Decreases fraud probability'),
], loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '09_shap_individual.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_markdown_cell("### 7c. LIME — Local Explanation"))

cells.append(new_code_cell("""\
print("Setting up LIME...")
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    X_train_sm,
    feature_names=FEATURE_COLS,
    class_names=['Legitimate', 'Fraud'],
    mode='classification',
    random_state=RANDOM_STATE,
)

lime_instance = X_shap[best_local]
lime_prob = xgb_model.predict_proba(lime_instance.reshape(1, -1))[0, 1]
print(f"Explaining: P(fraud) = {lime_prob:.3f}")

lime_exp = lime_explainer.explain_instance(
    lime_instance, xgb_model.predict_proba,
    num_features=12, num_samples=1500,
)
fig = lime_exp.as_pyplot_figure()
fig.set_size_inches(11, 7)
plt.title(f'LIME — Fraud Transaction  (P(fraud) = {lime_prob:.3f})',
          fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '10_lime_explanation.png'), bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(new_markdown_cell("""\
### 7d. Stability Analysis

Perturbing each fraud instance with Gaussian noise and measuring Jaccard similarity of the
top-5 feature sets before and after perturbation, for both SHAP and LIME.

> Note: this cell takes around 5-10 minutes. Run it before the presentation.
"""))

cells.append(new_code_cell("""\
def top_n_shap(sv_row, n=5):
    return set(np.argsort(np.abs(sv_row))[-n:])

def top_n_lime(exp, n=5):
    # Sort feature names longest-first to avoid V1 matching V14 etc.
    feat_by_len = sorted(enumerate(FEATURE_COLS), key=lambda x: len(x[1]), reverse=True)
    top = set()
    for feat_str, _ in sorted(exp.as_list(), key=lambda x: abs(x[1]), reverse=True)[:n]:
        for i, fn in feat_by_len:
            if fn in feat_str:
                top.add(i)
                break
    return top

def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 1.0

NOISE_LEVELS    = [0.01, 0.05, 0.10, 0.20]
N_INSTANCES     = 20
N_PERTURBATIONS = 10
rng_stab        = np.random.default_rng(RANDOM_STATE + 1)

fraud_test_idx  = np.where(y_test == 1)[0]
stab_idx        = fraud_test_idx[:N_INSTANCES]

shap_stability  = {nl: [] for nl in NOISE_LEVELS}
lime_stability  = {nl: [] for nl in NOISE_LEVELS}

print(f"{N_INSTANCES} instances x {N_PERTURBATIONS} perturbations x {len(NOISE_LEVELS)} noise levels")

for nl in NOISE_LEVELS:
    print(f"  sigma={nl} ...", end=' ', flush=True)
    for idx in stab_idx:
        x_orig = X_test_s[idx]
        orig_sv      = explainer_xgb.shap_values(x_orig.reshape(1, -1))[0]
        orig_shap_t  = top_n_shap(orig_sv)
        orig_lime_exp = lime_explainer.explain_instance(
            x_orig, xgb_model.predict_proba, num_features=5, num_samples=200)
        orig_lime_t  = top_n_lime(orig_lime_exp)

        shap_j, lime_j = [], []
        for _ in range(N_PERTURBATIONS):
            x_p = x_orig + rng_stab.normal(0, nl, x_orig.shape)
            sv_p = explainer_xgb.shap_values(x_p.reshape(1, -1))[0]
            shap_j.append(jaccard(orig_shap_t, top_n_shap(sv_p)))
            exp_p = lime_explainer.explain_instance(
                x_p, xgb_model.predict_proba, num_features=5, num_samples=150)
            lime_j.append(jaccard(orig_lime_t, top_n_lime(exp_p)))

        shap_stability[nl].append(np.mean(shap_j))
        lime_stability[nl].append(np.mean(lime_j))

    print(f"SHAP={np.mean(shap_stability[nl]):.3f}  LIME={np.mean(lime_stability[nl]):.3f}")

print("Done.")
"""))

cells.append(new_code_cell("""\
shap_means = [np.mean(shap_stability[nl]) for nl in NOISE_LEVELS]
shap_stds  = [np.std(shap_stability[nl])  for nl in NOISE_LEVELS]
lime_means = [np.mean(lime_stability[nl]) for nl in NOISE_LEVELS]
lime_stds  = [np.std(lime_stability[nl])  for nl in NOISE_LEVELS]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('RQ2: Explanation Stability — Jaccard Similarity of Top-5 Features\\n'
             '(20 fraud instances, 10 perturbations each)',
             fontsize=13, fontweight='bold')

ax = axes[0]
x_pos = np.arange(len(NOISE_LEVELS))
w = 0.35
b1 = ax.bar(x_pos - w/2, shap_means, w, yerr=shap_stds, label='SHAP',
            color='#2196F3', alpha=0.85, capsize=5, ecolor='black')
b2 = ax.bar(x_pos + w/2, lime_means, w, yerr=lime_stds, label='LIME',
            color='#FF9800', alpha=0.85, capsize=5, ecolor='black')
ax.set_xticks(x_pos)
ax.set_xticklabels([f'sigma={nl}' for nl in NOISE_LEVELS])
ax.set_ylabel('Mean Jaccard Similarity')
ax.set_title('Stability by Noise Level', fontweight='bold')
ax.set_ylim(0, 1.18)
ax.axhline(1.0, color='k', ls='--', lw=0.8, alpha=0.3, label='Perfect')
ax.legend()
for bar, v in list(zip(b1, shap_means)) + list(zip(b2, lime_means)):
    ax.text(bar.get_x()+bar.get_width()/2, v+0.02, f'{v:.2f}', ha='center', fontsize=9)

ax = axes[1]
ax.errorbar(NOISE_LEVELS, shap_means, yerr=shap_stds,
            label='SHAP', color='#2196F3', marker='o', lw=2.5, capsize=5, markersize=9)
ax.errorbar(NOISE_LEVELS, lime_means, yerr=lime_stds,
            label='LIME', color='#FF9800', marker='s', lw=2.5, capsize=5, markersize=9)
ax.axhline(1.0, color='k', ls='--', lw=0.8, alpha=0.3)
ax.set_xlabel('Noise Level (sigma)')
ax.set_ylabel('Mean Jaccard Similarity')
ax.set_title('Stability vs. Noise', fontweight='bold')
ax.set_ylim(0, 1.1); ax.legend(); ax.grid(True, alpha=0.4)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '11_stability_analysis.png'), bbox_inches='tight', dpi=150)
plt.show()

print("Stability results (mean Jaccard +/- std):")
print(f"{'Method':6} | " + " | ".join(f"s={nl}" for nl in NOISE_LEVELS))
print(f"{'SHAP':6} | " + " | ".join(f"{m:.3f}+/-{s:.3f}" for m,s in zip(shap_means,shap_stds)))
print(f"{'LIME':6} | " + " | ".join(f"{m:.3f}+/-{s:.3f}" for m,s in zip(lime_means,lime_stds)))
"""))

cells.append(new_markdown_cell("### 7e. SHAP vs LIME Feature Agreement"))

cells.append(new_code_cell("""\
n_compare  = min(25, len(fraud_test_idx))
agreements = []
print(f"SHAP-LIME agreement on {n_compare} fraud instances...")

for i, idx in enumerate(fraud_test_idx[:n_compare]):
    x = X_test_s[idx]
    sv = explainer_xgb.shap_values(x.reshape(1, -1))[0]
    shap_top = top_n_shap(sv)
    exp = lime_explainer.explain_instance(x, xgb_model.predict_proba,
                                          num_features=5, num_samples=300)
    lime_top = top_n_lime(exp)
    agreements.append(jaccard(shap_top, lime_top))
    if (i + 1) % 5 == 0:
        print(f"  {i+1}/{n_compare}  running mean Jaccard = {np.mean(agreements):.3f}")

mean_agree = np.mean(agreements)
std_agree  = np.std(agreements)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(agreements, bins=10, range=(0, 1), color='#673AB7', edgecolor='white', alpha=0.85)
ax.axvline(mean_agree, color='red', lw=2, ls='--',
           label=f'Mean = {mean_agree:.3f} +/- {std_agree:.3f}')
ax.set_xlabel('Jaccard Similarity (SHAP top-5 vs LIME top-5)')
ax.set_ylabel('Count (fraud instances)')
ax.set_title('SHAP-LIME Feature Agreement', fontweight='bold')
ax.set_xlim(0, 1); ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '12_shap_lime_agreement.png'), bbox_inches='tight', dpi=150)
plt.show()

level = 'high' if mean_agree > 0.6 else 'moderate' if mean_agree > 0.4 else 'low'
print(f"Agreement: {mean_agree:.3f} +/- {std_agree:.3f}  ({level} consistency)")
"""))

# ---- 8. Summary -------------------------------------------------------------
cells.append(new_markdown_cell("## 8. Summary"))

cells.append(new_code_cell("""\
print("RQ1 — Model performance on imbalanced test set")
print(metrics_df[KEY_METRICS].round(4).to_string())
print()

best_f1  = metrics_df['F1'].idxmax()
best_pr  = metrics_df['PR-AUC'].idxmax()
print(f"Best F1:     {best_f1} ({metrics_df.loc[best_f1, 'F1']:.4f})")
print(f"Best PR-AUC: {best_pr} ({metrics_df.loc[best_pr, 'PR-AUC']:.4f})")
print()
print("Key findings:")
print("  - Rule-based has reasonable precision but misses a lot of fraud (low recall)")
print("  - LR improves recall considerably with SMOTE + class_weight=balanced")
print("  - XGBoost best overall — handles imbalance well and captures nonlinear patterns")
print("  - Neural network competitive, slight edge in some metrics depending on run")
print()
print("RQ2 — SHAP vs LIME stability")
for nl, sm, ss, lm, ls in zip(NOISE_LEVELS, shap_means, shap_stds, lime_means, lime_stds):
    winner = 'SHAP' if sm > lm else 'LIME'
    print(f"  sigma={nl}  SHAP={sm:.3f}+/-{ss:.3f}  LIME={lm:.3f}+/-{ls:.3f}  ({winner} more stable)")
print()
print(f"SHAP-LIME feature agreement: {mean_agree:.3f} +/- {std_agree:.3f}")
print()
shap_top5 = shap_imp_series.head(5).index.tolist()
print(f"Top fraud indicators (SHAP): {', '.join(shap_top5)}")
print()
print("Key findings:")
print("  - TreeSHAP is deterministic so it's consistently more stable than LIME")
print("  - LIME stability drops faster as noise increases, especially above sigma=0.10")
print("  - Both methods broadly agree on top features (V14, V4 dominate both)")
"""))

# Build notebook
nb = new_notebook(cells=cells)
nb['metadata'] = {
    'kernelspec': {
        'display_name': 'Python 3.11 (fraud detection)',
        'language': 'python',
        'name': 'fraud-detection-venv',
    },
    'language_info': {
        'name': 'python',
        'version': '3.11.9',
    },
}

out_path = r"C:\Users\metka\Desktop\FRAUD DETECTION\Fraud_Detection_Presentation.ipynb"
with open(out_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"Notebook written: {out_path}")
print(f"Cells: {len(cells)}")
