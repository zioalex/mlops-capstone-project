#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
from datetime import datetime

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error

import xgboost as xgb



def localstack_check():
    # S3_ENDPOINT_URL = "http://localhost:4566"
    if os.getenv("S3_ENDPOINT_URL"):
        options = {"client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT_URL")}}
        print("Using Localstack")
    else:
        options = {}
        print("Using AWS")
    return options
  

def read_data(filename, options={}):
    df = pd.read_pickle(filename, storage_options=options)

    return df


def save_data(df, output_file, options={}):
    result = df.to_pickle(
        output_file, storage_options=options
    )
    print(f"save_data {result}")


def optimize_df(df):
    usecols=['Year','Aggregate Level','Reporter ISO','Partner','Partner ISO','Commodity Code','Commodity','Qty Unit','Qty','Netweight (kg)','Trade Value (US$)']
    dataframe = df.convert_dtypes()

    # Optimize DF memory consumption
    for col in dataframe.columns:
      if dataframe[col].dtype == 'Float64':
        dataframe[col] = dataframe[col].astype('float16')
    try :
        if dataframe[col].dtype == 'Int64':
            dataframe[col] = dataframe[col].astype('int16')
    except :
        dataframe[col] = dataframe[col].astype('float16')
    dataframe.drop(dataframe[dataframe['Commodity Code'] == 'TOTAL'].index, inplace=True)
    dataframe['Commodity Code'] = dataframe['Commodity Code'].astype('float16')

    return dataframe
 

def data_enrichment(dataframe, storage_options={}, filename='s3://russian-trade/iso3.csv'):
    df = dataframe[dataframe['Aggregate Level']==2]
    iso = pd.read_csv(filename, storage_options=storage_options)
    iso.drop(axis=1, columns=['FIPS','ISO (2)','ISO (No)','Internet','Note','Capital'], inplace=True)

    continents = ['Asia', 'Europe', 'Africa', 'Oceania', 'Americas']
    for x in continents:
        y = iso[iso['Continent'] == x]
        m = df['Partner ISO'].isin(y['ISO (3)'])
        df.loc[m, 'Continent'] = x

    Region = ['South Asia', 'South East Europe', 'Northern Africa', 'Pacific',
        'South West Europe', 'Southern Africa', 'West Indies',
        'South America', 'South West Asia', 'Central Europe',
        'Eastern Europe', 'Western Europe', 'Central America',
        'Western Africa', 'South East Asia', 'Central Africa',
        'North America', 'East Asia', 'Indian Ocean', 'Northern Europe',
        'Eastern Africa', 'Southern Europe', 'Central Asia',
        'Northern Asia']

    for x in Region:
        y = iso[iso['Region'] == x]
        m = df['Partner ISO'].isin(y['ISO (3)'])
        df.loc[m, 'Region'] = x

    return df
  
def prepare_df(df_train, df_valid):
    categorical = ['Partner ISO', 'Commodity Code']
    numerical = ['Year']

    # Available years 2007 - 2020
    # df_train = df.loc[(df['Year']>=2007) & (df['Year']<=2015)]
    # df_valid = df.loc[(df['Year']>=2016) & (df['Year']<=2020)]

    #df = read_dataset(2008) -
    # I must convert to str otherwise the DV fail. Explain why?

    dv = DictVectorizer()
    target = 'Trade Value (US$)'

    # Prepare train data
    df_train[categorical] = df_train[categorical].astype(str)
    train_dicts = df_train[categorical + numerical].to_dict(orient='records')
    X_train = dv.fit_transform(train_dicts)
    y_train = df_train[target].values

    # Prepare validation data
    df_valid[categorical] = df_valid[categorical].astype(str)
    valid_dicts = df_valid[categorical + numerical].to_dict(orient='records')
    X_val = dv.transform(valid_dicts)
    y_val = df_valid[target].values

    return X_train, X_val, y_train, y_val, dv

   
def main():
    options=localstack_check()
    df_train = read_data("s3://russian-trade/RUStoWorldTrade_2007.pkl", options=options)
    df_valid = read_data("s3://russian-trade/RUStoWorldTrade_2008.pkl", options=options)
    
    print(df_train.info(), df_valid.info())
    save_data(df_train, "s3://russian-trade/test_write_df_train.pkl", options=options )  
    X_train, X_val, y_train, y_val, dv = prepare_df(df_train, df_valid) #.result()
    
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_val)

    mse = mean_squared_error(y_val, y_pred, squared=False)
    print("Mean Squared Error:", mse)
    #   optimized_df = optimize_df(df)
    #   print(optimized_df.info())
    #   enriched_df = data_enrichment(df, storage_options=options)
    #   print(enriched_df.info())
    
    print('predicted mean trade:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['Partner ISO'] = df_valid['Partner ISO']
    df_result['Commodity Code'] = df_valid['Commodity Code']
    df_result['predicted_trade'] = y_pred

    print(df_result.head())
    save_data(df_result, "s3://russian-trade/batch_result.pkl", options=options)
  
   
if __name__ == '__main__':
  main()