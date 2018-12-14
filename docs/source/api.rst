API
===

* :ref:`The PyMICA module`
* :ref:`Multiregression`
* :ref:`Clustered regression`
* :ref:`Calculate Field`
* :ref:`Interpolation`
    * :ref:`Inverse of the distance (2D)`
    * :ref:`IDW`
* :ref:`Cluster creation`
    * :ref:`Create clusters`
    * :ref:`Create cluster files`


The pyMICA module
-----------------

This is the main module, that bundles all the others to take the input data and generate the output field.

.. automodule:: pymica.pymica
    :members:

Multiregression
---------------

.. automodule:: pymica.multiregression
    :members:

.. automodule:: pymica.apply_regression
    :members:

Clustered regression
--------------------

.. automodule:: pymica.clustered_regression
    :members:

Calculate Field
---------------

.. automodule:: pymica.calculate_field
    :members:

Interpolation
-------------
The MICA software obtains an interpolated field through applying the
regression coefficients to a raster and an anomaly correction. This
correction is obtained interpolation the regression residuals before
adding the field to the interpolation result, which can be done using 
several methods:

Inverse of the distance (2D)
############################

.. automodule:: interpolation.inverse_distance
    :members:

IDW
###

.. automodule:: interpolation.idw
    :members:

Cluster creation
----------------

There are some functions used to create the clusters and the rasterized clusters file.

Create clusters
###############

Creates the geoJSON with the cluster definitions

.. automodule:: cluster.create_clusters
    :members:

Create cluster files
####################

Creates the GeoTIFFs with the clusters influence areas to blend the final interpolation

.. automodule:: cluster.create_cluster_files
    :members:
