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

Now you have a `sqlite` database for your app and you can use *pytest* from your *pycharm* IDE.

What is it for?
---------------
`pydal <https://py4web.com/_documentation/static/en/chapter-07.html>`_ is a very good database abstraction layer (DAL)
for python handling of just about any database including `sqlite`.

BUT you do not need to use *pyDAL*, because you can also use it to generate class definitions of your tables (this repo uses `datamodel-code-generator` to do that)
It also converts your `anvil.yaml` into `openapi.yaml` if want to use some other yaml converter.


Once the git repo is downloaded, use an `openapi.yaml` (or an `anvil.yaml`) file containing the
projects database description. This will read the file and generate a python file with the database
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

    main.py # the entire software divided into function files
    Input:  tests/yaml/in/anvil.yaml  # file from downloaded anvil.works app
            tests/yaml/in/anvil_refined.yaml # OPTIONAL openapi format of fields requiring more information to specify
            OR
            tests/yaml/in/openapi.yaml
    Output: tests/yaml/out/anvil_openapi.yaml  # conversion to openapi standard yaml
            tests/yaml/out/db_models.py  # pydantic type models
            tests/yaml/out/pydal_def.py  # database definition for pyDAL


How to use it?
--------------
Here is an example run in the terminal (good for python3.7+)::

    mkdir work
    cd work
    python3 -m venv ./venv
    source venv/bin/activate
    pip3 install datamodel-code-generator
    pip3 install strictyaml
    git clone https://github.com/benlawraus/yaml2schema.git
    cd yaml2schema/src/yaml2schema
    # change anvil.yaml or openapi.yaml
    python3 main.py
    # checkout your changes in the files in the out/ directory

#.  You need to supply a `yaml` file, either `anvil.yaml` (created with your repo on `anvil.yaml <https://anvil.works>`_)
    or `openapi.yaml` which has the `components` section of the `openapi` standard.
#.  Sometimes `anvil.yaml` is too vague for what you need. You can over-write parts of `anvil.yaml`
    with a more detailed specification in `anvil_refined.yaml`. `anvil_refined.yaml` needs to be written in **openapi** yaml though.
    For example

    `number`
            is implemented as `integer` by default, but you can over-ride to `float` in `anvil_refined.yaml`

Included in the `src/yaml2schema/input` directory, there is an example database schema. You can see
what is generated in the `src/yaml2schema/output` directory.

Implemented
-----------
============= ================== ======= ========= ============= =============== ======= =========
INPUT                                                            OUTPUT
-------------------------------------------------- -----------------------------------------------
ANVIL                            OPENAPI           CLASSES       PYDAL           OPENAPI
-------------------------------- ----------------- ------------- --------------- -----------------
TYPE          NOTE               TYPE    FORMAT    TYPE          TYPE            TYPE    FORMAT
============= ================== ======= ========= ============= =============== ======= =========
string                           string            str           string          string
string        pydal only         string  text      str           text            string
number                           integer           int           integer         integer int32
number        anvil_reduced.yaml integer int32     int           integer         integer int32
number        anvil_reduced.yaml integer int64     int           bigint          integer int64
number        anvil_reduced.yaml number  float     float         double          number  float
datetime                         string  date-time datetime      datetime        string  date-time
date                             string  date      date          date            string  date
bool                             boolean           bool          boolean
link_single                      #ref              class         reference       #ref
link_multiple                    array   #ref      List[class]   list: reference array   #ref
simpleObject  anvil_reduced.yaml array   integer   List[int]     list:integer    array   integer
simpleObject  anvil_reduced.yaml array   string    List[str]     list:string     array   string
simpleObject                     object            Dict[str,Any] json            object
============= ================== ======= ========= ============= =============== ======= =========

Examples anvil_refined.yaml
----------------------------
A *meetings* table has a *discussion* field that is a large text body and *peoples_names* that is a list of strings:
In anvil_refined.yaml, for sqlite::

    components:
      schemas:
        meetings:
          properties:
            peoples_names:
              type: array
              items:
                type: string
            discussion:
              type: string
              format: text


