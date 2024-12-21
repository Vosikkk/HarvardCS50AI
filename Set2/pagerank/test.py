from pagerank import transition_model 

corpus = {
    "1.html": {"2.html", "3.html"},
    "2.html": {"3.html"},
    "3.html": {}
}

def test_transition_model():
    res = transition_model(corpus, '3.html', 0.85)
    print(res)





test_transition_model()