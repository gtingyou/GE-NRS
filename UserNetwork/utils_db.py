#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 21:54:11 2020

@author: gtingyou
"""

import sqlite3
import argparse


def create_nodes_table(database_name):
    conn = sqlite3.connect(database_name)
    conn.execute('''CREATE TABLE NODES
                 (NewsIndex TEXT,
                 ParseDate TEXT,
                 NewsURL TEXT,
                 NewsDate TEXT,
                 NewsTitle TEXT,
                 NewsContext TEXT);''')
    conn.close()


def create_edges_table(database_name):
    conn = sqlite3.connect(database_name)
    conn.execute('''CREATE TABLE EDGES
                 (News1 TEXT,
                 News2 TEXT,
                 ParseDate TEXT);''')
    conn.close()
                 
                 
def insert_nodes_table(database_name, nodes):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    for n in nodes:
        cur.execute("INSERT INTO NODES (NewsIndex,ParseDate,NewsURL,NewsDate,NewsTitle,NewsContext) VALUES (?,?,?,?,?,?)", n)
    conn.commit()
    conn.close()

def insert_edges_table(database_name, edges):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    for e in edges:
        cur.execute("INSERT INTO EDGES (News1,News2,ParseDate) VALUES (?,?,?)", e)
    conn.commit()
    conn.close()


def select_nodes_table(database_name, ParseDate):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    myresult = cur.execute("SELECT NewsIndex,NewsContext,NewsTitle FROM NODES WHERE ParseDate==?", (ParseDate,))
    result = []
    for row in myresult:
        result.append(row)
    conn.close()    
    return result

def select_edges_table(database_name, ParseDate):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    myresult = cur.execute("SELECT News1,News2 FROM EDGES WHERE ParseDate==?", (ParseDate,))
    result = []
    for row in myresult:
        result.append(row)
    conn.close()        
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get news browsing history.')
    parser.add_argument('--db_path', '-n', required=True, help='Database name')
    args = parser.parse_args()

    create_nodes_table(args.db_path)
    create_edges_table(args.db_path)

