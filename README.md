# RiboGraph
 
<a href="https://github.com/hakanozadam/ribograph"><img width="30%" src="https://github.com/hakanozadam/ribograph/blob/main/docs/ribograph_logo.png" alt="RiboGraph"></a>
 
RiboGraph is is an interactive web-based tool for browsing ribosome profiling data. As its input, it takes [ribo files](https://ribopy.readthedocs.io/en/latest/ribo_file_format.html) that have been generated using [riboflow](https://github.com/ribosomeprofiling/riboflow) and uploaded via the browser. RiboGraph belongs to a [software ecosystem](https://ribosomeprofiling.github.io/) designed to work with ribosome profiling data.
 
Ribograph can deliver at a glance visualizations of QC information, such as read length distributions, region counts, and metagene plots, as well as in depth coverage plots for each gene.
 
 
**RiboGraph** has been tested on Firefox and Safari.
 
## Installation (Local Development)
RiboGraph requires [Docker](https://docs.docker.com/install/).
Here is a [tutorial for installing it on Ubuntu.](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
 
RiboGraph runs entirely within a Docker container, and local development should happen within this running container. All other dependencies, including required Python packages and Node.js, are installed inside the container.
 
To build the container:
```
docker compose -f Docker/docker-compose_local.yml build
```
 
To run the container:
```
docker compose -f Docker/docker-compose_local.yml up
```
 
If you're running into permission issues and being forced to run with sudo, [you might need to add yourself to the docker user group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
 
### Linting and formatting
We use black to format Python files and djlint to format Django templates.
 
To reformat python files:
```
black .
```
 
To lint template files:
```
djlint .
```
 
To reformat template files:
```
djlint . --reformat
```
 
## Deployment
...

## Usage
After the docker instance is started, on first time use you will be prompted to create an admin user account. After this, you'll be able to add other users through the admin panel, as well as add projects and references.

### QC Plots
...

### Coverage Plots
...

### P Site Correction
Users can select offsets for P Site Correction for each read length. These offsets can then be used for the coverage plot. Offsets for each experiment are kept in the user's browser local storage.

### References
...

## Implementation Notes
RiboGraph is implemented as a Django web app that uses Vue supplementally to provide reactivity on the front-end. During development, both the Django dev server and the hot reloading Vue dev server are run in parallel. During production, the Vue files are built into static assets that are served through Django. This logic is implemented in the [vue_app](ribograph/browser/templates/browser/vue_app.html) Django template.
 
### Django HTTPS API
The Vue app interfaces with the Django backend through [a series of HTTPS APIs](ribograph/browser/api.py). These APIs provide the front-end with the data required to render the charts. Results are cached for around 10 minutes for faster results and a smoother user experience.
 
### Reference Compatibility
 
When an experiment is created in the system, an md5 hash sum of the reference of that experiment is also
stored as an attribute of the experiment. This hash sum is obtained by computing the md5 sum of the string S1 + S2, where `+` stands for string concatenation. **S1** is the concatenation of the transcript names in the ribo file in the existing order and
**S2** is the concatenation of the corresponding transcript lengths. The names and lengths are separated by `,` in concatenation.
 
The references of two experiments are called compatible if the hash sum of their references are the same. In practice, this means that
the two experiments are coming from the same transcriptomic reference and therefore their coverages can be viewed together.
 
Reference hash sum is an experiment attribute and it is stored in the `reference_digest` attribute.
 
