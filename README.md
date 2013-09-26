DataMart for Biomedical Research
================================
Version 0.0.1

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
