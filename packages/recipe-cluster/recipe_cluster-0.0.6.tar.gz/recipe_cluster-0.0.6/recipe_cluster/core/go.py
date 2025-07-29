class GO:
    def __init__(self, ID, features):
        self.ID = ID
        self.D = features
        self.name = features['name']

    def __repr__(self):
        return '{} - <{}>'.format(self.ID, self.name)

    def __eq__(self, other):
        return self.ID == other.ID

    def __hash__(self):
        return hash(self.ID)

    @staticmethod
    def extract_GO_id_from_list(l):
        if isinstance(l,list):
            return [i.split('|')[0] for i in l]
        else:
            return None
    
    @staticmethod
    def read_GO_obo(infile): # TODO: throw errors 
        terms = {}
        with open(infile,'r') as f:
            for line in f:
                tDict = {}
                line = line.strip()
                if line == "[Term]":
                    line = f.readline().strip().split(': ')
                    while not line == ['']:
                        tDict[line[0]] = ''.join(line[1:])
                        line = f.readline().strip().split(': ')
                    for k,v in tDict.items():
                        k = k.strip()
                        v = v.strip()
                        tDict[k] = v
                    terms[tDict['id']] = GO(tDict['id'], tDict)
        return terms
