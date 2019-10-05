from collections import defaultdict


def check_key(key, item_dict):
    for k, v in item_dict.items():
        if k == key:
            return True
    else:
        return False


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.visited = {}
        self.recStack = {}

    def addEdge(self, u, v):
        if not v in self.graph[u]:
            self.visited[u] = False
            self.visited[v] = False
            self.recStack[u] = False
            self.recStack[v] = False
            self.graph[u].append(v)

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        if check_key(v, self.graph):
            for neighbour in self.graph[v]:
                if not visited[neighbour]:
                    if self.isCyclicUtil(neighbour, visited, recStack):
                        return True
                elif recStack[neighbour]:
                    return True

        # The node needs to be poped from
        # recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        for k, v in self.graph.items():
            if not self.visited[k]:
                if self.isCyclicUtil(k, self.visited, self.recStack):
                    return True
        return False


# g = Graph()
# g.addEdge('sazal', 'farhad')
# g.addEdge('sazal', 'ashik')
# g.addEdge('farhad', 'sumon')
# g.addEdge('farhad', 'tashfik')
# g.addEdge('ashik', 'shakil')
# g.addEdge('ashik', 'sumon')
#
# if g.isCyclic() == 1:
#     print("Graph has a cycle")
# else:
#     print("Graph has no cycle")
