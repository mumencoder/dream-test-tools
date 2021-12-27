
#include "include/interface.dmf"
#include "include/map_one.dmm"
#include "include/test_common.dm" 

/datum/tree_node
  var/left
  var/right

/proc/test()
  var/min_depth = 4
  var/max_depth = text2num(file2text("binary-tree.input"))
  if (max_depth < min_depth)
    max_depth = min_depth + 2

  var/stretch_tree = create_tree(max_depth+1)
  world.log << "stretch tree of depth [max_depth+1] check: [tree_checksum(stretch_tree)]"
  del stretch_tree

  var/long_lived_tree = create_tree(max_depth)
  for (var/cdepth = min_depth; cdepth < max_depth, cdepth += 2)
    var/iters = 1 << (max_depth - cdepth + min_depth)
    var/checksum = 0
    for(var/i = 1; i <= iters; i++)
      var/datum/tree_node/tree = create_tree(cdepth)
      checksum += tree_checksum(tree)
    world.log << "[iters] trees of depth [cdepth] check: [checksum]"

  world.log << "long lived tree of depth [max_depth] check: [tree_checksum(long_lived_tree)]"

/proc/create_tree(depth)
  var/datum/tree_node/root = new /datum/tree_node
  if (depth > 0)
    root.left = create_tree(depth - 1)
    root.right = create_tree(depth - 1)
  else
    root.left = null
    root.right = null
  return root

/proc/tree_checksum(datum/tree_node/root)
  if (root.left)
    return tree_checksum(root.left) + tree_checksum(root.right) + 1
  else
    return 1


