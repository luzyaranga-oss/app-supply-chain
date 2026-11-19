import sys, time, json, joblib, numpy as np, pandas as pd
sys.path.insert(0,'.')
from prep_lib import build_raw
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, BaggingClassifier, AdaBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

_, d = build_raw('data.csv', drop_status=True)
target='Late_delivery_risk'
cols_cat=['Type','Market','Customer Segment','Shipping Mode','Department Name','Customer Country','Order Region','Category Name','Order Country','Customer State']
cols_num=[c for c in d.columns if c not in cols_cat+[target]]
X=d.drop(columns=[target]); y=d[target]
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
prep=ColumnTransformer([("num",StandardScaler(),cols_num),("cat",OneHotEncoder(handle_unknown="infrequent_if_exist",min_frequency=0.01,sparse_output=False),cols_cat)])
cp=lambda m: Pipeline([("prep",clone(prep)),("clf",m)])
dt=lambda: DecisionTreeClassifier(max_depth=12,min_samples_leaf=1,random_state=42)
MODELS={
 "adaboost_arbol_FINAL": lambda: cp(AdaBoostClassifier(estimator=dt(),n_estimators=50,learning_rate=1.0,random_state=42)),
 "regresion_logistica": lambda: cp(LogisticRegression(max_iter=2000,random_state=42,C=0.01)),
 "arbol_decision": lambda: cp(dt()),
 "bagging_arbol": lambda: cp(BaggingClassifier(estimator=dt(),n_estimators=50,bootstrap=True,random_state=42,n_jobs=1)),
 "svm_muestra15000": lambda: cp(SVC(kernel="rbf",C=1,gamma="scale",probability=True,random_state=42)),
 "gradient_boosting": lambda: cp(GradientBoostingClassifier(learning_rate=0.1,n_estimators=200,max_depth=5,random_state=42)),
 "random_forest": lambda: cp(RandomForestClassifier(n_estimators=200,max_depth=16,min_samples_leaf=1,random_state=42,n_jobs=1)),
}
if __name__=="__main__":
    for name in sys.argv[1:]:
        t0=time.time(); m=MODELS[name]()
        if name.startswith("svm"):
            Xs,_,ys,_=train_test_split(Xtr,ytr,train_size=15000,stratify=ytr,random_state=42); m.fit(Xs,ys)
        else: m.fit(Xtr,ytr)
        p=m.predict_proba(Xte)[:,1]; pr=m.predict(Xte)
        r=dict(modelo=name,accuracy=accuracy_score(yte,pr),precision=precision_score(yte,pr),recall=recall_score(yte,pr),f1=f1_score(yte,pr),roc_auc=roc_auc_score(yte,p),segundos=round(time.time()-t0))
        joblib.dump(m,f'modelo/{name}.joblib',compress=3)
        json.dump(r,open(f'datos/test_{name}.json','w'))
        print(r,flush=True)
