#!/usr/bin/env python
# coding: utf-8

import batch as batch

options=batch.localstack_check()

# original df
original_df = batch.read_data("s3://russian-trade/RUStoWorldTrade_2007.pkl", options=options)

# test df
batch.save_data(original_df, "s3://russian-trade/test_write_df_train.pkl", options=options)
test_df = batch.read_data("s3://russian-trade/test_write_df_train.pkl", options=options)

wrong_df = batch.read_data("s3://russian-trade/RUStoWorldTrade_2008.pkl", options=options)

print("test_DF", test_df.info())

print("original DF", original_df.info())


def test_integration():
    assert original_df.equals(test_df)

