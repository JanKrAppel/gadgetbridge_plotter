#!/usr/bin/env python
# -*- coding: utf-8 -*-

class result_iterator:
    
    def __init__(self, cursor):
        self.__cursor = cursor

    def __iter__(self):
        return self
    
    def next(self):
        item = self.__cursor.fetchone()
        if not item is None:
            return item
        else:
            raise StopIteration
            
    def all(self):
        return self.__cursor.fetchall()

class gb_database:
    """
    Provides a simple abstraction layer around the Sqlite DB.
    """
    
    def __init__(self, filename):
        import sqlite3
        self.__db_filename = filename
        self.__db = sqlite3.connect(self.__db_filename)
        self.__cursor = self.__db.cursor()
        self.results = result_iterator(self.__cursor)
        self.query('SELECT name FROM sqlite_master WHERE type="table";')
        self.tables = [x[0] for x in self.results.all()]
        
    def __del__(self):
        self.__cursor.close()
        self.__db.close()
        
    def query(self, querystring):
        self.__cursor.execute(querystring)
        
    def query_tableinfo(self, table_name):
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
        for table in self.tables:
            tab_info = self.query_tableinfo(table)
            print table
            print '-'*10
            for index, name, datatype in zip(tab_info['index'], 
                                             tab_info['name'], 
                                             tab_info['type']):
                print index, name, ':', datatype
            print
