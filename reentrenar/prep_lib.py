import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
def build_raw(path="data.csv", drop_status=True):
    df = pd.read_csv(path, encoding="latin1")
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'], errors='coerce')
    cols_pii = ['Customer Email','Customer Password','Customer Fname','Customer Lname','Customer Street']
    cols = (cols_pii+['Product Status','Product Description','Order Zipcode','Delivery Status','Days for shipping (real)','Product Image',
        'Category Id','Customer Id','Department Id','Order Customer Id','Order Id','Order Item Cardprod Id','Order Item Id','Product Card Id','Product Category Id','Customer Zipcode',
        'Order City','Order State','Customer City','Product Name','Latitude','Longitude',
        'Benefit per order','Order Item Product Price','Sales','Order Item Total','Sales per customer'])
    d = df.drop(columns=cols)
    d['order_year']=d['order date (DateOrders)'].dt.year; d['order_month']=d['order date (DateOrders)'].dt.month; d['order_dayofweek']=d['order date (DateOrders)'].dt.dayofweek
    d = d.drop(columns=['order date (DateOrders)','shipping date (DateOrders)'])
    def cap(s):
        q1,q3=s.quantile(.25),s.quantile(.75); i=q3-q1; return s.clip(q1-1.5*i,q3+1.5*i)
    for c in ['Order Item Discount','Order Item Profit Ratio','Order Item Quantity','Order Profit Per Order','Product Price']: d[c]=cap(d[c])
    if drop_status: d=d.drop(columns=['Order Status'])
    return df, d
