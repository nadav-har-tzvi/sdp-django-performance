Performance optimization is a basic skill any developer should acquire.
This repository walks through between different states of database access optimization.

# How to setup the project
## Prerequisites -
1. [Python](http://www.python.org) >= 3.5 - Consult with the installation docs appropriate for your OS.
2. [pip](https://pip.pypa.io/en/stable/) - Usually bundled with most modern Python releases. If not, refer to [pip's installation](https://pip.pypa.io/en/stable/installing/) part of the docs
3. An [IMDB dataset](https://www.imdb.com/interfaces/), fully extracted into a single directory somewhere on your machine.

## Setting up (*nix only)
0. Clone this repo, don't download it as you will need the ability to jump between git tags.
1. Checkout tag step0-no-optimization
2. Open a terminal and navigate to the repository's root.
3. Create a .env file in the repository's root. The .env file should contain the following keys:
```env
DB_ENGINE=<the relevant django DB backend>  # Required, Refer to https://docs.djangoproject.com/en/2.2/ref/settings/#engine
DB_HOST=<host URL>  # Default: localhost
DB_USER=<DB username> # Required
DB_PASSWORD=<DB password> # Required
DB_NAME=<DB name> # Default: imdb
IMDB_DATASET_LOCATION=<a relative or absolute path to the dataset directory> # e.g. - ~/Downloads/imdb
```
4. Create a virtual environment by executing the following command (while still in the repository's root directory):
```bash
python -m venv venv
```
5. Activate the newly created environment by executing the following command (while still in the repository's root directory):
```bash
source venv/bin/activate
```
4. Install the required dependencies via executing the following command (while still in the repository's root directory):
```bash
pip install -r requirements.txt
```
4. Migrate the project using the following command (while still in the repository's root directory):
```bash
python manage.py migrate
```
> Note! The migrate operation includes loading tons of data into your DB. This operation can take several hours! I advise to let this run overnight.
5. Run the Django self hosted server (while still in the repository's root directory):
```bash
python manage.py runserver
```
Note, Django binds to port 8000 by default, to change this, simply run the following command:
```bash
python manage.py runserver localhost:<port>
# e.g. python manage.py runserver localhost:8005
```
6. To validate this works, open a browser and go to `http://localhost:<port>/api`. It should take about 2 minutes to load. If everything worked, you should see the following page:
<iframe src="https://drive.google.com/file/d/196nXtdAZkFlMxHDwOI_ypvQVG61491yn/preview" width="640" height="480"></iframe>

## How to use this repository
This repository is supposed to lead the developer through a set of steps needed to optimize the Titles API.
Use `git checkout <tag>` to move between the steps.
After moving between the steps, execute `python manage.py migrate` to apply any newly added migrations
You should pay attention to how the time spent on SQL changes between steps (after applying migrations), you can achieve this via Django Debug Toolbar that is .
There are 5 steps:

1. `step0-no-optimization` - No optimization whatsoever.
2. `step1-indices` - DB indices added, significant optimization
3. `step2-eager-loading` - Eager loading via .prefetch_related and .select_related added, significant optimization
4. `step3-using-only-defer` - Load only required attributes, minor optimization
5. `step4-pagination` - Switch to cursor based pagination, somewhat major optimization.

If you want to switch to step3 for example, execute the following command:
```bash
git checkout step3-using-only-defer
```