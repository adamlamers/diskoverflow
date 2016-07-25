""" stackexchange_to_sqlite_iterparse
Converts StackExchange's data dump from XML into a sqlite
database with full-text search tables """

# coding: utf-8
import xml.etree.cElementTree as ET
import sqlite3
import sys

SE_COMMUNITY_NAME = "stackoverflow"
skipindex = 0
SAVE_EVERY = 25000

conn = sqlite3.connect('{}.sqlite3'.format(SE_COMMUNITY_NAME))
db = conn.cursor()

se_post_schema = {"Title" : "TEXT",
                  "Body" : "TEXT",
                  "Score" : "INTEGER",
                  "Tags" : "TEXT",
                  "Id" : "INTEGER UNIQUE NOT NULL",
                  "CreationDate" : "TEXT",
                  "OwnerUserId" : "INTEGER",
                  "LastActivityDate" : "TEXT",
                  "ViewCount" : "INTEGER",
                  "AnswerCount" : "INTEGER",
                  "PostTypeId" : "INTEGER", #1 is question, 2 is answer
                  "CommentCount" : "INTEGER",
                  "LastEditorUserId" : "INTEGER",
                  "AcceptedAnswerId" : "INTEGER",
                  "FavoriteCount" : "INTEGER",
                  "LastEditDate" : "TEXT",
                  "ParentId" : "INTEGER",
                  "ClosedDate" : "TEXT",
                  "OwnerDisplayName" : "TEXT",
                  "CommunityOwnedDate" : "TEXT"}

def schema_column_names(schema_dict):
    schema = []
    for key, _ in schema_dict.items():
        schema.append(key)

    return schema


def create_table_from_schema(table_name, schema_dict):
    schema = []
    for key, deftype in se_post_schema.items():
        schema.append("{} {}".format(key, deftype))

    qcolumns = ', '.join(schema)
    template = "CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, qcolumns)

    return template

def create_community_table(COMMUNITY_NAME):
    db.execute(
        create_table_from_schema("{}_posts".format(COMMUNITY_NAME), se_post_schema))
    db.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS {}_fts USING fts4(title, body)" .format(COMMUNITY_NAME))
    db.execute("""CREATE TRIGGER IF NOT EXISTS {0}_posts_bu BEFORE UPDATE ON {0}_posts BEGIN
                      DELETE FROM {0}_fts WHERE docid=old.rowid;
                  END;""".format(COMMUNITY_NAME))
    db.execute("""CREATE TRIGGER IF NOT EXISTS {0}_posts_bd BEFORE DELETE ON {0}_posts BEGIN
                      DELETE FROM {0}_fts WHERE docid=old.rowid;
                  END;""".format(COMMUNITY_NAME))
    db.execute("""CREATE TRIGGER IF NOT EXISTS {0}_posts_au AFTER UPDATE ON {0}_posts BEGIN
                      INSERT INTO {0}_fts(docid, title, body) VALUES(new.rowid, new.Title, new.Body);
                  END;""".format(COMMUNITY_NAME))
    db.execute("""CREATE TRIGGER IF NOT EXISTS {0}_posts_ai AFTER INSERT ON {0}_posts BEGIN
                      INSERT INTO {0}_fts(docid, title, body) VALUES(new.rowid, new.Title, new.Body);
                  END;""".format(COMMUNITY_NAME))

create_community_table(SE_COMMUNITY_NAME)

#tree = ET.parse('Posts.xml')
#root = tree.getroot()

columns = schema_column_names(se_post_schema)
fields = ['?' for x in range(len(columns))]
query = "INSERT INTO {}_posts({}) VALUES({})".format(SE_COMMUNITY_NAME,
                                                    ', '.join(columns),
                                                    ', '.join(fields))
i = 0
failed = 0

for event, row in ET.iterparse('Posts.xml', events=("start", "end")):
    if event == 'start':
        continue

    if i < skipindex-1:
        if i % 100 == 0:
            print("Skipping... ({}/{})".format(i, skipindex), end="\r")
        i += 1
        row.clear()
        del row
        del event
        continue

    values = []
    for column in columns:
        current_column = row.get(column)
        if current_column:
            values.append(current_column)
        else:
            values.append("NULL")


    try:
        db.execute(query, values)
        i += 1
    except sqlite3.IntegrityError as e:
        failed += 1
        print(e)

    row.clear()
    del row
    del event

    try:
        if i % SAVE_EVERY == 0:
            print("Saving...{}".format(" " * 70), end="\r")
            conn.commit()
    except Exception:
        sys.exit(1)

    if i % 100 == 0:
        print("Succeeded: {:<8} | Failed: {:<8}".format(i, failed), end="\r")

conn.commit()
print("Wrote {} records to {}.sqlite3".format(i, SE_COMMUNITY_NAME))
print("Succeeded: {:<8} | Failed: {:<8}".format(i, failed))
conn.close()
