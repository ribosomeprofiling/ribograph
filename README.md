# RiboGraph
 
<a href="https://github.com/ribosomeprofiling/ribograph"><img width="30%" src="https://github.com/ribosomeprofiling/ribograph/raw/main/docs/ribograph_logo.png" alt="RiboGraph"></a>
 
RiboGraph is is an interactive web-based tool for browsing ribosome profiling data. As input, it takes [ribo files](https://ribopy.readthedocs.io/en/latest/ribo_file_format.html) that are generated using [Riboflow](https://github.com/ribosomeprofiling/riboflow) and uploaded via the browser. RiboGraph belongs to a [software ecosystem](https://ribosomeprofiling.github.io/) designed to work with ribosome profiling data.
 
Ribograph can deliver at a glance visualizations of QC information, such as read length distributions, region counts, and metagene plots, as well as in depth coverage plots for each gene.
 
 
**RiboGraph** has been tested on Firefox and Safari and usage of these browsers are highly encouraged for RiboGraph.

---
 
## Installation
RiboGraph requires [Docker](https://docs.docker.com/install/). Here is a [tutorial for installing it on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04). If you're running into permission issues and being forced to run with sudo, [you might need to add yourself to the docker user group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
 
RiboGraph runs entirely within a Docker container, and local development should happen within this running container. All other dependencies, including required Python packages and Node.js, are installed inside the container.

First, clone this repository.
```
git clone https://github.com/ribosomeprofiling/ribograph.git
```

Go to the Docker folder.

```
cd ribograph/Docker/
```

Make sure that the docker-compose file is in the working folder.
```
ls docker-compose_local.yml
```
 
Build the container. This may take a while.
```
docker compose -f docker-compose_local.yml build
```
 
Once the container is ready, you can run the container.
```
docker compose -f docker-compose_local.yml up
```

We recommend using <a href="https://www.mozilla.org/">Firefox</a> for Ribograph. <a href="https://www.mozilla.org/">
<img width="5%" src="https://github.com/ribosomeprofiling/ribograph/raw/main/docs/Firefox_logo,_2019.svg" alt="Firefox"></a>

On your browser, go to the URL: [http://localhost:8000/](http://localhost:8000/). 
If the container is built succesfully, you should see a welcome prompt asking you to create a username and password.

![Welcome Screen](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/welcome.jpg?raw=true)
 

---

## Usage

After the docker instance is started, on first time use you will be prompted to create an admin user account. After this, login and you'll be able to add other users through the admin panel, as well as add projects and references.

### Adding a Project

Click on the "+" icon on the bottom right.

![Add New Project](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/add_project.jpg?raw=true)

Fill out the form. You can leave description box empty.

![New Project Form](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/project_creation_form.jpg?raw=true)

### Upload Ribo File

Upload your ribo file. If you don't have any, you can download a sample file: [GSM3323389.ribo](https://github.com/ribosomeprofiling/ribograph_sampledata/raw/main/human/GSM3323389.ribo). After you select your file and upload, the system will ask you to select experiments and confirm.

![Ribo File Upload](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/ribo_file_upload.jpg?raw=true)

### QC Plots

Click on the experiment name to go to the QC page.
![Go to QC](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/go_to_qc.jpg?raw=true)

You can use the slider to view a range of ribosome footprints.
![QC Page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/qc_page.jpg?raw=true)


### Coverage Plots

For individual transcripts, you can view the ribosome footprint coverage.

![Go to coverage](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/go_to_coverage.jpg?raw=true)

You can select transcripts or search them and see their coverage.

![Coverage page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/coverage_page.jpg?raw=true)

### P-Site Correction
Users can select offsets for P-Site Correction for each read length. These offsets can then be used for the coverage plot. Offsets for each experiment are kept in the user's browser local storage.

![Go to offsets](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/go_to_offsets.jpg?raw=true)

You can adjust the offset of each footprint length. Then you can save the offsets to use in the coverage.

![Offsets](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/offset_page.jpg?raw=true)

![Using gOffsets](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/use_offsets.jpg?raw=true)

You can also auto-initialize reasonable offset values using the "Auto-Init" button. This will align the max value from [-18, -6] on the start site metagene plot to 0 for every read length. Note that these values still need to be saved before they can take effect on the coverage plot.

### Adding References

To be able to view nucelotide sequences in the coverage plot, you need to associate the experiment with a reference.

![Reference Page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/reference_page.jpg?raw=true)

Reference files must be gzipped fasta files with the "`fa.gz`" extension. If you have the reference file you used for the ribo file, upload it, or if you downloaded and used the sample ribo file `GSM3323389.ribo`, then [download the corresponding refeerence file here](https://github.com/ribosomeprofiling/ribograph_sampledata/raw/main/human/appris_human_v2_selected.fa.gz).

Upload the reference file and give a name to this entry.
![Reference Page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/upload_reference.jpg?raw=true)

Go back to the coverage page and match the experiment with the reference uploaded.

![Reference Page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/select_reference.jpg?raw=true)

Click on the "Sequence" to view the nucleotide sequences.

![Reference Page](https://github.com/ribosomeprofiling/ribograph/raw/main/docs/screenshots/view_nucleotides.jpg?raw=true)

### Gene Correlation Viewer
Select "Open Gene Correlation" from a project page to open the gene correlation viewer. On the left will be a scatterplot comparing the gene frequencies in two different experiments. On the right will be a heatmap displaying the Speaman correlation of gene frequencies between each experiment and every other compatible experiment. By clicking on any cell in this heatmap, the corresponding scatterplot will be displayed to the left.

Experiments are grouped by compatibility as determined by their reference digest (See Reference Compatibility for more information). If multiple compatible groups of experiments are available in a project, the gene correlation page will allow you to select between them.

### UCSC Genome Database Integration
By right clicking on a gene name in the coverage search list or on a point in the gene correlation plot, you can open that gene's entry in the UCSC Genome Database. To enable this functionality, select either the 'hg38 (Homo sapiens)' or 'mm10 (Mus musculus)' database. You may have to enable pop-ups in your browser.

### More Files

You can find additional ribo files and references in the following Github repository:
[https://github.com/ribosomeprofiling/ribograph_sampledata](https://github.com/ribosomeprofiling/ribograph_sampledata).

## Reference Compatibility
 
When an experiment is created in the system, an md5 hash sum of the reference of that experiment is also
stored as an attribute of the experiment. This hash sum is obtained by computing the md5 sum of the string S1 + S2, where `+` stands for string concatenation. **S1** is the concatenation of the transcript names in the ribo file in the existing order and
**S2** is the concatenation of the corresponding transcript lengths. The names and lengths are separated by `,` in concatenation.
 
The references of two experiments are called compatible if the hash sum of their references are the same. In practice, this means that
the two experiments are coming from the same transcriptomic reference and therefore their coverages can be viewed together.
 
Reference hash sum is an experiment attribute and it is stored in the `reference_digest` attribute.
 


---
## Development 

### Linting and formatting
We use [black](https://black.readthedocs.io/en/stable/) to format Python files and [djlint](https://www.djlint.com/) to format Django templates.
 
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
 


### References
When a ribo file is uploaded, a hash sum is computed for the transcript names and their corresponding lengths. More precisely, the transcript names and their lengths are concatanated and and a single md5 sum of the entire string is computed. This value is used to compare two experiments to conclude whether they have the same transcriptome refrence or not.

When  there is an attempt of matching an experiment with a reference, transcript names and lengths are compared one-by-one and if the first mismatch is reported. This way users can clearly see why their refernce does not match that of the experiment.

## Implementation Notes
RiboGraph is implemented as a Django web app that uses Vue supplementally to provide reactivity on the front-end. During development, both the Django dev server and the hot reloading Vue dev server are run in parallel. During production, the Vue files are built into static assets that are served through Django. This logic is implemented in the [vue_app](ribograph/browser/templates/browser/vue_app.html) Django template.
 
### Django HTTPS API
The Vue app interfaces with the Django backend through [a series of HTTPS APIs](ribograph/browser/api.py). These APIs provide the front-end with the data required to render the charts. Results are cached for around 10 minutes for faster results and a smoother user experience.
 
