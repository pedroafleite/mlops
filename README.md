# MLOps no GCP: Tutorial passo-a-passo

<p align="center">
  <img src="https://user-images.githubusercontent.com/68903879/139669005-4e311982-3990-4e9c-95b4-d188d62f8052.png">
</p>

Para uma breve explicação da solução, [clique aqui](https://github.com/pedroafleite/mlops_exercise/tree/main/diagram).

## Pré-requisitos:
- Anaconda instalado.
- Google Cloud SDK Shell instalado.

## Criando um ambiente virtual

Primeiramente, seguiremos boas práticas se criarmos uma virtualenv. Esta virtualenv terá Python 3.8 (downgrade da versão atual 3.9), que será necessária para rodar alguns recursos mais para frentes. Como possuo Anaconda no meu computador, posso facilmente executar estes passos com:

`conda create -n "venv" python=3.8.0 ipython`

Podemos verificar se a nova venv foi criada junto às demais com:

`conda env list`

E ativar a venv que acabamos de criar com:

`conda activate venv`

## Configurações iniciais e permissões

Dentro do Google Cloud SDK Shell, podemos acessar nossa conta através de:

`gcloud auth login` 

Iremos criar uma nova conta com uma PROJECT_ID distinta. O Google Cloud irá recomendar algumas IDs disponíveis. No nosso caso, utilizamos a PROJECT_ID **mlops-1635587444840** (Este não é um projeto existente, apenas um exemplo. Em projetos que serão enviados para produção, as variáveis devem ser propriamente escondidas através da declaração de variáveis de ambientes.)

`gcloud projects create mlops-1635587444840`

Com projeto criado, iremos criar uma nova service account, aonde designaremos as permissões necessárias para acessar os serviços. Então, criaremos uma service account chamada **service-mlops-1382162467** com um display name **service-mlops**.

`gcloud iam service-accounts create service-mlops-1382162467 --description="service account for mlops exercise" --display-name="service-mlops"`

Podemos visualizar todas as service accounts criadas:

`gcloud iam service-accounts list`

Aqui, designamos à conta de serviço nossas políticas de acesso. Assim, criaremos roles de admin para o PubSub, Storage, Dataflow, Dataproc e Cloud Functions, que serão as ferramentas utilizadas neste tutorial:

`gcloud projects add-iam-policy-binding mlops-1635587444840 --member="serviceAccount:service-mlops-1382162467@mlops-1635587444840.iam.gserviceaccount.com" --role="roles/pubsub.admin"`

`gcloud projects add-iam-policy-binding mlops-1635587444840 --member="serviceAccount:service-mlops-1382162467@mlops-1635587444840.iam.gserviceaccount.com" --role="roles/storage.admin"`

`gcloud projects add-iam-policy-binding mlops-1635587444840 --member="serviceAccount:service-mlops-1382162467@mlops-1635587444840.iam.gserviceaccount.com" --role="roles/dataflow.admin"`

`gcloud projects add-iam-policy-binding mlops-1635587444840 --member="serviceAccount:service-mlops-1382162467@mlops-1635587444840.iam.gserviceaccount.com" --role="roles/dataproc.admin"`

`gcloud projects add-iam-policy-binding mlops-1635587444840 --member="serviceAccount:service-mlops-1382162467@mlops-1635587444840.iam.gserviceaccount.com" --role="roles/cloudfunctions.admin"`

Em um teste como o nosso, podemos escolher uma role bastante abrangente (no caso, admin), ou até mesmo mais abrangente do que isso (owner, por exemplo). No entanto, em projetos que seguirão para a produção, é importante restringirmos ao máximo o papel das roles de cada service account para tornar o app seguro. Agora, criamos um json com as credenciais para acessarmos os serviços:

`gcloud iam service-accounts keys create mlops-485cf5c206db.json --iam-account=service-mlops-1382162467@$mlops-1635587444840.iam.gserviceaccount.com` 

Este json deve estar propriamente escondido atrás do [.gitignore](https://github.com/pedroafleite/mlops_exercise/blob/main/.gitignore), já que estamos compartilhando este repositório no Github.

## Treinamento do algoritmo de ML

### Preparando o Storage

Vamos criar um novo bucket no Storage com o nome **ml_input**:

`gsutil mb gs://ml_input`

### Configurando o PubSub

Dentro da venv, instale as dependências do PubSub para acessá-lo no Python:

`pip install --upgrade google-cloud-pubsub`

Crie um novo tópico chamado **topic-brigade**:

`gcloud pubsub topics create topic-brigade`

E uma subscrição à este tópico chamada **sub-brigade**:

`gcloud pubsub subscriptions create sub-brigade --topic topic-brigade`

A subscrição não é necessária para o fluxo do pipeline, mas pode ser utilizada para debuggar o fluxo de dados até esta etapa.

### Configurando o Dataflow

Instale as dependências:

`pip install apache_beam[gcp]`

Permita que sua conta instale apitools e certifique-se que a API do Dataflow está ativa.

Com [pubsub_gcs.py](https://github.com/pedroafleite/mlops_exercise/blob/main/pubsub_gcs.py), iremos executar o Dataflow:

`python pubsub_gcs.py --project=mlops-1635587444840 --region=us-central1 --input_topic=projects/mlops-1635587444840/topics/topic-brigade --output_path=gs://ml_input/samples/output --runner=DataflowRunner --window_size=2 --num_shards=1 --temp_location=gs://ml_input/temp`

As configurações de windows size e número de shards podem ser modificadas para melhor performance. Para estes valores autoescalarem, remova estas variáveis da linha de comando. Para uma boa ilustração prática de windowning (que nada mais é do que uma janela deslizante que analisa dados vizinhos em microbatches, um por um), veja [este tutorial](https://cloud.google.com/architecture/using-apache-spark-dstreams-with-dataproc-and-pubsub). Já sharding significa que os dados serão particionados e processados paralelamente pelo Spark. Um número de shards igual a 1 significa que este processamento paralelo não ocorrerá.

### Criando uma nova cluster submetendo um job no Dataproc

Inicializaremos uma nova cluster chamada **brigade-cluster**:

`gcloud dataproc clusters create brigade-cluster --project=mlops-1635587444840 --region=us-central1 --single-node`

Submetemos o job do Pyspark que irá executar o `train_ml_model.py`. 

`gcloud dataproc jobs submit pyspark train_ml_model.py --cluster=brigade-cluster --region=us-central1 -- gs://ml_input/input/ gs://ml_output/output/`

Designamos os diretórios do Storage de input e output, mas dentro do script, ainda determinamos um subdiretório para salvar os modelos. Os subdiretórios serão dinamicamente nomeados com a data em que ocorreu o treinamento, no formato doc-classification-model-YYYY-MM-DD. Além disso, ao executar `train_ml_model`, executamos também a dependência `spark_sql.py`, importada no arquivo anterior, que faz a transformação do arquivo json recebido no input do PubSub para um .parquet. que será lido pelo modelo de ML.

### Executando a pipeline de treinamento

...

## Classificação em tempo real

...

[Em construção...]