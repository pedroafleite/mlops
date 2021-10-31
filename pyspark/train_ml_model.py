import spark_sql
import datetime

# Transformar json em parquet para alimentar algoritmo de ML:
# spark_sql.json_into_parquet()

"""
Treinamento de modelo de ML
"""

# Salvar modelo em uma pasta específica:
# model.save(f'doc-classification-model-{datetime.datetime.now():%Y-%m-%d}/model_generator_dropout_augmenepoch5.h5')
