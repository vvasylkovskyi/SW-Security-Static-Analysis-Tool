from analysis.reaching_definition_analysis import ReachingDefinitionsAnalysis


class FixedPointAnalysis():
    """Run the fix point analysis."""

    def __init__(self, cfg):
        """Fixed point analysis
        analysis must be a dataflow analysis containing a 'fixpointmethod' method that analyzes one CFG node"""
        self.analysis = ReachingDefinitionsAnalysis()
        self.cfg = cfg
        # print("HERE")
        self.fixpoint_runner()

    def constraints_changed(self):
        """Return true if any constraint has changed."""
        return any(node.old_constraint != node.new_constraint for node in self.cfg.nodes)

    def swap_constraints(self):
        """Set odl constraint to new constraint and set new constraint to None."""
        for node in self.cfg.nodes:
            # print("Swap constraints: ", node)
            # print("Old Constraints: ", node.old_constraint)
            # print("New Constraints: ", node.new_constraint)
            node.old_constraint = node.new_constraint
            node.new_constraint = None

    def fixpoint_runner(self):
        """Runs the fixpoint algorithm."""
        self.fixpoint_iteration()
        while self.constraints_changed():
            print("Iteration")
            self.swap_constraints()
            self.fixpoint_iteration()

    def fixpoint_iteration(self):
        """A fixpoint iteration."""
        for node in self.cfg.nodes:
            self.analysis.fixpointmethod(node)
