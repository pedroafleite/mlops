import pandas as pd
import json
from pyspark.sql import SparkSession

def json_into_parquet():
    spark = SparkSession.builder.getOrCreate()

    with open('samples_output-20_06-20_08-1') as f:
        lines = f.readlines()        
    lines = lines[:-1]
    lines.append("}")

    with open('samples_output-20_06-20_08-1.json', 'w') as f:
        for item in lines:
            f.write("%s\n" % item)

    with open('samples_output-20_06-20_08-1.json', 'r') as f2:
        data = json.loads(f2.read())
        print(data)

    list_tags = data['doc']['metadata']['otherTags']
    d = [] # lista para iterar elementos de otherTags
    for i in range(len(list_tags)):
        a = data['doc']['metadata']['otherTags'][i]['tagName']
        b = data['doc']['metadata']['otherTags'][i]['tagValue']
        c = a + ':' + b
        d.append(c)        
    other_tags = '|'.join(d) # concatenar strings de otherTags
    
    pandas_df = pd.DataFrame({
        'eventTimestamp': [data['eventTimestamp']],
        'eventSource': [data['eventSource']],
        'eventType': [data['eventType']],
        'eventVersion': [data['eventVersion']],
        'accountId': [data['doc']['metadata']['accountId']],
        'superTag01': [data['doc']['metadata']['superTag01']],
        'superTag02': [data['doc']['metadata']['superTag02']],
        'concatOtherTags': [other_tags],
        'payload': [data['doc']['payload']]
    })
    df = spark.createDataFrame(pandas_df)
    df.write.parquet("output/proto.parquet")
    