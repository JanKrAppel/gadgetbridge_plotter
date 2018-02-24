#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ResultIterator:
    """A class used to iterate over sqlite3 cursor results in a for loop."""
    
    def __init__(self, cursor):
        """Initialize the interface with a cursor.
        
        Parameters
        ----------
            cursor : sqlite.Cursor
                The database cursor pointing to the results
        
        Returns
        -------
            None
        """
        self._cursor = cursor

    def __iter__(self):
        """Return self for iteration.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            self : ResultIterator
                This instance
        """
        return self
    
    def next(self):
        """Iterate over the cursor result items.
        
        Parameters
        ----------
            None
            
        Returns
        -------
            item : sequence
                One row of results
        """
        item = self._cursor.fetchone()
        if not item is None:
            return item
        else:
            raise StopIteration
            
    def all(self):
        """Convenience function to return all result items at once.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            list
                A list containing all rows
        """
        return self._cursor.fetchall()

class GadgetbridgeDatabase:
    """Provides a simple abstraction layer around the Sqlite DB."""
    
    def __init__(self, filename, device):
        """Initiate the interface. Pass a filename and a device name. The device
        name is used to pull database table mapping.
        
        Parameters
        ----------
            filename : string
                The name of the SQLite database file to open
            device : string
                The name of the device the data is stored for. This selects
                table mappings for the database.
        
        Returns
        -------
            None
        """
        import sqlite3
        from device_db_mapping import device_db_mapping
        self._db_filename = filename
        self._db = sqlite3.connect(self._db_filename)
        self._cursor = self._db.cursor()
        self.results = ResultIterator(self._cursor)
        self._query('SELECT name FROM sqlite_master WHERE type="table";')
        self.tables = [x[0] for x in self.results.all()]
        self.device = device
        self._db_names = device_db_mapping[self.device]
        
    def __del__(self):
        """Clear the class instance. This closes the database cleanly.
        
        Parameters
        ----------
            None
        
        Returns
        -------
            None
        """
        self._cursor.close()
        self._db.close()
        
    def _query(self, querystring):
        """Execute a query on the database.
        
        Parameters
        ----------
            querystring : string
                The SQLite query string
        
        Returns
        -------
            None
        """
        self._cursor.execute(querystring)
        
    def query_tableinfo(self, table_name):
        """Retrieve info about a table in the database. Returns a dict 
        containing the entries:
            * index
            * name
            * type
        for each of the columns in the table.
        
        Parameters
        ----------
            table_name : string
                The name of the table that the layout should be queried for.
        
        Returns
        -------
            None
        """
        if table_name in self.tables:
            self.query('pragma table_info({table_name:s});'.format(
                    table_name=table_name))
            res = {'name': [], 'type': [], 'index': []}
            for row in self.results:
                res['index'].append(row[0])
                res['name'].append(row[1])
                res['type'].append(row[2])
            return res
        else:
            return None

    def _build_querystring(self, dataset):
        """Build a Sqlite query to pull the dataset from the database.
        
        Parameters
        ----------
            dataset : string
                The dataset to build a query string for. Must be one of the 
                following:
                    * timestamp
                    * heartrate
                    * intensity
                    * activity
                    * steps
        
        Returns
        -------
            string
                An SQLite query string for the requested dataset
        """
        query_template = 'SELECT {dataset_col:s} FROM {table:s};'
        return query_template.format(dataset_col=self._db_names['timestamp'] + \
                                         ', ' + self._db_names[dataset],
                                     table=self._db_names['table'])
        
    def query_dataset(self, dataset):
        """Builds the query to pull a dataset from the database and executes it.
        
        Parameters
        ----------
            dataset : string
                The dataset to query from the database. Must be one of the 
                following:
                    * timestamp
                    * heartrate
                    * intensity
                    * activity
                    * steps
        
        Returns
        -------
            None
        """
        datasets = self._db_names.keys()
        datasets.remove('table')
        datasets.remove('timestamp')
        if not dataset in datasets:
            raise LookupError('Dataset not available, must be in ' + \
                              str(datasets))
        self._query(self._build_querystring(dataset))
        
    def retrieve_dataset(self, dataset, **kwargs):
        """Retrieve a dataset from the database.
        
        Parameters
        ----------
            dataset : string
                The dataset to retrieve from the database. Must be one of the 
            following:
                * timestamp
                * heartrate
                * intensity
                * activity
                * steps
            kwargs : dict
                Any other named parameters will be passed to the 
                DatasetContainer instance returned.
        
        Returns
        -------
            res : DatasetContainer
                The container with the retrieved dataset.
        """
        from datetime import datetime
        from dataset_container import DatasetContainer
        self.query_dataset(dataset)
        res = DatasetContainer(dataset, **kwargs)
        for ts, val in self.results:
            res.append(datetime.fromtimestamp(ts), val)
        return res
    
if __name__ == '__main__':
    from datetime import timedelta
    from sys import argv
    from matplotlib import gridspec, pyplot as plt
    time_resolution = timedelta(days=1)
    db = GadgetbridgeDatabase(argv[1], 'MI Band')
    heartrate = db.retrieve_dataset('heartrate', time_resolution=time_resolution)
    heartrate.add_filter('heartrate')
    steps = db.retrieve_dataset('steps', time_resolution=time_resolution)
    fig = plt.figure()
    gs = gridspec.GridSpec(2,1,height_ratios=[4,1])
    plt.subplot(gs[0])
    heartrate.downsample_histogram().plot()
    plt.xticks([])
    plt.subplot(gs[1])
    plt.subplots_adjust(hspace=0)
    steps.downsample_sum().plot()
    plt.savefig(argv[2])