## Utility scripts for mindmapping

### syncmm.py

Prune and merge mindmaps using node icons.

#### Examples

1. Prune away branches that contain no checked nodes

	- And save in place: `syncmm.py map1`
	- And save as a new file: `syncmm.py -w newmap.mm map1`
	- And merge with an existing map: `syncmm.py -m mastermap1.mm map1`

2. Prune away checked branches to leave only unchecked nodes

	- And save in place: `syncmm.py -u map1`
	- And save as a new file: `syncmm.py -u -w newmap.mm map1`
	- And merge with an existing map: `syncmm.py -u -m mastermap2.mm map1`