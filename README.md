# Ribograph

<a href="https://github.com/hakanozadam/ribograph"><img width="30%" src="https://github.com/hakanozadam/ribograph/blob/main/docs/ribograph_logo.png" alt="RiboGraph"></a>
<br>
Interactive browser for Ribo Files.

**RiboGraph** has been tested on Firefox and Safari.

## Local Development

To build the container:
```
docker compose -f Docker/docker-compose_local.yml build
```

To run the container:
```
docker compose -f Docker/docker-compose_local.yml up
```


If you're running into permission issues and being forced to run with sudo, [you might need to add yourself to the docker user group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

## Reference Compatibility

When an experiment is created in the system, an md5 hash sum of the reeference of that experiment is also
stored as an attribute of the experiment. This hash sum is obtained by computing the md5 sum of the string S1 + S2, where `+` stands for string concatanation. **S1** is the concatanation of the transcript names in the ribo file in the existing order and
**S2** is the concatanation of the corresponding transcript lengths. The names and lengths are separated by `,` in concatanation.

The references of two experiments are called comptaible if the hash sum of their references are the same. In practice, this means that
the two experiments are coming from the same transcriptomic reference and therefore their coverages can be viewed together.

Reference hash sum is an experiment attribute and it is stored in the `reference_digest` attribute.

### Linting and formatting
To reformat python files
```
black .
```

To lint template files
```
djlint .
```

To reformat template files
```
djlint . --reformat
```

