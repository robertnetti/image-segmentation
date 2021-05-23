# Initialize Component Class
class Components:
    def __init__(self, num_pixels):
        self.parent = [i for i in range(num_pixels)]
        self.comp_rank = [0 for i in range(num_pixels)]
        self.comp_size = [1 for i in range(num_pixels)]
        self.num_comp = num_pixels

    # return the size of a component
    def get_size(self, vertex_id):
        return self.comp_size[vertex_id]

    # return the parent of a vertex recursively
    def get_parent(self, vertex_id):
        if self.parent[vertex_id] == vertex_id:
            return vertex_id

        self.parent[vertex_id] = self.get_parent(self.parent[vertex_id])
        return self.parent[vertex_id]

    # merge two components
    def merge_comps(self, v1, v2):
        c1 = self.get_parent(v1)
        c2 = self.get_parent(v2)

        # if the components don't share the same parent...
        if c1 != c2:
            # if c1's rank is higher than c2's swap their values
            if self.comp_rank[c1] > self.comp_rank[c2]:
                c1, c2 = c2, c1

            # set c1's parent to be c2
            self.parent[c1] = c2

            # set c2's size by summing the size of both components
            self.comp_size[c2] += self.comp_size[c1]

            # if c1 has the same rank as c2 increment c2's rank by 1
            if self.comp_rank[c1] == self.comp_rank[c2]:
                self.comp_rank[c2] += 1

            # after merging, decrease the number of components by 1
            self.num_comp -= 1
