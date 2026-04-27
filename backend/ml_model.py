from sklearn.ensemble import IsolationForest
import pandas as pd

def detect_anomalies(df):
    if df.empty or len(df) < 4:
        return pd.DataFrame(), []

    features = df.groupby('paid_by').agg(
        total_spent=('amount', 'sum'),
        avg_expense=('amount', 'mean'),
        num_expenses=('amount', 'count'),
        max_expense=('amount', 'max')
    ).reset_index()

    X = features[['total_spent', 'avg_expense', 'num_expenses', 'max_expense']]
    model = IsolationForest(contamination=0.2, random_state=42)
    features['anomaly'] = model.fit_predict(X)
    features['score'] = model.score_samples(X)
    flagged = features[features['anomaly'] == -1]['paid_by'].tolist()
    return features, flagged

from sklearn.cluster import KMeans

def get_spending_personality(df):
    if df.empty or len(df['paid_by'].unique()) < 2:
        return "Not enough data for personality profiles. Add expenses for at least two people."
        
    features = df.groupby('paid_by').agg(
        total_spent=('amount', 'sum'),
        avg_expense=('amount', 'mean'),
        num_expenses=('amount', 'count')
    ).reset_index()
    
    X = features[['total_spent', 'avg_expense', 'num_expenses']]
    n_clusters = min(len(features), 3)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    features['cluster'] = kmeans.fit_predict(X)
    
    profiles = []
    for _, row in features.iterrows():
        profiles.append(f"- {row['paid_by']}: Total Rs {row['total_spent']:.0f} | Avg Rs {row['avg_expense']:.0f} | Count: {row['num_expenses']} | Cluster ID: {row['cluster']}")
        
    return "\n".join(profiles)
