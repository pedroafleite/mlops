# Solução de problema de MLOps na GCP

Consideramos aqui um problema de MLOPs na Google Cloud Platform, em que um algoritmo de Machine Learning deve ser treinado a cada 4 semanas, gerando um novo modelo, ao mesmo tempo que é disponibilizado para o usuário uma classificação em tempo real baseada no último modelo gerado. Para solucionar este problema, escolhemos um determinado fluxo de ferramentas da GCP que cumpririam estas tarefas. Neste documento, justificaremos estas escolhas.

Segue abaixo o desenho completo da solução:

<p align="center">
  <img src="https://user-images.githubusercontent.com/68903879/139598908-fe0bba9c-7d6a-4824-8a8e-60596d8ae364.png">
</p>

## Treinamento do algoritmo de ML

Começaremos pelo lado esquerdo da figura acima, justificando as etapas de treinamento do algoritmo de Machine Learning.

Consideraremos a primeira ferramenta do Data Pipeline como o **Cloud Pub/Sub**, um serviço de mensageria que iria receber o JSON de entrada de uma API. Depois, iremos guardar este JSON de entrada em um bucket do **Storage**. Ao salvarmos as mensagens do Pub/Sub no Storage, teremos arquivos resilientes que serão acumulados até o próximo treinamento do modelo, e além. 

Para salvar o arquivo de um lugar para outro, precisamos do **Dataflow**, um serviço de gerenciamento de pipelines baseado no Apache Beam. 

Para orquestrarmos todo esse processo para ser executado automaticamente a cada 4 semanas, criaremos um cron job utilizando o **Cloud Scheduler**. Tecnicamente, este seria o primeiro passo a ser executado no Data Pipeline, já que coordena o disparo de todos os próximos passos. No entanto, é uma etapa que exige que o resto do fluxo já esteja pronto para execução.