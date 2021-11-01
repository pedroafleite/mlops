# Solução de problema de MLOps na GCP

Consideramos aqui um problema de MLOPs na Google Cloud Platform, em que um algoritmo de Machine Learning deve ser treinado a cada 4 semanas, gerando um novo modelo, ao mesmo tempo que é disponibilizado para o usuário uma classificação em tempo real baseada no último modelo gerado. Para solucionar este problema, escolhemos um determinado fluxo de ferramentas da GCP que cumpririam estas tarefas. Neste documento, justificaremos estas escolhas.

Segue abaixo o desenho completo da solução:

<p align="center">
  <img src="https://user-images.githubusercontent.com/68903879/139666648-954c4024-239c-4bd3-ab78-71c429599fe4.png">
</p>

## Treinamento do algoritmo de ML

Começaremos pelo lado esquerdo da figura acima, justificando as etapas de treinamento do algoritmo de Machine Learning.

A primeira etapa do Data Pipeline passa pelo **Cloud Pub/Sub**, um serviço de mensageria que irá receber o JSON de entrada de uma API. Depois, iremos guardar este JSON de entrada em um bucket do **Storage**. Ao salvarmos as mensagens do Pub/Sub no Storage, teremos arquivos resilientes que serão acumulados até o próximo treinamento do modelo, e além. Finalmente, para salvar a mensagem como um arquivo no Storage, precisamos do **Dataflow**, um serviço de gerenciamento de pipelines baseado no Apache Beam.

Para executarmos o algoritmo de treinamento do modelo de ML (`train_ml_model.py`), contaremos com o **Dataproc**. A partir do Dataproc, utilizaremos o SparkSQL para manipularmos o JSON de entrada para um .parquet — a extensão exigida para o treinamento do modelo. Estas etapas serão coordenadas por uma *managed cluster*, que é criada e encerrada durante um workflow job, gerada a partir de um Dataproc Workflow Template. O workflow job consistirá em uma DAG (*Directed Acyclic Graph*) que orquestrará todo os processos do Dataproc. Esta DAG será executada a cada 4 semanas e será disparada através de um cron especificado no **Cloud Scheduler**. Uma vez que este Scheduler estiver ativo, nosso Data Pipeline estará pronto.

## Classificação em tempo real

Para disponibilizarmos o modelo para classificação em tempo real, criaremos utilizaremos uma arquitetura serverless utilizando o **Cloud Functions**. Nesta arquitetura simples, o Pub/Sub invoca a função de forma assíncrona e recebe um JSON de saída já classificado pelo modelo de ML mais recente disponível. Para permitir que esta API esteja altamente disponível independentemente do número de requisições, podemos aumentar o número de instâncias desta função disponíveis pelo auto-scaling do Cloud Functions. Desta forma, nossa aplicação será escalável na medida necessária e nossos custos serão correlacionados diretamente pelas requisições feitas no aplicativo.