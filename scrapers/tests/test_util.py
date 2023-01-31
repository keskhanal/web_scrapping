import pytest
import util
import pandas as pd


def test_save_to_s3():
    bucket_name = "terma-dealflow"
    prefix = "testdealflow"

    df = pd.DataFrame([{'a':1}])
    uri = util.save_to_s3("TESTMARKET", df, bucket_name, prefix)
    print(uri)
    df = pd.read_json(uri, lines=True)
    assert df.iloc[0]['a'] == 1
