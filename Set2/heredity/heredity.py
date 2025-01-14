import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0, # 0.1  
                False: 0 # 0.3 sum 0.4  
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    
    probability = 1

    for person, data in people.items():
        
        mother = data['mother']
        father = data['father']

        copy = copy_of_gene(person, one_gene, two_genes) 
        

        if mother is None and father is None:
            gene_prob = PROBS["gene"][copy]

        else:
            
            gene_prob = gene_probability(
                inheritance_probability(father, one_gene, two_genes), 
                inheritance_probability(mother, one_gene, two_genes),
                copy
            )
        
        
        probability *= gene_prob * PROBS["trait"][copy][person in have_trait]

    

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    
    for person in probabilities:

        probabilities[person]["gene"][
            copy_of_gene(person, one_gene, two_genes)
        ] += p
        
        probabilities[person]["trait"][person in have_trait] += p 

        

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        normalize_distribution(probabilities[person]["gene"])
        normalize_distribution(probabilities[person]["trait"])



def normalize_distribution(distribution):
    """
    Normalize a single probability distribution such that its values sum to 1.
    """

    total = sum(distribution.values())

    for key in distribution:
        distribution[key] /= total



def gene_probability(dad, mom, g):
    """
    Calculates the probability that a child will have a specific number of gene copies. 
    """

    prob = 0

    if g == 2:
        prob = dad * mom
    elif g == 1:
        prob = mom * (1 - dad) + dad * (1 - mom)
    else:
        prob = (1 - dad) * (1 - mom) 
    
    return prob
    


def inheritance_probability(parent, one_gene, two_gene):
    """
    Calculates the probability that a parent passes a gene to their child.
    """
    
    prob = 0

    if parent in two_gene:
        prob = 1 - PROBS["mutation"]
    
    elif parent in one_gene:
        prob = 0.5
    
    else:
        prob = PROBS["mutation"]

    return prob
    
    

def copy_of_gene(person, one, two):
    """
    Determines how many copies of a gene a person has.
    """

    gene = 0

    if person in two:
        gene = 2

    elif person in one:
        gene = 1

    return gene    



if __name__ == "__main__":
    main()
