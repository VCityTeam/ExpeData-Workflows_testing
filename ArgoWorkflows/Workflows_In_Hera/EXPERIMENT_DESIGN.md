# Experiment design notes

## On the asymmetry of roles of the vintage and borough parameters

At some level of abstraction
- a `boroughs-3Dtiles`` (of a city) can be seen as the (geographic) geometrical 
  data set gathering the boroughs that are considered to describe such a city.
- a `vintage-3DTiles` can be seen the gathering of dated data (vintages being a 
  coarse-grained measure for time) of a part of a city or the "whole" city
  (that is a `boroughs-3Dtiles`).

In theory, boroughs and vintages parameters thus play a symmetrical (or 
orthogonal) role in the partition of the data of a city. We could describe
a given city data as a set of `borough-vintage-3DTiles` where borough and
vintages vary in a prescribed set of values. 
For each vintage value we could then consider the 
`some_vintage-boroughS-3Dtiles` set gathering all the `borough-vintage-3DTiles` 
sharing some `vintage` value.
Equivalently, for each borough value we could then consider the 
`vintageS-borough-3Dtiles` set gathering all the `borough-vintage-3DTiles` 
describing some specified borough.

Most often when projects work on city data, they first scale up the data
by considering a greater number of boroughs (bigger cities). And once
geographic scale-up is achieved then (and only then) does time kick-in
(through different time based versions of the city).
When a city modeling project adopts such a project history (implicitly)
inherited ranking of space vs time parameters, and when/because data size 
imposes to split among different databases, then a "natural" choice arises:
a temporal city (data set, that is the set of `borough-vintage-3DTiles`) is
described a vintaged based set of `boroughS-3Dtiles`.

Still with memory or storage footprints concerns in mind, the implementation
then follows this arbitrary descriptive priming of vintage over boroughs.
And the implementation (might) then e.g. consider as many databases are they 
are vintages (each "vintaged-db" holding/storing a `boroughS-3Dtiles`).

Notice that the priming of vintage over boroughs can go further than an
asymmetry in storage and be propagated to the WorkflowTemplate level.
The `define_import_boroughs_to_3dcitydb_template()` function is an example
of the "functional" integration (AW WorkflowTemplates being the equivalent
of functions) of code due to optimization techniques (asserting a database
sanity check). The structure of `test_import_gml_integrated_for_loop.py`, that 
uses `define_import_boroughs_to_3dcitydb_template()`, reflects this 
"functional" integration by expressing only the vintage for loop (when the
boroughs for loop is integrated/hidden-away in the WorkflowTemplate). 

In opposition `test_import_gml.py`

