YAML to pyDAL or classes
------------
Generates openapi, `pydal <https://py4web.com/_documentation/static/en/chapter-07.html>`_
and class (or pydantic)  definitions of database schema from `anvil.yaml <https://anvil.works>`_ or
`openapi.yaml <https://swagger.io/docs/specification/about/>`_

Why is it here?
---------------
*pycharm* is awesome. *pytest* is awesome. *pyDAL* is awesome. *anvil.works* is awesome.
Why can't we use these mountains of awesomeness together?
This repo can used with `pyDALAnvilWorks <https://github.com/benlawraus/pyDALAnvilWorks>`_ to do just that.
When you clone your *anvil.works* app onto your computer, run this program to generate a *pyDAL* schema file.
You know what I mean if you use *pyDAL*, it starts something like this::

    db.define_table(....

describing your database schema.

Once you got that, you can copy and paste the `anvil` directory from `pyDALAnvilWorks <https://github.com/benlawraus/pyDALAnvilWorks>`_
into your *anvil.works* app.

Now you have a `sqlite` database for your app amd you can use *pytest* from your *pycharm* IDE.

What is it for?
---------------
`pydal <https://py4web.com/_documentation/static/en/chapter-07.html>`_ is a very good database abstraction layer (DAL)
for python handling of just about any database including `sqlite`. The motivation for writing this project was to use 
pydal locally so that tests can be run locally and not on external servers. 


Once the git repo is downloaded, use `anvil.yaml` (or an `openapi.yaml`) file containing the
projects database description. This will read `anvil.yaml` and generate a python file with the database
tables in openapi form, pydal form and pydantic model form.

How to run it?
---------------
First thing is to create a python environment. Once the environment is activated,
pip install the dependencies that are at the top of `main.py`.
Then copy the `anvil.yaml` or an `openapi.yaml` file into the `input` directory and run
`main.py` with::

    python main.py

The output model and definition files are in the `output` directory.

File Structure
^^^^^^^^^^^^^^
The file structure is as follows::

            main.py # the entire software divided into functions
    Input:  input/anvil.yaml
            OR
            input/openapi.yaml
    Output: output/anvil_openapi.yaml  # conversion to openapi standard yaml
            output/db_models.py  # pydantic type models
            output/pydal_def.py  # database definition for pyDAL


How to use it?
--------------
#.  You need to supply a `yaml` file, either `anvil.yaml` (created with your repo on `anvil.yaml <https://anvil.works>`_)
    or `openapi.yaml` which has the `components` section of the `openapi` standard.
#.  Some types are not implemented yet. What is implemented has some additional caveats.

`number`
           is implemented as integer.
`list:integer` and `list:string`
           are implemented from `simpleObject` in `anvil`. To differentiate, the column name must end in `_listint` or `_liststr`.

Implemented
-----------

============= ============== ======= ========= =========== =============== ======= =========
INPUT                                                      OUTPUT
---------------------------------------------- ---------------------------------------------
ANVIL                        OPENAPI           CLASSES     PYDAL           OPENAPI
TYPE          NOTE           TYPE    FORMAT    TYPE        TYPE            TYPE    FORMAT
============= ============== ======= ========= =========== =============== ======= =========
string                       string            str         string          string
datetime                     string  date-time datetime    datetime        string  date-time
date                         string  date      date        date            string  date
bool                         boolean           bool        boolean
link_single                  #ref              class       reference       #ref
link_multiple                array   #ref      List[class] list: reference
simpleObject  column_listint array   integer   List[int]   list:integer    array   integer
simpleObject  column_liststr array   string    List[str]   list:string     array   string
============= ============== ======= ========= =========== =============== ======= =========


TODO
------
- separate the functions into options
- anvil.works has `number` type that can be `int` or `float`. This program only uses `int`. Need to change this so that `float`, `double` etc can be used
- anvil.works has `simpleobject` i.e. `json`. `list:integer` and `list:string` are implemented but needs more work to specify as pure `json`
