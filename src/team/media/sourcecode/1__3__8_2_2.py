from_set= {} #a,b: a to b
to_set= {} #b,a: a to b
nodes = set()

def convert(a):
    if ord(a)>=97:#lower
        return ord(a)-ord('a')
    else:
        return ord(a)-ord('A')+26

def cycle(current, visited, onpath):
    onpath[current]=1 # true
    visited[current]=1
    print("visiting ",current)
    if from_set.get(current):
        for node in from_set.get(current):
            print("from",current,"visit",node)
            if onpath[node]==1:
                print(node,"onpath!!")
                return True
            if visited[node]==1:
                print(node,"visited")
                continue
            if cycle(node,visited,onpath):
                return True
    
    print(current,"not on cycle path")
    onpath[current]=0
    return False
    
def all_cycle(start,in_cycle):
    if start in from_set:
        print("start from",start,"to",from_set.get(start))
        for node in from_set.get(start):
            if node not in in_cycle:
                in_cycle.add(node)
                if all_cycle(node,in_cycle):
                    return True
            else:
                if len(in_cycle)==len(nodes):
                    return True
    return False
    
def isDAG(edges):
    
    error=False
    code=-6
    for edge in edges:
        if len(edge[0])!=1 or len(edge[1])!=1:
            error=True
            if code<-5:
                code=-5
        e=[0,0]
        e[0]=convert(edge[0])
        e[1]=convert(edge[1])
        if (ord(edge[0])<65 or (ord(edge[0])>90 and ord(edge[0])<97) or ord(edge[0])>122) or (ord(edge[1])<65 or (ord(edge[1])>90 and ord(edge[1])<97) or ord(edge[1])>122) or (e[0]<0 or e[0]>52 or e[1]<0 or e[1]>52):
            error=True
            if code<-5:
                code=-5
        nodes.add(e[0])
        nodes.add(e[1])
        if e[0] in from_set:
            if e[1] in from_set.get(e[0]):
                error=True
                if code<-4:# duplicate
                    code=-4
            else:
                from_set[e[0]].append(e[1])
        else:
            from_set[e[0]]=[]
            from_set[e[0]].append(e[1])
        # to set
        if e[1] in to_set:
            if e[0] in to_set.get(e[1]):
                error=True
                if code<-4:
                    code=-4
            else:
                to_set[e[1]].append(e[0])
        else:
            to_set[e[1]]=[]
            to_set[e[1]].append(e[0])
    print(nodes)     
    print(from_set)
    print(to_set)
    if len(nodes)>52:
        error=True
        if code<-5:
            code=-5
    # find a start
    start=-1
    for node in from_set:
        if node not in to_set:# is a start (maybe one of)
            if start>-1:
                error=True
                if code<-2:
                    code=-2
                break
            else:
                start=node
            
    # detect cycle
    visited = [0]*52
    onpath=[0]*52
    for node in nodes:
        if cycle(node,visited,onpath):
            error=True
            if code<-3:
                code=-3
            # check if all nodes in a cycle, when cycle=true
            in_cycle=set()
            in_cycle.add(node)
            if all_cycle(node,in_cycle):
                code=-1
            break
    if error:
        return code
    
    for key in to_set:
        if len(to_set.get(key))>1:
            return 1
    return 0
            
        
