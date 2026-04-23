"""
نموذج التعلم الآلي للتنبؤ باستهلاك الكهرباء 2026
هيئة الهلال الأحمر السعودي
"""

import pandas as pd
import numpy as np
import warnings
import os
import json
import pickle
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import xgboost as xgb
warnings.filterwarnings('ignore')

OUTPUT_DIR = "/home/ubuntu/srca_electricity"

# ============================
# 1. تحميل البيانات المعالجة
# ============================
print("=" * 60)
print("المرحلة 1: تحميل البيانات المعالجة")
print("=" * 60)

df = pd.read_csv(os.path.join(OUTPUT_DIR, "SRCA_Electricity_Data.csv"))
df['Date'] = pd.to_datetime(df['Date'])
print(f"إجمالي السجلات: {len(df):,}")
print(f"السنوات: {sorted(df['Year'].unique())}")

# ============================
# 2. هندسة الميزات
# ============================
print("\n" + "=" * 60)
print("المرحلة 2: هندسة الميزات")
print("=" * 60)

# الاستخدام على مستوى الحساب الفرعي الشهري
df_monthly = df.groupby(['Contract_Account', 'Collective_CA', 'Year', 'Month']).agg(
    Consumption_kWh=('Consumption_kWh', 'sum'),
    Bill_Amount=('Bill_Amount', 'sum'),
    Region_City=('Region_City', 'first'),
    Region_Major=('Region_Major', 'first'),
    Account_Category=('Account_Category', 'first')
).reset_index()

df_monthly['Date'] = pd.to_datetime(
    df_monthly['Year'].astype(str) + '-' + df_monthly['Month'].astype(str).str.zfill(2) + '-01'
)
df_monthly.sort_values(['Contract_Account', 'Date'], inplace=True)
df_monthly.reset_index(drop=True, inplace=True)

print(f"السجلات الشهرية: {len(df_monthly):,}")

# ============================
# 3. إنشاء الميزات الزمنية والإحصائية
# ============================
print("\n" + "=" * 60)
print("المرحلة 3: إنشاء الميزات")
print("=" * 60)

# ترميز الفئات
le_region = LabelEncoder()
le_ca = LabelEncoder()
le_account = LabelEncoder()

df_monthly['Region_encoded'] = le_region.fit_transform(df_monthly['Region_Major'].fillna('غير محدد'))
df_monthly['CA_encoded'] = le_ca.fit_transform(df_monthly['Collective_CA'].astype(str))
df_monthly['Account_encoded'] = le_account.fit_transform(df_monthly['Contract_Account'].astype(str))

# ميزات موسمية
df_monthly['sin_month'] = np.sin(2 * np.pi * df_monthly['Month'] / 12)
df_monthly['cos_month'] = np.cos(2 * np.pi * df_monthly['Month'] / 12)

# ميزة الفصل
season_map = {1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3, 12: 0}
df_monthly['Season_num'] = df_monthly['Month'].map(season_map)

# ميزة الربع
df_monthly['Quarter_num'] = ((df_monthly['Month'] - 1) // 3) + 1

# ميزة السنة النسبية (للتعامل مع الاتجاه)
df_monthly['Year_rel'] = df_monthly['Year'] - 2024

# ميزات الإبطاء (Lag Features) - على مستوى الحساب
df_monthly_sorted = df_monthly.sort_values(['Contract_Account', 'Date'])

# إبطاء 12 شهر (نفس الشهر من السنة الماضية)
df_monthly_sorted['lag_12'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].shift(12)
# إبطاء 6 أشهر
df_monthly_sorted['lag_6'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].shift(6)
# إبطاء 3 أشهر
df_monthly_sorted['lag_3'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].shift(3)
# إبطاء شهر واحد
df_monthly_sorted['lag_1'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].shift(1)

# المتوسط المتحرك (Rolling Mean)
df_monthly_sorted['rolling_mean_3'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].transform(
    lambda x: x.shift(1).rolling(3, min_periods=1).mean()
)
df_monthly_sorted['rolling_mean_6'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].transform(
    lambda x: x.shift(1).rolling(6, min_periods=1).mean()
)
df_monthly_sorted['rolling_std_3'] = df_monthly_sorted.groupby('Contract_Account')['Consumption_kWh'].transform(
    lambda x: x.shift(1).rolling(3, min_periods=1).std()
).fillna(0)

# متوسط الاستهلاك التاريخي للحساب
account_avg = df_monthly_sorted[df_monthly_sorted['Year'] < 2026].groupby('Contract_Account')['Consumption_kWh'].mean()
df_monthly_sorted['account_avg'] = df_monthly_sorted['Contract_Account'].map(account_avg)

# متوسط الاستهلاك حسب الشهر والحساب
month_account_avg = df_monthly_sorted[df_monthly_sorted['Year'] < 2026].groupby(
    ['Contract_Account', 'Month']
)['Consumption_kWh'].mean().reset_index()
month_account_avg.columns = ['Contract_Account', 'Month', 'month_account_avg']
df_monthly_sorted = df_monthly_sorted.merge(month_account_avg, on=['Contract_Account', 'Month'], how='left')

df_monthly = df_monthly_sorted.copy()

print(f"الميزات المنشأة: {len(df_monthly.columns)} عمود")

# ============================
# 4. إعداد بيانات التدريب والاختبار
# ============================
print("\n" + "=" * 60)
print("المرحلة 4: إعداد بيانات التدريب والاختبار")
print("=" * 60)

feature_cols = [
    'Month', 'Year_rel', 'Quarter_num', 'Season_num',
    'sin_month', 'cos_month',
    'Region_encoded', 'CA_encoded', 'Account_encoded',
    'lag_1', 'lag_3', 'lag_6', 'lag_12',
    'rolling_mean_3', 'rolling_mean_6', 'rolling_std_3',
    'account_avg', 'month_account_avg'
]

# بيانات التدريب: 2024 و 2025
train_data = df_monthly[df_monthly['Year'].isin([2024, 2025])].copy()
# بيانات الاختبار: الربع الأول 2026 (الفعلي)
test_data = df_monthly[df_monthly['Year'] == 2026].copy()

# إزالة الصفوف التي تحتوي على قيم ناقصة في الميزات
train_data_clean = train_data.dropna(subset=feature_cols + ['Consumption_kWh'])
test_data_clean = test_data.dropna(subset=feature_cols + ['Consumption_kWh'])

print(f"بيانات التدريب: {len(train_data_clean):,} سجل")
print(f"بيانات الاختبار (Q1 2026): {len(test_data_clean):,} سجل")

X_train = train_data_clean[feature_cols]
y_train = train_data_clean['Consumption_kWh']
X_test = test_data_clean[feature_cols]
y_test = test_data_clean['Consumption_kWh']

# ============================
# 5. تدريب النماذج
# ============================
print("\n" + "=" * 60)
print("المرحلة 5: تدريب النماذج")
print("=" * 60)

# نموذج XGBoost
xgb_model = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1
)

# نموذج Random Forest
rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=8,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

# نموذج Gradient Boosting
gb_model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    min_samples_split=10,
    subsample=0.8,
    random_state=42
)

# تدريب النماذج
print("تدريب XGBoost...")
xgb_model.fit(X_train, y_train)

print("تدريب Random Forest...")
rf_model.fit(X_train, y_train)

print("تدريب Gradient Boosting...")
gb_model.fit(X_train, y_train)

# ============================
# 6. تقييم النماذج
# ============================
print("\n" + "=" * 60)
print("المرحلة 6: تقييم النماذج")
print("=" * 60)

def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)  # لا نريد قيم سالبة
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100
    
    print(f"\n{model_name}:")
    print(f"  RMSE: {rmse:,.2f} كيلوواط/ساعة")
    print(f"  MAE:  {mae:,.2f} كيلوواط/ساعة")
    print(f"  R²:   {r2:.4f}")
    print(f"  MAPE: {mape:.2f}%")
    
    return {'model_name': model_name, 'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape, 'predictions': y_pred}

results = {}
results['XGBoost'] = evaluate_model(xgb_model, X_test, y_test, 'XGBoost')
results['RandomForest'] = evaluate_model(rf_model, X_test, y_test, 'Random Forest')
results['GradientBoosting'] = evaluate_model(gb_model, X_test, y_test, 'Gradient Boosting')

# اختيار أفضل نموذج بناءً على R²
best_model_name = max(results, key=lambda k: results[k]['r2'])
print(f"\nأفضل نموذج: {best_model_name} (R² = {results[best_model_name]['r2']:.4f})")

# ============================
# 7. التنبؤ بالأرباع الثاني والثالث والرابع 2026
# ============================
print("\n" + "=" * 60)
print("المرحلة 7: التنبؤ بالأرباع الثاني والثالث والرابع 2026")
print("=" * 60)

# الحسابات الفرعية الموجودة في 2026
accounts_2026 = df_monthly[df_monthly['Year'] == 2026]['Contract_Account'].unique()
print(f"عدد الحسابات الفرعية في 2026: {len(accounts_2026)}")

# إنشاء بيانات للأشهر 4-12 من 2026
future_months = list(range(4, 13))
future_records = []

for account in accounts_2026:
    account_data = df_monthly[df_monthly['Contract_Account'] == account].sort_values('Date')
    
    # آخر بيانات متاحة
    last_known = account_data.tail(1).iloc[0]
    
    # متوسط الاستهلاك التاريخي
    hist_avg = account_data[account_data['Year'] < 2026]['Consumption_kWh'].mean()
    
    # متوسط الاستهلاك حسب الشهر
    month_avgs = account_data[account_data['Year'] < 2026].groupby('Month')['Consumption_kWh'].mean()
    
    for month in future_months:
        record = {
            'Contract_Account': account,
            'Collective_CA': last_known['Collective_CA'],
            'Year': 2026,
            'Month': month,
            'Region_Major': last_known['Region_Major'],
            'Region_City': last_known.get('Region_City', ''),
            'Account_Category': last_known['Account_Category'],
            'Region_encoded': last_known['Region_encoded'],
            'CA_encoded': last_known['CA_encoded'],
            'Account_encoded': last_known['Account_encoded'],
            'sin_month': np.sin(2 * np.pi * month / 12),
            'cos_month': np.cos(2 * np.pi * month / 12),
            'Season_num': season_map[month],
            'Quarter_num': ((month - 1) // 3) + 1,
            'Year_rel': 2026 - 2024,
            'account_avg': hist_avg if not np.isnan(hist_avg) else 0,
            'month_account_avg': month_avgs.get(month, hist_avg) if not np.isnan(hist_avg) else 0
        }
        
        # حساب قيم الإبطاء
        # lag_12: نفس الشهر من 2025
        lag12_data = account_data[(account_data['Year'] == 2025) & (account_data['Month'] == month)]
        record['lag_12'] = lag12_data['Consumption_kWh'].values[0] if len(lag12_data) > 0 else hist_avg
        
        # lag_6: 6 أشهر قبل
        lag6_month = month - 6
        lag6_year = 2026 if lag6_month > 0 else 2025
        lag6_month = lag6_month if lag6_month > 0 else lag6_month + 12
        lag6_data = account_data[(account_data['Year'] == lag6_year) & (account_data['Month'] == lag6_month)]
        record['lag_6'] = lag6_data['Consumption_kWh'].values[0] if len(lag6_data) > 0 else hist_avg
        
        # lag_3: 3 أشهر قبل
        lag3_month = month - 3
        lag3_year = 2026 if lag3_month > 0 else 2025
        lag3_month = lag3_month if lag3_month > 0 else lag3_month + 12
        lag3_data = account_data[(account_data['Year'] == lag3_year) & (account_data['Month'] == lag3_month)]
        record['lag_3'] = lag3_data['Consumption_kWh'].values[0] if len(lag3_data) > 0 else hist_avg
        
        # lag_1: الشهر السابق
        lag1_month = month - 1
        lag1_year = 2026 if lag1_month > 0 else 2025
        lag1_month = lag1_month if lag1_month > 0 else 12
        lag1_data = account_data[(account_data['Year'] == lag1_year) & (account_data['Month'] == lag1_month)]
        record['lag_1'] = lag1_data['Consumption_kWh'].values[0] if len(lag1_data) > 0 else hist_avg
        
        # rolling means
        recent_data = account_data.tail(6)['Consumption_kWh']
        record['rolling_mean_3'] = recent_data.tail(3).mean() if len(recent_data) >= 3 else hist_avg
        record['rolling_mean_6'] = recent_data.mean() if len(recent_data) >= 6 else hist_avg
        record['rolling_std_3'] = recent_data.tail(3).std() if len(recent_data) >= 3 else 0
        
        # معالجة القيم الناقصة
        for key in ['lag_12', 'lag_6', 'lag_3', 'lag_1', 'rolling_mean_3', 'rolling_mean_6']:
            if np.isnan(record[key]):
                record[key] = hist_avg if not np.isnan(hist_avg) else 0
        
        future_records.append(record)

df_future = pd.DataFrame(future_records)
print(f"سجلات التنبؤ المستقبلية: {len(df_future):,}")

# التنبؤ باستخدام أفضل نموذج
best_model = {'XGBoost': xgb_model, 'RandomForest': rf_model, 'GradientBoosting': gb_model}[best_model_name]

X_future = df_future[feature_cols].fillna(0)
df_future['Predicted_Consumption'] = np.maximum(best_model.predict(X_future), 0)

print(f"إجمالي الاستهلاك المتوقع (Q2-Q4 2026): {df_future['Predicted_Consumption'].sum():,.0f} كيلوواط/ساعة")

# ============================
# 8. تجميع نتائج التنبؤ الكاملة لـ 2026
# ============================
print("\n" + "=" * 60)
print("المرحلة 8: تجميع نتائج التنبؤ الكاملة")
print("=" * 60)

# الربع الأول الفعلي
q1_actual = df_monthly[df_monthly['Year'] == 2026][
    ['Contract_Account', 'Collective_CA', 'Year', 'Month', 'Consumption_kWh',
     'Region_Major', 'Region_City', 'Account_Category']
].copy()
q1_actual['Type'] = 'فعلي'
q1_actual['Predicted_Consumption'] = q1_actual['Consumption_kWh']

# الربع الأول المتوقع (للمقارنة)
q1_pred = test_data_clean[['Contract_Account', 'Collective_CA', 'Year', 'Month', 'Consumption_kWh',
                             'Region_Major', 'Region_City', 'Account_Category']].copy()
q1_pred['Predicted_Consumption'] = np.maximum(best_model.predict(X_test), 0)
q1_pred['Type'] = 'متوقع (Q1 مقارنة)'

# الأرباع المستقبلية
df_future_save = df_future[['Contract_Account', 'Collective_CA', 'Year', 'Month', 
                              'Region_Major', 'Region_City', 'Account_Category', 'Predicted_Consumption']].copy()
df_future_save['Consumption_kWh'] = np.nan
df_future_save['Type'] = 'متوقع'

# دمج الكل
df_2026_full = pd.concat([q1_actual, df_future_save], ignore_index=True)
df_2026_full['Date'] = pd.to_datetime(
    df_2026_full['Year'].astype(str) + '-' + df_2026_full['Month'].astype(str).str.zfill(2) + '-01'
)

# إجماليات شهرية
monthly_2026 = df_2026_full.groupby(['Year', 'Month', 'Type']).agg(
    total_actual=('Consumption_kWh', 'sum'),
    total_predicted=('Predicted_Consumption', 'sum')
).reset_index()

print("إجماليات 2026 الشهرية:")
print(monthly_2026.to_string())

# إجمالي 2026 المتوقع
total_2026_predicted = df_2026_full['Predicted_Consumption'].sum()
print(f"\nإجمالي الاستهلاك المتوقع لعام 2026: {total_2026_predicted:,.0f} كيلوواط/ساعة")

# ============================
# 9. التحليلات الذكية
# ============================
print("\n" + "=" * 60)
print("المرحلة 9: التحليلات الذكية")
print("=" * 60)

# أعلى وأقل حسابات استهلاكاً في 2026
ca_2026 = df_2026_full.groupby('Collective_CA')['Predicted_Consumption'].sum().sort_values(ascending=False)
print("أعلى 5 حسابات تجميعية استهلاكاً في 2026:")
print(ca_2026.head(5))
print("\nأقل 5 حسابات تجميعية استهلاكاً في 2026:")
print(ca_2026.tail(5))

# معدل النمو المتوقع
total_2024 = df_monthly[df_monthly['Year'] == 2024]['Consumption_kWh'].sum()
total_2025 = df_monthly[df_monthly['Year'] == 2025]['Consumption_kWh'].sum()
growth_2024_2025 = (total_2025 - total_2024) / total_2024 * 100
print(f"\nمعدل النمو 2024→2025: {growth_2024_2025:.2f}%")

# مقارنة Q1 الفعلي مع المتوقع
q1_actual_total = q1_actual['Consumption_kWh'].sum()
q1_pred_total = q1_pred['Predicted_Consumption'].sum()
q1_accuracy = (1 - abs(q1_actual_total - q1_pred_total) / q1_actual_total) * 100
print(f"دقة التنبؤ للربع الأول 2026: {q1_accuracy:.1f}%")
print(f"  الفعلي: {q1_actual_total:,.0f} كيلوواط/ساعة")
print(f"  المتوقع: {q1_pred_total:,.0f} كيلوواط/ساعة")

# ============================
# 10. حفظ النتائج
# ============================
print("\n" + "=" * 60)
print("المرحلة 10: حفظ النتائج")
print("=" * 60)

# حفظ نتائج التنبؤ
df_2026_full.to_csv(os.path.join(OUTPUT_DIR, "SRCA_2026_Predictions.csv"), 
                     index=False, encoding='utf-8-sig')

# حفظ مقارنة Q1
q1_comparison = test_data_clean[['Contract_Account', 'Collective_CA', 'Year', 'Month', 
                                   'Consumption_kWh', 'Region_Major', 'Account_Category']].copy()
q1_comparison['Predicted_Consumption'] = np.maximum(best_model.predict(X_test), 0)
q1_comparison['Error'] = q1_comparison['Consumption_kWh'] - q1_comparison['Predicted_Consumption']
q1_comparison['Error_Pct'] = abs(q1_comparison['Error']) / (q1_comparison['Consumption_kWh'] + 1e-10) * 100
q1_comparison.to_csv(os.path.join(OUTPUT_DIR, "SRCA_Q1_2026_Comparison.csv"), 
                      index=False, encoding='utf-8-sig')

# حفظ مقاييس التقييم
metrics = {
    'best_model': best_model_name,
    'models': {
        name: {
            'rmse': float(res['rmse']),
            'mae': float(res['mae']),
            'r2': float(res['r2']),
            'mape': float(res['mape'])
        }
        for name, res in results.items()
    },
    'q1_accuracy': float(q1_accuracy),
    'total_2024': float(total_2024),
    'total_2025': float(total_2025),
    'total_2026_predicted': float(total_2026_predicted),
    'growth_2024_2025': float(growth_2024_2025)
}

with open(os.path.join(OUTPUT_DIR, "model_metrics.json"), 'w', encoding='utf-8') as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

# حفظ النموذج
with open(os.path.join(OUTPUT_DIR, "best_model.pkl"), 'wb') as f:
    pickle.dump(best_model, f)

# حفظ المشفرات
encoders = {'region': le_region, 'ca': le_ca, 'account': le_account}
with open(os.path.join(OUTPUT_DIR, "encoders.pkl"), 'wb') as f:
    pickle.dump(encoders, f)

print("تم حفظ جميع الملفات:")
print(f"  - SRCA_2026_Predictions.csv")
print(f"  - SRCA_Q1_2026_Comparison.csv")
print(f"  - model_metrics.json")
print(f"  - best_model.pkl")

print("\n" + "=" * 60)
print("اكتمل بناء النموذج بنجاح!")
print("=" * 60)
print(f"\nملخص النتائج:")
print(f"  - أفضل نموذج: {best_model_name}")
print(f"  - R²: {results[best_model_name]['r2']:.4f}")
print(f"  - RMSE: {results[best_model_name]['rmse']:,.2f}")
print(f"  - MAE: {results[best_model_name]['mae']:,.2f}")
print(f"  - دقة Q1 2026: {q1_accuracy:.1f}%")
print(f"  - إجمالي الاستهلاك المتوقع 2026: {total_2026_predicted:,.0f} كيلوواط/ساعة")
