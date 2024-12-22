import os
import random
import re
import sys
from collections import defaultdict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    num_links = len(corpus[page]) 
    if num_links > 0:
 
        prob = {
            link: (1 - damping_factor) /
                    len(corpus)
            
            for link in corpus
        }
        
        for link in corpus[page]:
            prob[link] += damping_factor / num_links
    else:
        prob = {
            link: 1 / len(corpus) 
            
            for link in corpus
        }

    return prob    




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    start_page = random.choice(list(corpus.keys()))
    page_visits = defaultdict(int)

    for _ in range(n):
        
        page_visits[start_page] += 1
        
        prob = transition_model(corpus, start_page, damping_factor)
        
        start_page = random.choices(
            list(prob.keys()), weights=prob.values(), 
            k=1)[0]

    return {
        page: page_visits[page] / n 
        
        for page in corpus
    }
    

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    total_pages = len(corpus)
    
    page_rank = {
        page: 1 / total_pages
        for page in corpus
    }
    
    
    
    while True:

        new_page_rank = {}
        
        # Calculate sum of all ranks of empty pages
        rank_leak = sum(
            page_rank[page] 
            for page in corpus 
            if not corpus[page]
        )
        
        # Calculate how many rank they give for each page 
        # As we know, empty page has links for all pages 
        rank_leak_contrib = damping_factor * rank_leak / total_pages

        for page in corpus:
            
            new_rank = (
                ((1 - damping_factor) / 
                total_pages) + 
                rank_leak_contrib
            )
            
            for other_page in corpus:
                
                if page in corpus[other_page]:
                    new_rank += (
                        damping_factor * page_rank[other_page] / 
                        len(corpus[other_page])
                    )
        
            new_page_rank[page] = new_rank

            
        if all(
            abs(new_page_rank[page] - page_rank[page]) < 0.001
            for page in corpus
        ):
            break

    
        page_rank = new_page_rank

    return page_rank


if __name__ == "__main__":
    main()
