DataMart for Biomedical Research
================================
Version 0.1.0

Meant to act as a single data store at the end of the QA pipeline that will
allow querying across all data sources. Organized around the idea of Variables,
which represent discrete pieces of information that have some Dimension, which
is essentially a datatype.

###Dimensions

Dimensions are the datatypes for variables. A Dimension consists of a name, a
description, and a datatype, e.g.

Name: Distance (in)
Description: Distance in inches
Datatype: Float

Name: Years
Description: Time represented by years (float)
Datatype: Float

Name: Count
Description: An integer count of something.
Datatype: Integer

Name: Volume (mm^3)
Description: Volume in cubic millimeters.
Datatype: Float

Every Variable in the system will have a Dimension associated with it.
Possible datatypes are Integers, Floats, Dates, and Strings.

###Variables

Variables are the heart of the datamart. A Variable is some measurement of
interest and is minimally a name, description, and dimension but also has a
list of associated Roles and Sources. When a Role is associated with a variable
is allows anyone with that Role to view that variable. Associating a Source
with a Variable is needed when flagging data as needing attention, so that it
can be tracked to the source. Best way to understand is some examples:

Name: Subject Height (in)
Description: Height of a subject in inches.
Dimension: Distance (in)
Roles: Internal User, External User
Sources: Biographic Survey

Name: Years of Education
Description: A subject's years of education.
Dimension: Years
Roles: Internal User, External User
Sources: Biographic Survey

Name: Number of Children
Description: Number of children a subject has.
Dimension: Count
Roles: Internal User, External User
Sources: Biographic Survey

Name: Left Striatal Volume (mm^3)
Description: A subject's left striatal volume in cubic millimeters.
Dimension: Volume (mm^3)
Roles: Internal User
Sources: Freesurfer Measures


###Subjects / External IDs

Individuals on which there is data in the system. 

Subjects are made up of internal IDs meant for use within the datamart and an
unlimitted number of external IDs. External IDs are meant to be shared outside
the system. Tying external IDs to roles so that a given role can only see the
specified external IDs is a planned feature.

###Sources

Where a variable came from, e.g. a CRF, an imaging repository such as XNAT, an
online database of anatomical data, etc. Sources are made up of a name,
description, url, and a list of associated Events and Variables.


###Events

Events are when data was collected. For instance, any time a subject is
scanned is an event, as is any time they fill out a form. Some Variables may
not have clear events associated with them, such as the output of a specific
MRI processing pipeline. In those situations a new event can be created or the
variables can be added to the event when the scan that generated the data was
taken.

Events are associated with Sources, meaning that for a given event, those
Sources may have been collected.


###Users

Users internal to the system. Any user who has logged into the system will be
listed here. With the exception of the superuser, authentication is handled by
LDAP.


###Roles

Roles are groups of permissions that get assigned to Users. Permission to view
Variables is associated with Roles, so a User will only be able to view a
variable if they have a Role that has been granted permission to do so. This
allows for sharing data while still limiting access to sensitive information.

###Facts

All of the above are to enable the Facts table, where rows are unique to a
Subject, Event combination and the columns are Variables. Complex nested
queries can be constructed over all Facts in the system, and the results
downloaded in a number of formats.

Facts can be added a Variable at a time, but can also be uploaded in csv
format.

To Run
------

If there isn't an accessible postgres instance, install a local postgres
instance and create user/db. Update instace/production.cfg so
SQLALCHEMY_DATABASE_URI reflects the DB, username, and password.

###Install Requirements

Create a virtualenv
    
    virtualenv datamart_env

Install production requirements

    pip install -r prod-requirements.txt

Install development requirements (to run testing or the dev server)

    pip install -r dev-requirements.txt
    
###Instance Directory and config file

To handle logs and uploaded files you'll need to create an instance directory.
By default the config assumes the instance directory is datamart/instance but
that can be overidden in the config files. To use the default:

    $ cd repo_dir
    $ mkdir instance
    $ mkdir logs
    $ mkdir uploads

This is also where the production.cfg file will go, which allows you to
set any configuration variables specific to this instance. An example
production.cfg can be found as datamart/example_production.cfg. Copy it to your
instance directory and rename it production.cfg then edit the appropriate
variables, such as the SQLALCHEMY_DATABASE_URI, the SECRET_KEY, the mail server
settings, etc.

###Secret Keys

For sessions to be secure you need to generate a secret key and copy it into
your production.cfg file. A secret key can be generated at the command line by
running a python interpreter and:

    >>> import os
    >>> os.urandom('24')
    '\xd2G\x85\x92\x8f\x12B\xc9\x03\xf1\x89\xde\xd0\x9b\xa1\xdc\x1aU!\xb2\xc3xq\xed'

###Development

Use the manager to launch a dev server after creating a virtualenv and
installing the dev requirements:

    python manage.py runserver

###Testing

After creating a virtualenv and installing the dev requirements use the manager
to run the tests:

    python manage.py test
    
Javascript and selenium based testing is coming.

###Production

Clone the repository, create a virtualenv, and install the python production
requirements. Install uWSGI, Nginx, and Postgres >=9.1 (Preferably on a
separate machine)

See docs/<YOUR_OS>/ for detailed documentation. (Currently only RHEL/CENTOS.)

Developers
----------

###Code Layout
.
├── README.md
├── dev-requirements.txt
├── dev_config.py
├── manage.py
├── prod-requirements.txt
├── requirements.txt
├── alembic.ini
├── license.txt
├── docs
│   └── RHEL_Centos_production_setup.md
├── datamart
│   ├── __init__.py
│   ├── admin.py
│   ├── api.py
│   ├── app.py
│   ├── config.py
│   ├── datamart.db
│   ├── extensions.py
│   ├── forms.py
│   ├── jinja_filters.py
│   ├── models.py
│   ├── production.cfg
│   ├── secure_redirect.py
│   ├── utils.py
│   ├── views.py
│   ├── static
│   │   ├── css
│   │   │   ├── bootstrap-responsive.css
│   │   │   ├── bootstrap-responsive.min.css
│   │   │   ├── bootstrap.css
│   │   │   ├── bootstrap.min.css
│   │   │   ├── chosen-sprite.png
│   │   │   ├── chosen.css
│   │   │   └── custom.css
│   │   ├── font
│   │   ├── img
│   │   │   ├── glyphicons-halflings-white.png
│   │   │   └── glyphicons-halflings.png
│   │   ├── js
│   │   │   ├── dimension.js
│   │   │   ├── fact_edit.js
│   │   │   ├── facts.js
│   │   │   ├── facts_datasource.js
│   │   │   ├── label-upload.js
│   │   │   ├── templates.js
│   │   │   ├── upload.js
│   │   │   └── ext
│   │   │       ├── bootstrap.js
│   │   │       ├── bootstrap.min.js
│   │   │       ├── chosen.jquery.js
│   │   │       ├── handlebars.js
│   │   │       ├── jquery-1.9.1.js
│   │   │       ├── jquery.fileDownload.js
│   │   │       ├── jquery.min.js
│   │   │       ├── json2.js
│   │   │       ├── underscore-min.js
│   │   │       └── underscore.js
│   │   └── templates
│   │       ├── edit-fact-new-variable.handlebars
│   │       ├── facts-nested-filter.handlebars
│   │       ├── facts-new-filter.handlebars
│   │       └── model-table-controls.handlebars
│   └── templates
│       ├── _formhelpers.html
│       ├── _gridhelpers.html
│       ├── base.html
│       ├── dimension_edit.html
│       ├── dimensions.html
│       ├── errors
│       │   ├── forbidden_page.html
│       │   ├── page_not_found.html
│       │   └── server_error.html
│       ├── event_edit.html
│       ├── events.html
│       ├── externalid_edit.html
│       ├── externalids.html
│       ├── fact_edit.html
│       ├── facts.html
│       ├── index.html
│       ├── label_upload.html
│       ├── login.html
│       ├── role_edit.html
│       ├── roles.html
│       ├── source_edit.html
│       ├── sources.html
│       ├── subject_edit.html
│       ├── subjects.html
│       ├── upload.html
│       ├── user_edit.html
│       ├── users.html
│       ├── variable_edit.html
│       └── variables.html
├── tests
│   ├── __init__.py
│   ├── test_dimension_api.py
│   ├── test_dimensions.py
│   ├── test_events.py
│   ├── test_facts.py
│   ├── test_facts_api.py
│   ├── test_home.py
│   ├── test_roles.py
│   ├── test_sources.py
│   ├── test_subjects.py
│   ├── test_users.py
│   ├── test_variable_api.py
│   └── test_variables.py
└── alembic
    ├── README
    ├── env.py
    ├── script.py.mako
    └── versions
        ├── 23dcdff2dad2_added_backref_so_rol.py
        ├── 27895d4324c8_variables_and_roles_.py
        ├── 3048e84eead4_added_delete_cascade.py
        ├── 33dee8e1b22c_added_subject_table_.py
        ├── 340608d055f3_added_roles_to_varia.py
        ├── 362ecdf08386_added_source_table_a.py
        ├── 36f1f1bd8a5a_removed_not_null_con.py
        ├── 3bbac6e7d8ee_standardized_on_name.py
        ├── 403c42ff4a79_added_is_admin_to_us.py
        ├── 420c1fe55812_added_data_type_enum.py
        ├── 499accc505c3_dropped_unique_const.py
        ├── 5267f92565cb_switched_user_ips_to.py
        ├── 57f90b4e233f_added_is_admin_to_us.py
        ├── 5abd00729c5c_.py
        ├── 6da215bb5f1_added_in_use_column_.py
        ├── 96489d0aa37_added_event_table_wi.py
        └── efda3e6ba54_drop_reviewed_from_f.py


###Found a bug?

Please use the integrated issues in github to submit your bug.

###Contribute Your Changes

Please submit a pull request with your changes. 
Author
------

Mark Scully
DataPraxis, LLC

License
-------

Released under OSI version of MIT license. See license.txt

