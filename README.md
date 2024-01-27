# pred8tor
Pred8tor is a simple tool to clean up K8s objects that were tagged for expiration

### Push to Docker Registry:

```sh
docker buildx build --push --platform linux/arm64,linux/amd64  -t pavelzagalsky/pred8tor:1.0.0 -f Dockerfile .
```

## Description
pred8tor is an innovative open-source tool designed for maintaining clean and tidy Kubernetes environments. 

## Features
pred8tor identifies and removes expired Kubernetes objects using "expiration_time" label with a corresponding timestamp value.
it ensures the safe deletion of identified objects.

Installation
To install pred8tor, you can install it directly into your managed cluster running:

```shell
kubectl apply -f https://github.com/pavelzag/pred8tor/blob/master/deployment/pred8tor_deployment.yaml
```

bash
Copy code
pip install pred8tor
Alternatively, clone the repository and install the dependencies:

bash
Copy code
git clone https://github.com/yourusername/pred8tor.git
cd pred8tor
pip install -r requirements.txt
Usage
After installing pred8tor, you can start using it with the following command:

bash
Copy code
pred8tor [options]
Replace [options] with your desired parameters. For detailed usage instructions, refer to the Usage Documentation.

Configuration
pred8tor can be configured according to your Kubernetes environment needs. Edit the config.yaml file to set your preferences. For more details, refer to the Configuration Guide.

Contributing
We welcome contributions to pred8tor! If you have suggestions or improvements, please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -am 'Add some feature').
Push to the branch (git push origin feature-branch).
Create a new Pull Request.
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

License
This project is licensed under the MIT License - see the LICENSE.md file for details.

Acknowledgments
Mention any inspirations, code snippets, etc.
Acknowledge contributors and maintainers.
This template is just a starting point. You should customize it to fit your project's specific needs and characteristics. Including screenshots or demo videos can also be very helpful for users to understand how pred8tor works in action.