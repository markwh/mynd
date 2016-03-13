## Utility scripts for mindmapping

### mynd.py

Prune and merge mindmaps using node icons. For use with Freeplane/Docear mindmap (.mm) files.

#### Examples

1. Prune away branches that contain no checked nodes

	- And save in place: `mynd.py map1
	- And save as a new file: `mynd.py -w newmap.mm map1`
	- And merge with an existing map: `mynd.py -m mastermap1.mm map1`

Starting map: ![](examples/images/map_pre.png)

Pruned map: ![](examples/images/map_post1.png)

Starting master map: ![](examples/images/master1_pre.png)

Master map merged with new checked nodes ![](examples/images/master1_post.png)

2. Prune away checked branches to leave only unchecked nodes

	- And save in place: `mynd.py -u map1`
	- And save as a new file: `mynd.py -u -w newmap.mm map1`
	- And merge with an existing map: `mynd.py -u -m mastermap2.mm map1`

Starting map: ![](examples/images/map_pre.png)

Pruned map: ![](examples/images/map_post2.png)

Starting master map: ![](examples/images/master2_pre.png)

Master map merged with new checked nodes ![](examples/images/master2_post.png)