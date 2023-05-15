# filmemo
A movie emoji party game where users have to guess the movie name from emojis
Game Link: http://filmemo.techtuft.com

### Setting up and running docker

```shell
docker build -t platput/filmemo:1.0.0 .
docker create \
   -e OPENAI_API_KEY=<actual openai api key> \
   -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/g-secret.json \
   -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/g-secret.json:ro \
   --name filmemo -p8081:8080 platput/filmemo 
```

### Testing
```shell
poetry run coverage run -m pytest . && coverage report -m
```

### CI/CD
- Before setting up the github action, 
  - the openai api key should be set in github secrets
  - gcp credentials file should exist in the ec2 instance
  - the path to credential file should be set under the env key `GOOGLE_APPLICATION_CREDENTIALS`
- There will be 2 set of tags `ui-release-1.0.0` and `api-release-1.0.0`
  - upon a new tag like ui-v only ui action will be triggered
  - upon a new tag like api-v only api action will be triggered
