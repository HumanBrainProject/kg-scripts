# KG Scripts
This is a collection of scripts used to operate on the EBRAINS KG and to simplify some of the processes which need to be executed on top of its data.

## Run the scripts
The idea is that these scripts can be run e.g. from a specific Jupyter notebook. But of course, for development and / or other purposes, you can run these scripts from your local machine as well.

## The structure of the scripts
The scripts are held in python and they have to follow these conventions:

- each unit has its own package
- each package has a python file named the same way as the package (called "main script")
- the "main script" provides two methods: `run(properties:dict, kg:KGv3)` and `def simulate(properties:dict, kg:KGv3)`
- each package provides a file called `parameter_template.json` which defines the structure (and potential default values) of the properties which are passed to the above mentioned methods.
- each package provides a file called `description.txt` which describes what this script is doing. It can e.g. be displayed in the Jupyter notebook to let the user decide if it's the right script to be executed.
- dependencies to other packages can be specified in the requirements.txt file


