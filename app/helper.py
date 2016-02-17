from app import db
import json, os

class tableinfo(object):

    def __init__ (self, tablename):
        self.tablename = tablename

    # maybe later on can be used when recreating a table structure
    # this normalizes data types
    def datanorm(self, value):
        if self.value in ('INTEGER','id'):
            self.value = 'int'
        if self.value == 'VARCHAR':
            self.value = 'string'
        if self.value == 'DATETIME':
            self.value = 'date'
        return self.value

    # this gets data types from each field
    def getdatatype(self):
        self.datafields = db.session.execute("PRAGMA table_info(" + self.tablename + ")")
        self.datafieldsarray = []
        for self.v in self.datafields:
            self.datafieldsdict = {}
            for self.column, self.value in self.v.items():
                if self.column in ('name', 'type'):
                    if self.column == 'type':
                        self.value = self.datanorm(self.value)
                    self.datafieldsdict[self.column] = self.value
            self.datafieldsarray.append(self.datafieldsdict)
        self.datafieldsjson = json.dumps(self.datafieldsarray)

        return self.datafieldsjson

    # this gets field names
    def getdataname(self):
        self.columns = db.session.execute("PRAGMA table_info(" + self.tablename + ")")
        self.columnsarray = []
        for self.v in self.columns:
            self.columnsdict = {}
            for self.column, self.value in self.v.items():
                if self.column in ('name'):
                    self.columnsdict['datafield'] = self.value
                    self.columnsdict['text'] = self.value
            self.columnsarray.append(self.columnsdict)
        self.columnsjson = json.dumps(self.columnsarray)

        return self.columnsjson

    # and the actual table data
    def getdata(self):
        self.data = db.session.execute("select * from " + self.tablename)
        self.dataarray = []
        for self.v in self.data:
            self.datadict = {}
            for self.column, self.value in self.v.items():
                self.datadict[str(self.column)] = self.value
            self.dataarray.append(self.datadict)
        self.datajson = json.dumps(self.dataarray)

        return self.datajson

    # and data from selected fields
    def filterdata(self, fieldname, fieldvalue):
        self.filterdata = db.session.execute("select * from " + self.tablename
                                             + " where " + str(fieldname) + "=" + str(fieldvalue))
        self.filterdataarray = []
        for self.v in self.filterdata:
            self.filterdatadict = {}
            for self.column, self.value in self.v.items():
                self.filterdatadict[str(self.column)] = self.value
            self.filterdataarray.append(self.filterdatadict)
        self.filterdatajson = json.dumps(self.filterdataarray)

        return self.filterdatajson
