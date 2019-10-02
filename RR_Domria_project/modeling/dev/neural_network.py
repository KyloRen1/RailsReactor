import sqlalchemy as db
import pandas as pd
import time
import re

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
data = data.drop(['page_url', 'image_urls', 'description','street_name', 'verified', 'title'], axis = 1)

# data preprocessing 
data['year_of_construction'] = data['year_of_construction'].apply(lambda x: re.findall(r'\b\d+\b',str(x))[0] 
                                                                  if len(re.findall(r'\b\d+\b',str(x))) != 0 else -1)

# detecting outliers
data = data.drop(data[(data['price_usd'] > 1000000) | (data['total_area'] > 600) | (data['living_area'] > 200) | (data['kitchen_area'] > 100) | (data['floor'] > 40) | 
                          (data['number_of_rooms'] > 6)].index)

target = data['price_usd']
data = data.drop(['price_usd', 'price_uah', 'date_created'], axis=1)











