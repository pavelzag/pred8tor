# pred8tor
Pred8tor is a simple tool to clean up K8s objects that were tagged for expiration

### Push to Docker Registry:

```sh
docker buildx build --push --platform linux/arm64,linux/amd64  -t pavelzagalsky/pred8tor:1.0.0 -f Dockerfile .
```