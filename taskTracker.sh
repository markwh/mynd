#!/bin/bash

##
# Functions
##

# Get all text specifying checked nodes
get_checked_nodes_1 () {
  xmlstarlet sel -t -c '/map/node/node[icon/@BUILTIN="checked"]' $1
}

get_structure () {
  xmlstarlet el -v $1
}

get_checked_nodes_2 () {
  xmlstarlet sel -t -c '/map/node/node[node/icon/@BUILTIN="checked"]' $1
}

get_checked_nodes_3 () {
  xmlstarlet sel -t -c '/map/node/node/node[node/icon/@BUILTIN="checked"]' $1
}

# Identify all parent nodes of all checked nodes



# Merge into completed tasks file, beginning with highest parent

# tests
#get_checked_nodes_1 ../20160116Weekend.mm
get_structure ../20160116Weekend.mm
