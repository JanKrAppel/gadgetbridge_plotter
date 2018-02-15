#!/usr/bin/env python
# -*- coding: utf-8 -*-

class result_iterator:
    """
    A class used to iterate over sqlite3 cursor results in a for loop.
    """
    
    def __init__(self, cursor):
        """
        Initialize the interface with a cursor.
        """
        self.__cursor = cursor

    def __iter__(self):
        """
        Return self.
        """
        return self
    
    def next(self):
        """
        Iterate over the cursor result items.
        """
        item = self.__cursor.fetchone()
        if not item is None:
            return item
        else:
            raise StopIteration
            
    def all(self):
        """
        Convenience function to return all result items at once.
        """
        return self.__cursor.fetchall()

class gb_database:
    """
    Provides a simple abstraction layer around the Sqlite DB.
    """
    
    def __init__(self, filename, device):
        """
        Initiate the interface. Pass a filename and a device name. The device
        name is used to pull database table mapping.
        """
        import sqlite3
        from device_db_mapping import device_db_mapping
        self.__db_filename = filename
        self.__db = sqlite3.connect(self.__db_filename)
        self.__cursor = self.__db.cursor()
        self.results = result_iterator(self.__cursor)
        self.__query('SELECT name FROM sqlite_master WHERE type="table";')
        self.tables = [x[0] for x in self.results.all()]
        self.device = device
        self.__db_names = device_db_mapping
        
    def __del__(self):
        self.__cursor.close()
        self.__db.close()
        
    def __query(self, querystring):
        """
        Execute a query on the database.
        """
        self.__cursor.execute(querystring)
        
    def query_tableinfo(self, table_name):
        """
        Retrieve info about a table in the database. Returns a dict containing
        the entries:
            - index
            - name
            - type
        for each of the columns in the table.
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
        
    def dump_tableinfo(self):
        """
        Print info on all the tables in the database.
        """
        for table in self.tables:
            tab_info = self.query_tableinfo(table)
            print table
            print '-'*10
            for index, name, datatype in zip(tab_info['index'], 
                                             tab_info['name'], 
                                             tab_info['type']):
                print index, name, ':', datatype
            print

    def __build_querystring(self, dataset):
        """
        Build a Sqlite query to pull the dataset from the database.
        Dataset must be one of the following:
            - timestamp
            - heartrate
            - intensity
            - activity
            - steps
        """
        query_template = 'SELECT {dataset_col:s} FROM {table:s};'
        db_names = self.__db_names[self.device]
        return query_template.format(dataset_col=db_names['timestamp_col'] + \
                                         ', ' + db_names[dataset + '_col'],
                                     table=db_names['table'])
        
    def query_dataset(self, dataset):
        """
        Builds the query to pull a dataset from the database and executes it.
        Dataset must be one of the following:
            - timestamp
            - heartrate
            - intensity
            - activity
            - steps
        """
        from device_db_mapping import datasets
        if not dataset in datasets:
            raise LookupError('Dataset not available, must be in ' + \
                              str(datasets))
        self.__query(self.__build_querystring(dataset))
        
    def retrieve_dataset(self, dataset, **kwargs):
        """
        Retrieve a dataset. Returns a dict with two entries containing a list 
        each:
            - timestamp
            - dataset
        Timestamp is formatted as datetime. Dataset must be one of the 
        following:
            - timestamp
            - heartrate
            - intensity
            - activity
            - steps
        """
        from datetime import datetime
        from dataset_container import dataset_container
        self.query_dataset(dataset)
        res = dataset_container(dataset, **kwargs)
        for ts, val in self.results:
            res.append(datetime.fromtimestamp(ts), val)
        return res
    
if __name__ == '__main__':
    from datetime import timedelta
    from sys import argv
    from matplotlib import gridspec, pyplot as plt
    time_resolution = timedelta(days=1)
    db = gb_database(argv[1], 'MI_BAND')
    heartrate = db.retrieve_dataset('heartrate', time_resolution=time_resolution)
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