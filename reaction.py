"""Implementation of Lynch-Willet algorithm."""

from rdkit import Chem
from chemical import Chemical


class Reaction:
    """A class representing a chemical reaction."""

    def __init__(self, smiles):
        self.reactant_smiles, self.product_smiles = smiles.split('>>')
        try:
            self.reactant = Chemical(self.reactant_smiles)
        except ValueError:
            raise ValueError("Invalid reactant SMILES")

        try:
            self.product = Chemical(self.product_smiles)
        except ValueError:
            raise ValueError("Invalid product SMILES")

    def find_core(self):
        """Extracts a reaction core.

        Function uses the Lynch-Willet algorithm to detect the reaction center.
        """

        while True:
            # Assign initial EC values to the reactant and the product.
            next_reactant_ecs = self.reactant.init_ecs()
            next_product_ecs = self.product.init_ecs()

            # Calculate higher order ECs until there are NO pairs of atoms for
            # which $EC_{r_{i}}^{n} = EC_{p_{j}}^{n}$.
            while set(next_reactant_ecs).intersection(next_product_ecs):
                # Save current sets of ECs of the reactant and product.
                prev_reactant_ecs = list(next_reactant_ecs)
                prev_product_ecs = list(next_product_ecs)

                # Calculate test set of ECs for reactant and product.
                next_reactant_ecs = self.reactant.increment_ecs()
                next_product_ecs = self.product.increment_ecs()

            # Find out EC-based maximal common substructure (EC-MCS).
            reactant_ec_mcs = set([])
            product_ec_mcs = set([])

            # Create maps between EC and atom indices for both product and
            # reactant.
            reactant_map = self.make_ec_map(prev_reactant_ecs)
            product_map = self.make_ec_map(prev_product_ecs)
            common_ecs = set(reactant_map).intersection(product_map)
            if not common_ecs:
                break

            for ec in common_ecs:
                for idx in reactant_map[ec]:
                    reactant_ec_mcs.update(self.reactant.find_ec_mcs(idx))
                for idx in product_map[ec]:
                    product_ec_mcs.update(self.product.find_ec_mcs(idx))

            # Delete all atoms in EC-MCS from the reactant and the product.
            self.reactant.remove_atoms(reactant_ec_mcs)
            self.product.remove_atoms(product_ec_mcs)

        return '>>'.join([Chem.MolToSmiles(self.reactant.mol),
                          Chem.MolToSmiles(self.product.mol)])

    def make_ec_map(self, ecs):
        """Returns a map between atoms ECs and their indices.

        Creates and returns a dictionary which keys are the EC indices and
        corresponding values are lists of atom indices with a given EC.
        """
        ec_map = {}
        for idx, ec in enumerate(ecs):
            ec_map.setdefault(ec, []).append(idx)
        return ec_map


if __name__ == '__main__':
    smarts = 'CC(=O)CC(C)C(CC#N)C(=O)N>>CC(=O)CC(C)C(CC#N)C#N'
    rxn = Reaction(smarts)
    # Should print something like N#CC.C(=O)N>>N#CC.N#C
    print rxn.find_core()
