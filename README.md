# EPyDb
[![version](https://img.shields.io/badge/version-0.1dev-blue.svg?style=flat-square)]() 
[![license](https://img.shields.io/github/license/HidekiHrk/EPyDb.svg?style=flat-square)](https://github.com/HidekiHrk/EPyDb/blob/master/LICENSE) 
[![forks](https://img.shields.io/github/issues/HidekiHrk/EPyDb.svg?style=flat-square)]()<br>
Enhanced Python database generator!<br>
```markdown
pip install EPyDb
```
<br>
**How to use:**<br>
**Sqlite3:**<br>
```python
import epydb

# Create Database obj #
# Sqlite3(filename='data.db')
con = epydb.Sqlite3()

# Create a Table #
# create_table(tablename, **kwargs)
con.create_table('table1', info1='TEXT', info2='TEXT', __ignore__=True)
# __ignore__=True prevents the code to raise an error if the table already exists

# Get that table #
# get_table(tablename)
con.get_table('table1')

# Add a row to the table #
# create_row(tablename, data)
con.create_row('table1', {'info1':'hello', 'info2':'world', 'basecol':'info1'}) 
# 'basecol' is the reference column to query 

# Get that row #
# get_row(tablename, basecol, basevalue)
con.get_row('table1', 'info1', 'hello')

# Update that row #
# update_row(tablename, basecol, basevalue, data)
con.update_row('table1', 'info1', 'hello', {'info1':'foo', 'info2':'bar'})

# Delete that row #
# del_row(tablename, basecol, basevalue)
con.del_row('table1', 'info1', 'foo')

# Get table list #
print(con.tables)

# Delete Table #
# del_table(tablename, ignore=False)
con.del_table('table1', ignore=True)
# ignore=True prevents code to raise an error if ctx table not exists

# Execute SQL code if you want #
# execute_sql(*args, fetch=None, commit=False)
con.execute_sql('CREATE TABLE IF NOT EXISTS table1 (info1 TEXT, info2 TEXT)', commit=True)
# commit=True commits database changes
# fetch returns the value of query and must be None, 'one' or 'all'
# None returns nothing, 'one' returns "cursor.fetchone()", 'all' returns "cursor.fetchall()"
```
<br>
Errors:

- epydb.errors.TableError
- epydb.errors.ColumnError
- epydb.errors.RowError
