# Pred8tor
Pred8tor is a simple tool to clean up K8s objects that were tagged for expiration.

![Pred8tor Logo](documentation/pred8tor_logo.png)

## Description
Pred8tor is an innovative open-source Python based tool designed for maintaining clean and tidy Kubernetes environments. 
To trigger Pred8tor's action simply add similar label to a Kubernetes object:

```shell
kubectl label pods ubuntu expiration_time=1706255118
```

This will set the expiration time for the labeled object to the mentioned epoch time which is:
`Saturday, January 27, 2024 11:29:50 AM`
When that time arrives, Pred8tor will terminate this specific pod object.

At the moment, Pred8tor allows termination of the following objects: [deployment, pod, namespace, service] and more to come!

## Features
Pred8tor identifies and removes expired Kubernetes objects using "expiration_time" label with a corresponding timestamp value.
it ensures the safe deletion of identified objects.

## Installation
To install Pred8tor, you can clone the repository and run the following command from project's root:

```shell
kubectl apply -f deployment/pred8tor_deployment.yaml
```

## Developing
Pred8tor is free for use and contribution.
In order to contribute please do the following:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes.
4. Commit your changes (git commit -am 'Add some feature').
5. Push to the branch (git push origin feature-branch).
6. Create a new Pull Request and tag me for a review

# Running locally
Running Pred8tor locally is very simple!
1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Create a new Python virtual env:
```shell
python3 -m venv pred8tor_venv
```
4. Step into the created directory and install the requirements:
```shell
pip3 install -r Pred8tor/app/requirements.txt
```
5. Start working!

License
This project is licensed under the Apache 2 License - see the LICENSE.md file for details.
