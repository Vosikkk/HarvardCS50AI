import sys
import math
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        for v in self.domains:
            inconsistent_values = [w for w in self.domains[v] if v.length != len(w)]
            for x in inconsistent_values:
                self.domains[v].remove(x)



    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        
        if overlap is None:
            return revised
        
        i, j = overlap

        to_remove = {
            word_x 
            for word_x in self.domains[x]
            if not any(
                word_x[i] == word_y[j] 
                for word_y in self.domains[y]
            )
        }

        
        if to_remove:
            self.domains[x].difference_update(to_remove)
            revised = True

        return revised    


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))
            
        return self.process_arcs(arcs)    



    def process_arcs(self, arcs):
        
        from collections import deque
        
        queue = deque(arcs)
       
        while queue:
            
            x, y = queue.popleft()

            if self.revise(x, y):
                
                if not self.domains[x]:
                    return False
                
                for z in self.crossword.neighbors(x) - {y}:
                   queue.append((z, x))

        return True    


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all(var in assignment for var in self.crossword.variables)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
       
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        
        for var in assignment:

            if (
                len(assignment[var]) != var.length or 
                self.conflict_with_neighbors(var, assignment)
            ):
                return False  
            
                        
        return True    
    


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        def count_conflicts(value):
            return sum(
                sum(
                    not self.check_overlap_consistency(
                        value, neighbor_value, 
                        overlap
                    )
                    for neighbor_value in self.domains[neighbor]
                )
                
                for neighbor in self.crossword.neighbors(var)
                
                if neighbor not in assignment and 
                   (overlap := self.crossword.overlaps[var, neighbor])
            )

        lcv = [(value, count_conflicts(value)) for value in self.domains[var]]    
        
        return [value for value, _ in sorted(lcv, key=lambda item: item[1])] 



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        def heuristic(var):
            return (len(self.domains[var]), -(len(self.crossword.neighbors(var))))  

        unassigned_value = [
            var for var in self.crossword.variables if var not in assignment
        ]           

        return min(unassigned_value, key=heuristic, default=None)            
                

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):

            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):  
                
                if self.ac3([(var, neighbor) for neighbor in self.crossword.neighbors(var)]):
                    result = self.backtrack(new_assignment)

                    if result is not None:
                        return result
                
        return None



    
    def check_overlap_consistency(self, value, neighbor_value, overlap):
        """
        Check if the overlap between var and neighbor is consistent.
        """
        
        return value[overlap[0]] == neighbor_value[overlap[1]]
                

    
    def conflict_with_neighbors(self, variable, assignment):
        """
        Check if `variable` conflicts with its neighbors in `assignment`.
        """

        return any(
            (overlap := self.crossword.overlaps[variable, neighbor]) and
            neighbor in assignment and  
            not self.check_overlap_consistency(
                    assignment[variable], 
                    assignment[neighbor],
                    overlap
                )
            for neighbor in self.crossword.neighbors(variable)        
        )


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
