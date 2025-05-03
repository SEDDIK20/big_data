# -*- coding: utf-8 -*-
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler

os.environ["LOKY_MAX_CPU_COUNT"] = "4"

def load_and_clean_data():
    try:
        file_path = "cleaned_data_500MB.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found in current directory")
        print("🔍 Loading and cleaning data...")
        chunksize = 100000
        chunks = []
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            chunk['event_time'] = pd.to_datetime(chunk['event_time'], errors='coerce')
            chunk.dropna(subset=['event_time', 'user_id', 'event_type', 'price'], inplace=True)
            chunk = chunk[chunk['price'] > 0]
            chunk.drop_duplicates(inplace=True)
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        os.makedirs("results", exist_ok=True)
        df.to_csv("results/cleaned_data.csv", index=False)
        print("✅ Data cleaned and saved to results/cleaned_data.csv")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

def exploratory_analysis(df):
    if df is None or df.empty:
        print("⚠️ No data to analyze")
        return
    print("\n🔍 Performing exploratory analysis...")
    file_size = os.path.getsize("results/cleaned_data.csv")
    file_size_mb = file_size / (1024 * 1024)
    file_size_gb = file_size / (1024 * 1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB ({file_size_gb:.2f} GB)")
    print("\n📊 Basic statistics:")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print("\nData types:")
    print(df.dtypes)
    print("\nUnique event types:")
    print(df['event_type'].unique())
    print("\nNumeric column stats:")
    print(df.describe())
    event_counts = df['event_type'].value_counts().to_dict()
    print("\n📊 Event type distribution:")
    for event, count in event_counts.items():
        print(f"{event}: {count:,} ({count/len(df)*100:.1f}%)")
    df['hour'] = df['event_time'].dt.hour
    purchase_hours = df[df['event_type'] == 'purchase']['hour'].value_counts().sort_index()
    purchase_hours.to_csv("results/purchase_hours.csv")
    print("\n📊 Purchases per hour:")
    print(purchase_hours)
    top_products = df[df['event_type'] == 'purchase']['product_id'].value_counts().nlargest(10)
    top_products.to_csv("results/top_products.csv")
    print("\n📊 Top 10 products:")
    print(top_products)
    top_categories = df[df['event_type'] == 'purchase']['category_code'].value_counts().nlargest(10)
    top_categories.to_csv("results/top_categories.csv")
    print("\n📊 Top 10 categories:")
    print(top_categories)
    plt.figure(figsize=(10, 6))
    sns.countplot(x='event_type', data=df, order=df['event_type'].value_counts().index)
    plt.title('Event Type Distribution')
    plt.xlabel('Event Type')
    plt.ylabel('Count')
    plt.savefig('results/event_distribution.png')
    plt.close()

def customer_segmentation(df):
    if df is None or df.empty:
        print("⚠️ No data for segmentation")
        return
    print("\n👥 Segmenting customers...")
    customer_activity = df.groupby('user_id').agg(
        total_purchases=('event_type', lambda x: (x == 'purchase').sum()),
        total_carts=('event_type', lambda x: (x == 'cart').sum()),
        total_views=('event_type', lambda x: (x == 'view').sum()),
        total_spent=('price', 'sum'),
        avg_price=('price', 'mean'),
        last_activity=('event_time', 'max')
    ).reset_index()
    current_date = df['event_time'].max()
    customer_activity['days_since_last_activity'] = (current_date - customer_activity['last_activity']).dt.days
    customer_activity.to_csv("results/customer_activity.csv", index=False)
    features = ['total_purchases', 'total_carts', 'total_views', 'total_spent', 'days_since_last_activity']
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(customer_activity[features])
    kmeans = KMeans(n_clusters=4, random_state=42)
    customer_activity['cluster'] = kmeans.fit_predict(scaled_features)
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='total_spent', y='total_purchases', hue='cluster', 
                    data=customer_activity, palette='viridis', alpha=0.6)
    plt.title('Customer Segmentation')
    plt.xlabel('Total Spent')
    plt.ylabel('Total Purchases')
    plt.savefig('results/customer_segmentation.png')
    plt.close()
    cluster_summary = customer_activity.groupby('cluster').agg(
        avg_purchases=('total_purchases', 'mean'),
        avg_carts=('total_carts', 'mean'),
        avg_views=('total_views', 'mean'),
        avg_spent=('total_spent', 'mean'),
        avg_days_inactive=('days_since_last_activity', 'mean'),
        count=('user_id', 'count')
    ).reset_index()
    cluster_summary.to_csv("results/cluster_summary.csv", index=False)
    print("\n📊 Cluster summary:")
    print(cluster_summary)

def build_models():
    try:
        df = pd.read_csv("results/cleaned_data.csv")
    except:
        print("❌ Cannot load cleaned data")
        return
    print("\n🤖 Building models...")
    df['event_time'] = pd.to_datetime(df['event_time'], errors='coerce')
    customer_activity = df.groupby('user_id').agg(
        total_purchases=('event_type', lambda x: (x == 'purchase').sum()),
        total_carts=('event_type', lambda x: (x == 'cart').sum()),
        total_views=('event_type', lambda x: (x == 'view').sum()),
        total_spent=('price', 'sum'),
        last_activity=('event_time', 'max')
    ).reset_index()
    customer_activity['has_purchased'] = customer_activity['total_purchases'].apply(lambda x: 1 if x > 0 else 0)
    features = ['total_carts', 'total_views', 'total_spent']
    X = customer_activity[features]
    y = customer_activity['has_purchased']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42, n_estimators=100)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📊 Classification model accuracy: {accuracy:.2f}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))
    y = customer_activity['total_purchases']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    models = {
        "Random Forest": RandomForestRegressor(random_state=42, n_estimators=100),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42, n_estimators=100),
        "XGBoost": XGBRegressor(random_state=42, n_estimators=100),
        "LightGBM": LGBMRegressor(random_state=42, verbose=-1,  n_estimators=100)
    }
    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        results.append({"Model": name, "RMSE": rmse})
        print(f"📊 {name}: RMSE = {rmse:.2f}")
    pd.DataFrame(results).to_csv("results/model_results.csv", index=False)

if __name__ == "__main__":
    print("🚀 Starting e-commerce data analysis...")
    df = load_and_clean_data()
    exploratory_analysis(df)
    customer_segmentation(df)
    build_models()
    print("\n✅ All analyses completed successfully!")
    print("📁 Saved files:")
    print("- results/cleaned_data.csv")
    print("- results/customer_activity.csv")
    print("- results/cluster_summary.csv")
    print("- results/top_products.csv")
    print("- results/top_categories.csv")
    print("- results/model_results.csv")
    print("- results/customer_segmentation.png")
    print("- results/event_distribution.png")
