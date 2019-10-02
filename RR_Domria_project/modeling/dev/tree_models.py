import sqlalchemy as db
import pandas as pd
import time
import re
from sklearn.preprocessing import LabelEncoder
from catboost import Pool, CatBoostRegressor
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

engine = db.create_engine(f'postgresql://bogdanivanyuk:bogdanivanyuk@localhost:5431/flats_data')
connection = engine.connect()
metadata = db.MetaData()
flat_info = db.Table('flat_info', metadata, autoload=True, autoload_with=engine)
announcement_info = db.Table('announcement_info', metadata, autoload=True, autoload_with=engine)

# getting flat_info data
query_flat_info = connection.execute(db.select([flat_info]))
df_flat_info = pd.DataFrame(query_flat_info)
df_flat_info.columns = query_flat_info.keys()

# getting announcement_info data
query_announcement_info = connection.execute(db.select([announcement_info]))
df_announcement_info = pd.DataFrame(query_announcement_info)
df_announcement_info.columns = query_announcement_info.keys()

# merging two columns and dropping useless columns
data = pd.merge(df_announcement_info, df_flat_info, on='flat_id')
data = data.drop(['flat_id','page_url', 'image_urls', 'description','street_name', 'verified', 'title'], axis = 1)

# data preprocessing 
data['year_of_construction'] = data['year_of_construction'].apply(lambda x: re.findall(r'\b\d+\b',str(x))[0] 
                                                                  if len(re.findall(r'\b\d+\b',str(x))) != 0 else -1)

# detecting outliers
data = data.drop(data[(data['price_usd'] > 1000000) | (data['total_area'] > 600) | (data['living_area'] > 200) | (data['kitchen_area'] > 100) | (data['floor'] > 40) | 
                          (data['number_of_rooms'] > 6)].index)

target = data['price_usd']
data = data.drop(['price_usd', 'price_uah', 'date_created'], axis=1)

# =========================CATBOOST=========================
# train_test_split
start_time = time.time()
train_pool = Pool(data, target, cat_features=['type_of_proposal',  'city_name', 'heating_type', 'walls_type'])

# specify the training parameters 
model_catboost = CatBoostRegressor(iterations=10, 
                          depth=16, 
                          learning_rate=1, 
                          loss_function='RMSE')
#train the model
model_catboost.fit(train_pool)
model_catboost.save_model('cat_boost_model')
print('Catboost time: '+str(time.time() - start_time))
# =========================DECISION_TREE=========================
start_time = time.time()
# filter categorical columns
categorical_cols = ['type_of_proposal', 'city_name', 'heating_type', 'walls_type'] 

# preparing data for Decision Tree model
le = LabelEncoder()
data[categorical_cols] = data[categorical_cols].apply(lambda col: le.fit_transform(col))
# initialize DecisionTree model
dtr = DecisionTreeRegressor(random_state=42, max_depth=10, min_samples_leaf = 1)
# fit model
dtr.fit(data, target)
# saving model weights
dump(dtr, 'decision_tree_model.joblib') 
print('Decision Tree time: '+str(time.time() - start_time))











