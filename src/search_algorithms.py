from collections import deque
from dataclasses import dataclass
from heapq import heappush, heappop
from itertools import count
from time import perf_counter
from typing import Optional, Tuple

State = Tuple[int, int, int]

@dataclass
class SearchResult:
    algorithm: str
    state: Optional[State]
    path: list
    cost: float
    expanded: int
    generated: int
    time_ms: float

class SearchProblem:
    """Problema de agenda: estado=(desplazamiento_dia, indice_hora, indice_veterinario)."""
    def __init__(self, initial, goals, max_day, slots=7, vets=3):
        self.initial, self.goals, self.max_day = initial, set(goals), max_day
        self.slots, self.vets = slots, vets
    def is_goal(self, state): return state in self.goals
    def valid(self, state):
        d,h,v=state
        return 0 <= d <= self.max_day and 0 <= h < self.slots and 0 <= v < self.vets
    def neighbors(self, state):
        d,h,v=state
        candidates=[((d+1,h,v),2),((d,h+1,v),1),((d,h,v+1),1.5),
                    ((d,h-1,v),1),((d,h,v-1),1.5),((d-1,h,v),2)]
        return [(s,c) for s,c in candidates if self.valid(s)]
    @staticmethod
    def metric(a,b): return 2*abs(a[0]-b[0])+abs(a[1]-b[1])+1.5*abs(a[2]-b[2])
    def heuristic(self,state): return min((self.metric(state,g) for g in self.goals),default=0)

def rebuild(parent, goal):
    path=[]
    while goal is not None: path.append(goal); goal=parent[goal]
    return path[::-1]

def run_search(problem, algorithm):
    start=perf_counter(); parent={problem.initial:None}; g={problem.initial:0.0}; expanded=0; generated=1
    if algorithm=='BFS': frontier=deque([problem.initial])
    elif algorithm=='DFS': frontier=[problem.initial]
    elif algorithm=='A*': frontier=[]; serial=count(); heappush(frontier,(problem.heuristic(problem.initial),next(serial),problem.initial))
    else: raise ValueError('Algoritmo no soportado')
    closed=set()
    while frontier:
        if algorithm=='BFS': state=frontier.popleft()
        elif algorithm=='DFS': state=frontier.pop()
        else:
            _,_,state=heappop(frontier)
            if state in closed: continue
            closed.add(state)
        expanded += 1
        if problem.is_goal(state):
            return SearchResult(algorithm,state,rebuild(parent,state),g[state],expanded,generated,(perf_counter()-start)*1000)
        neighbors=problem.neighbors(state)
        if algorithm=='DFS': neighbors=reversed(neighbors)
        for nxt,cost in neighbors:
            ng=g[state]+cost
            if algorithm in ('BFS','DFS'):
                if nxt not in parent:
                    parent[nxt]=state; g[nxt]=ng; frontier.append(nxt); generated+=1
            elif ng < g.get(nxt,float('inf')):
                if nxt not in g: generated+=1
                parent[nxt]=state; g[nxt]=ng
                heappush(frontier,(ng+problem.heuristic(nxt),next(serial),nxt))
    return SearchResult(algorithm,None,[],float('inf'),expanded,generated,(perf_counter()-start)*1000)
