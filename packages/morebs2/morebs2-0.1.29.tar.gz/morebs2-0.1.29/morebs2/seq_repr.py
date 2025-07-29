from .matrix_methods import * 
from copy import deepcopy

"""
given: a sequence S, either an np.array or a list 
output: sequence S' corresponding to `S`. Every 
    element of S' is a pair of the form 
    [0] value v of S at the j'th index 
    [1] number of contiguous indices, from the 
        j'th index in increasing order, with 
        values that equal v. 

EX: 
S = <0,0,1,2,1,2,3,3,4,4,4>
S' = <(0,2),(1,1),(2,1),(1,1),(2,1),(3,2),(4,2)> 
"""
def contiguous_repr__sequence(S):
    assert is_vector(S) or type(S) == list
    assert len(S) > 0

    q = [[S[0],1]]
    ref = q[-1]

    for i in range(1,len(S)):
        if S[i] == ref[0]:
            ref[1] += 1
        else:
            ref_ = [S[i],1]
            q.append(ref_) 
            ref = ref_
    return q

def contiguous_repr_size(S,size_type):
    return -1 

"""
V is a vector of (value,frequency) pairs 
assumed to be sorted in ascending or descending 
order. Function finds the sequence of all 
(value,frequency) pairs that tie for a place 
in the ranking of frequency. 
"""
def valuefreq_pair_vector__nth_place(V,i=0):

    j = None

    ip = 0
    ref = V[0]
    seq = []
    for i_ in range(1,len(V)):
        if ip == i:
            if ref[1] != V[i_][1]:
                break
            else: 
                seq.append(V[i_][0]) 
            continue
    
        if ref[1] != V[i_][1]:
            ip += 1 
            ref = V[i_] 
    return seq

def valuefreq_pair_vector_to_tie_partition(V):

    j = None
    ip = 0
    ref = V[0]
    seqs = []
    seq = []
    for i_ in range(1,len(V)):
        if ref[1] != V[i_][1]:
            ip += 1 
            ref = V[i_] 
            seqs.append(seq) 
            seq = [V[i_][0]]
        else: 
            seq.append(V[i_][0]) 
    return seqs 

"""
most common contiguous subsequence search 
"""
class MCSSearch:

    def __init__(self,L,cast_type=int,is_bfs:bool=True):  
        assert type(L) == list or is_vector(L) 
        assert type(is_bfs) == bool
        self.l = np.array(L)  
        self.cast_type = cast_type 
        self.is_bfs = is_bfs 

        self.preproc()
        # stringized subsequence of L --> index list of occurrence 
        self.subseq_occurrences = defaultdict(list) 
        self.key_queue = [] 
        self.key_cache = []
        return
    
    def preproc(self):
        self.d2index = defaultdict(list) 
        for (i,l_) in enumerate(self.l):
            self.d2index[l_].append(i) 
    
    def most_frequent_(self):
        q = sorted([(k,len(v)) for k,v in self.d2index.items()],key=lambda x:x[1],reverse=True) 

        q_ = q.pop(0)   
        s = set() 
        s |= {q_[0]} 
        while len(q) > 0:
            q2_ = q.pop(0) 
            if q2_[1] != q_[1]:
                break 
            s |= {q2_[0]} 
        return s 
    
    """
    post-search main method 
    """
    def mcs(self):
        x = [(k,len(v)) for k,v in self.subseq_occurrences.items()] 
        x = sorted(x,key=lambda x:x[1])
        q = x.pop(-1)
        s = [string_to_vector(q[0],castFunc=self.cast_type)]
        while len(x) > 0:
            q_ = x.pop(-1)
            if q_[1] == q[1]:
                s_ = string_to_vector(q_[0],castFunc=self.cast_type)
                s.append(s_)
            else: 
                break 
        return s 

    def mcs_nth(self,i=0): 
        x = [(k,len(v)) for k,v in self.subseq_occurrences.items()] 
        x = sorted(x,key=lambda x_:x_[1],reverse=True)
        return valuefreq_pair_vector__nth_place(x,i)
    
    def init_search(self):

        self.subseq_occurrences.clear() 
        self.key_queue.clear()
        self.key_cache.clear() 

        #ss = sorted(self.most_frequent())
        ss = sorted(set(np.unique(self.l)))

        for ss_ in ss: 
            v = self.d2index[ss_] 
            ssv = vector_to_string([ss_],castFunc=self.cast_type)
            self.subseq_occurrences[ssv] = v
            self.key_queue.append(ssv)  
        return
    
    def __next__(self):
        if len(self.key_queue) == 0: 
            return False 
        
        x = self.key_queue.pop(0)
        q = self.extend_subseq(x) 

        self.key_cache.append(x) 

        # sort q by frequency
        q_ = []
        for q2 in q:
            v = self.subseq_occurrences[q2] 
            q_.append((q2,v)) 
        q_ = sorted(q_,key=lambda x:x[1],reverse=True)  
        q_ = [q2[0] for q2 in q_] 

        if self.is_bfs:
            self.key_queue.extend(q_)
        else:
            while len(q_) > 0:
                self.key_queue.insert(0,q_.pop(-1)) 
        return True 

    def extend_subseq(self,subseq_str): 
        q = self.subseq_occurrences[subseq_str] 
        subseq_base = string_to_vector(subseq_str,castFunc=self.cast_type)
        new_subseq_ = set() 
        for q_ in q:
            # get the next index
            i = len(subseq_base) + q_ 

            if i >= len(self.l): continue

            subseq = deepcopy(subseq_base) 
            subseq = np.append(subseq,self.l[i])

            subseq_str_ = vector_to_string(subseq,castFunc=self.cast_type) 
            self.subseq_occurrences[subseq_str_].append(q_)  
            new_subseq_ |= {subseq_str_}
        return new_subseq_ 
    
    """
    pre-search main method 
    """
    def search(self):
        self.init_search() 

        stat = True 
        while stat: 
            stat = self.__next__()
        return 