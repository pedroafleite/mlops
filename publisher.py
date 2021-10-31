from google.cloud import pubsub_v1
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="mlops-485cf5c206db.json"

# TODO(developer)
project_id = "mlops-1635587444840"
topic_id = "topic-brigade"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

data = """{
   "eventTimestamp":"2019-04-02T21:55:57Z",
   "eventId":"3dc6eb9af4154635b688e7cfeb8db131bfe84ccd",
   "eventSource":"doc.contract",
   "eventVersion":"1.0",
   "eventType":"DocSchedule",
   "doc":{
      "schemaVersion":"1.0",
      "docId":"CF2909E5-12C8-4D42-A996-12672B727B3B",
      "metadata":{
         "accountId":"EA2425CF-EF72-40C6-8DD3-C7D5310FA07D",
         "superTag01":"A",
         "superTag02":"C",
         "otherTags":[
            {
               "tagName":"otherTag01",
               "tagValue":"A"
            },
            {
               "tagName":"otherTag02",
               "tagValue":"X"
            }
         ]
      },
      "payload":"texto teste"
   }
}
"""
# Data must be a bytestring
data = data.encode("utf-8")
# When you publish a message, the client returns a future.
future = publisher.publish(topic_path, data)
print(future.result())

print(f"Published messages to {topic_path}.")
