from src.search_algorithms import SearchProblem, run_search

def test_algorithms_find_goal():
    p=SearchProblem((0,0,0),{(2,3,1)},5)
    for name in ("BFS","DFS","A*"):
        r=run_search(p,name)
        assert r.state==(2,3,1)
        assert r.expanded>0
