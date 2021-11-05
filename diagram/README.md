# Solução de problema de MLOps na GCP

Consideramos aqui um problema de MLOPs na Google Cloud Platform, em que um algoritmo de Machine Learning deve ser treinado a cada 4 semanas, gerando um novo modelo, ao mesmo tempo que é disponibilizado para o usuário uma classificação em tempo real baseada no último modelo gerado. Para solucionar este problema, escolhemos um determinado fluxo de ferramentas da GCP que cumpririam estas tarefas.

Segue abaixo o desenho completo da solução:

<p align="center">
  <img src="https://user-images.githubusercontent.com/68903879/139669005-4e311982-3990-4e9c-95b4-d188d62f8052.png">
</p>

## Treinamento do algoritmo de ML

A primeira etapa do Data Pipeline passa pelo **Cloud Pub/Sub**, um serviço de mensageria que irá receber o JSON de entrada de uma API. Depois, iremos guardar este JSON de entrada em um bucket do **Storage**. Ao salvarmos as mensagens do Pub/Sub no Storage, teremos arquivos resilientes que serão acumulados até o próximo treinamento do modelo, e além. Finalmente, para salvar a mensagem como um arquivo no Storage, precisamos do **Dataflow**, um serviço de gerenciamento de pipelines baseado no Apache Beam. Uma opção menos resiliente para guardar nossos dados seria utilizar o Cloud Datastore, que armazenaria nossos JSONs em um banco de dados NoSQL. Ao armazenarmos aqui, poderiamos perder resiliência, mas ganharíamos em performance.

Para executarmos o algoritmo de treinamento do modelo de ML, contaremos com o **Dataproc**. A partir do Dataproc, utilizaremos o SparkSQL para manipularmos o JSON de entrada para um .parquet — a extensão exigida para o treinamento do modelo. Depois disso, treinaremos o modelo utilizando o Pyspark (ainda no Dataproc), recebendo como input os arquivos de um determinado bucket do Storage, e criando como output o modelo de ML dentro de um diretório etiquetado com a atual data do treinamento. Estas etapas serão coordenadas por uma *managed cluster*, criada e encerrada durante um workflow job, gerada a partir de um Dataproc Workflow Template. O workflow job consistirá em uma DAG (*Directed Acyclic Graph*) que orquestrará todo os processos do Dataproc. Esta DAG será executada a cada 4 semanas e será disparada através de um cron especificado no **Cloud Scheduler**. Uma vez que este Scheduler estiver ativo, nosso Data Pipeline estará pronto para o treinamento do algoritmo.

## Classificação em tempo real

Para disponibilizarmos o modelo para classificação em tempo real, criaremos uma arquitetura serverless utilizando o **Cloud Functions**. Nesta arquitetura simples, o Pub/Sub invoca a função de forma assíncrona e recebe um JSON de saída já classificado pelo modelo de ML mais recente. Para permitir que esta API esteja altamente disponível, podemos aumentar o limite do número de instâncias pelo auto-scaling do Cloud Functions. Desta forma, nossa aplicação será escalável na medida necessária e nossos custos serão relacionados diretamente ao número de requisições da função.

Aqui, eu gostaria de questionar a escolha pelo **Apache Structured Streaming** neste contexto. Se iremos utilizar um modelo pré-treinado que se renova a cada quatro semanas, qual seria o sentido de utilizar uma operação de streaming como essa? Teoricamente, o Apache Structured Streaming seria muito útil se estivéssemos treinando o modelo continuamente, e não pré-treinado. Creio que uma simples Cloud Function alimentada pelo modelo mais recente seria suficiente. Caso optemos por usar Apache Structured Streaming de fato, então, poderíamos utilizar também o Cloud Datastore para melhor performance.
