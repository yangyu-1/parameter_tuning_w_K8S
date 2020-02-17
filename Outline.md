## Parameter Tuning with Kubernetes
In this tutorial we'll use Kubernetes to start a cluster to speed up our parameter tuning tasks. If you're a data scientist wondering what Kubernetes (K8s) is, I hope this tutorial will server as a good starting point.

The ML task at hand is a simple regression problem using the [california housing dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_california_housing.html). We'll do parameter tuning across 3 packages: XGBoost, CatBoost,and LightGBM.  

This tutorial will be using Google Cloud Platform. This is mostly because at the time of writing (Feb, 2020), GCP has the best sign-up promotional credit, $300.

Prior Knowledge: Accessing APIs via Python and doing simple parameter tuning should be familiar to you, as well as knowledge of Docker, Numpy, Pandas, Scikit-learn, and one of the following: XGBoost, CatBoost, or LightGBM. Some knowledge of message queues, Google Cloud Platform (GCP), and mongoDB would be helpful but not necessary. No prior knowledge of Kubernetes is assumed, although for the pacing of the videos, I will sometimes relegate detail explanations and additional resources for K8s to the blog post.   

Disclaimer: This tutorial is a contrived example attempting demonstrate Kubernetes. In reality, there are other solutions that will do parameter tuning more [efficiently](https://optuna.org/) and [easier](https://dask.org/). If your goal is to tune parameters, you should try those first. 

#### Overview
Here is our overall structure:

1. Producer: The producer generates the parameter tuning tasks from param grids, and send the tasks to the message queue. Each tasks contains the specific parameters needed for training. We'll use a Jupyter Notebook to send the tasks. 
   - Kubernetes Resources used: None

2. Message Queue: The message queue sits between the producer and the workers. The message queue holds all the tasks passed in by the producer, and workers read the message off the queue and to do the processing. There are numerous message queue technologies, including Kafka, redis-queue, and RabbitMQ. Hosted solutions include GCP Pub/Sub and many others. In this tutorial, we'll host our own RabbitMQ using Kubernetes.
   - Kubernetes Resources used: Deployment, Service

3. Workers: Workers reads messages from message queue. Each message contains a specific model parameter. Workers then builds regression models with the parameters (eg. search_depth = 3, or num_leaves = 50), and calculates a result mean. Finally, the worker saves the result to our mongoDB database, and sends back an acknowledgement to the MQ to signal task completion before starting on the next task.
   - Kubernetes Resources used: Deployment with specific resource constraints, ConfigMap 

4. Database: Database is where results from workers are stored. There are plenty of open source and hosted database technologies. Here we'll host our own mongoDB, since it requires very little set up in order to save data.
   - Kubernetes Resources used: PersistentVolume, PersistentVolumeClaim, ReplicaSet, Service  

5. Front-end (Optional): An simple flask front end app that connects to our mongoDB database
   - Kubernetes Resources used: Deployment, Service (NodePort)
  
6. AutoScaler (Optional): #TODO 
