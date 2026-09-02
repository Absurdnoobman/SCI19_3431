import pandas as pd

order_reviews_dataset = pd.read_csv("./dataset/olist_order_reviews_dataset.csv")
orders_dataset = pd.read_csv("./dataset/olist_orders_dataset.csv")
order_items_dataset = pd.read_csv("./dataset/olist_order_items_dataset.csv")

orders_dataset['order_delivered_customer_date'] = pd.to_datetime(orders_dataset['order_delivered_customer_date'])
orders_dataset['order_estimated_delivery_date'] = pd.to_datetime(orders_dataset['order_estimated_delivery_date'])

orders_dataset = orders_dataset[orders_dataset['order_status'] == 'delivered']

orders_dataset.dropna(subset=['order_delivered_customer_date', 'order_estimated_delivery_date'], inplace=True)

orders_dataset['delay'] = (orders_dataset['order_delivered_customer_date'] - orders_dataset['order_estimated_delivery_date']).dt.days

orders_dataset['is_late'] = (orders_dataset['delay'] > 0).astype(int)

items_agg = order_items_dataset.groupby('order_id').agg(
    freight_value = ('freight_value', 'sum'),
    price = ('price', 'sum')
).reset_index()

# Cap price outliers at IQR bounds (per stated cleaning plan)
Q1 = items_agg['price'].quantile(0.25)
Q3 = items_agg['price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
items_agg['price'] = items_agg['price'].clip(lower=lower_bound, upper=upper_bound)

orders_dataset = orders_dataset.merge(items_agg, on= 'order_id')

# Impute missing review_score with the mean (per stated cleaning plan)
order_reviews_dataset['review_score'] = order_reviews_dataset['review_score'].fillna(
    order_reviews_dataset['review_score'].mean()
)

order_reviews_dataset['is_satisfied'] = (order_reviews_dataset['review_score'] >= 4).astype(int)

merged = pd.merge(orders_dataset, order_reviews_dataset, on= 'order_id')

merged.drop(columns= ['review_comment_title', 'review_comment_message'], inplace= True)

X = merged[['delay', 'is_late', 'freight_value', 'price']]
y = merged['is_satisfied']

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.3, random_state=67)

pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1_000, class_weight= 'balanced', random_state=67)
)

pipeline.fit(X_train, y_train)

y_predict = pipeline.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix

print(classification_report(y_test, y_predict, zero_division=0))
print(confusion_matrix(y_test, y_predict))