# Build

Code here requires the following to be fully executed:

+ a standard ipython notebook install, if you want to run the notebook
    + ipython
    + jinja2
    + pyzmq
    + tornado
    + jsonschema
+ numpy
+ scipy
+ pandas
+ matplotlib

And maybe not scipy... If you have an environment that already has all that, give it a go; otherwise try the virtual environment setup below.


```
# cloning repo
git clone git@github.com:RZachLamberty/l_ds_challenge.git
cd l_ds_challenge

# getting data, if you don't have it already
wget https://www.dropbox.com/s/h205ik7nwvjjcvd/rides.csv?dl=1 -O rides.csv

# building your python virtual environment
virtualenv ~/path/to/my/venv
. ~/path/to/my/venv/bin/activate
pip install -r requirements.txt
```

# Design
Pretty dumb so far -- just loading the data into a pandas dataframe and then attempting to do random sampling of hotroutes / customer rides. The data set is large enough right now that I'm clearly not doing it the right way. Perhaps a later version will improve it.

## IPython Notebook
Launch the ipython notebook by calling

```
ipython notebook
```

Once inside, choose ```hotroute_vis.ipynb``` and run all cells.


OR

Just click on the ipynb file up above -- github will display the final version for you because it's flipping awesome.
