import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

df = pd.read_csv("data/feature_engineered_dataset.csv")

X = df.drop("risk_level", axis=1)
y = df["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

model = XGBClassifier(
    objective="multi:softprob",
    num_class = 3,
    n_estimators = 200,
    max_depth = 5,
    learning_rate = 0.1,
    subsample = 0.8,
    colsample_bytree = 0.8,
    random_state = 42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

scores = cross_val_score(model, X, y, cv=skf, scoring="accuracy")
print("CV Accuracy:", scores.mean())

joblib.dump(model, "data/trained_model.pkl")