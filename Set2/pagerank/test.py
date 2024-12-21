from pagerank import sample_pagerank 

corpus = {
    "1.html": {"2.html", "3.html"},
    "2.html": {"3.html"},
    "3.html": {"2.html"}
}

def test_transition_model():
    res = sample_pagerank(corpus, 0.85, 100000)
    print(res)





test_transition_model()