from math import log2,ceil,floor
from random import randint, sample
import matplotlib.pyplot as plt
import time

import parameters



def nearest_even_number(x):
    """Returns the nearest even number"""
    result = round(x)
    if not result%2: return result
    if abs(result-1-x) > abs(result+1-x): return result - 1
    else: return result + 1



#Parameters
alphabet  = parameters.alphabet
numPop    = parameters.population
xRate     = parameters.slectionRate
mutRate   = parameters.mutateRate
numElite  = parameters.eliteChromosoms
itMax     = parameters.iterationMax
target    = parameters.targetString
precision = parameters.precisionMin
sameL     = parameters.sameLimit


numGen  = floor(log2(2*len(alphabet)-1))       #Number of bits encoding a gen
numVar  = len(target)                          #Number of gens in a chromosom
numBits = numGen*numVar                        #Number of bits in chromosom
numKeep = nearest_even_number(numPop*xRate)    #Number of chromosmes to keep after evaluation
numMut  = ceil(numPop*mutRate)                 #Number of gens to mutate



#ENCODING
def encode_alphabet():
    """Encodes whole alphabet where every charcater has its own list of bits"""
    encAlph={}
    for i in range(len(alphabet)):
        tmp=bin(i)[2:]
        while len(tmp) < numGen:
            tmp = '0' + tmp
        encAlph[alphabet[i]]=[int(x) for x in tmp]
    return encAlph

#Creating dictionary with the key:value pair for each character in the alphabet
encodedAlphabet=encode_alphabet()

def encode_gen(g):
    """Returns correspinding list of bits to given letter from encoded alphabet"""
    return encodedAlphabet[g]

def encode_chromosom(chrom):
    """Return list of lists of bits correspinding to given string"""
    return list(map(encode_gen,chrom))

def encode_population(pop):
    """Return list of lists of lists of bits correspinding to given strings"""
    return list(map(encode_chromosom,pop))



#DECODING
def decode_gen(g):
    """Returns letter from alphabet by its index"""
    tmp = sum([2**i*g[abs(i-len(g)+1)] for i in range(len(g)-1,-1,-1)])
    return alphabet[tmp]

def decode_chromosom(chrom):
    """Returns string of corresponding letters to given list"""
    return ''.join([decode_gen(g) for g in chrom])

def decode_population(pop):
    """Return list of strings"""
    return list(map(decode_chromosom,pop))



#GENERATING FIRST POPULATION
def random_bit():
    return randint(0,1)

def random_bits_list():
    """Generate random list of bits"""
    return [random_bit() for i in range(numGen)]

def random_gen():
    """Returns random character"""
    return decode_gen(random_bits_list())

def random_chromsom():
    "Returns random string"
    return ''.join([random_gen() for i in range(numVar)])

def radnom_population():
    """Generates random population"""
    return [random_chromsom() for i in range(numPop)]



#FUNCTIONALITY
def random_bit_index():
    """Generates random crossing point in bits list"""
    return randint(0,numGen-1)

def random_gen_index():
    """Generates random crossing point in gen string"""
    return randint(0,numVar-1)

def element_cost(a,b):
    if a == b: return 0
    else: return 1

def cost(a,b):
    """Return cost of the two iterable objects"""
    return sum([element_cost(a[i],b[i]) for i in range(len(a))])

def gen_cost(genA,genB):
    """Generates cost between two gens"""
    return cost(encode_gen(genA),encode_gen(genB))
    
def chromosom_pair_cost(tar, chrom):
    """Generates tuple of (cost,chromsom) (cost tells how the chromosom differs from the target chromosom)"""
    return (sum([gen_cost(tar[i],chrom[i]) for i in range(numVar)]), encode_chromosom(chrom))

def evaluate_population(pop):
    """Evaluates entire population"""
    return [chromosom_pair_cost(target,chrom) for chrom in pop]

def sort_tuples(evPop):
    """Sort chromosom by cost"""
    evPop.sort(key=lambda x: x[0])

def elite_chromosom(evPop):
    """Chosing the best chromosoms"""
    return [evPop[i][1] for i in range(numElite)]

def select_parenst(evPop):
    """Selecting parents"""
    elChrom=elite_chromosom(evPop)
    par=[evPop[i][1] for i in range(numElite, numKeep)]
    return elChrom+par

#Crossover
def crossover(a,b,idx):
    newA=a[:idx]+b[idx:]
    newB=a[idx:]+b[:idx]
    return [newA,newB]

#Mating
def mate(a,b):
    """Functions corssover genes of the chromosm and then crossover bits of every gene in chromosm"""
    tmpC=crossover(a,b,random_gen_index())                  #crossing gens in chromosoms
    newA=tmpC[0]
    newB=tmpC[1]
    newChromA=[]
    newChromB=[]
    for i in range(numVar):
        tmpG=crossover(newA[i],newB[i],random_bit_index())  #crossing bits in gens
        newChromA.append(tmpG[0])
        newChromB.append(tmpG[1])
    return [newChromA,newChromB]

#Children generation
def children_gen(pop):
    """Function generates two childen for every pair of parents"""
    tmp=[]
    for i in range(0,numKeep,2):
        tmp+=mate(pop[i],pop[i+1])
    return tmp

#Mutate
def mutate_bit(b):
    if b == 1: return 0
    else: return 1

def mutate_gen(g):
    """Choosing random bit in gen"""
    idx=random_bit_index()
    g[idx]=mutate_bit(g[idx])
    return g

def mutate_chromosom(chrom):
    """Choosing random gen chromosm"""
    idx=random_gen_index()
    chrom[idx]=mutate_gen(chrom[idx])
    return chrom

def mutate(pop):
    """Mutate random chromosm in the population of children"""
    idx=sample(range(len(pop)),numMut)
    for i in idx: pop[i]=mutate_chromosom(pop[i])



if __name__ == '__main__':

    #Generating first population
    popultion=radnom_population()
    firstPopulation=popultion

    bestSolutions=[]
    notFind=True
    result=None

    last_ptr=None
    first=True
    same_cost=sameL

    start=time.time()
    for i in range(itMax):

        #Evaluation and sorting population
        evaluatedPopulation=evaluate_population(popultion)
        sort_tuples(evaluatedPopulation)

        bestSolutions.append(evaluatedPopulation[0][0])
        result=(i,evaluatedPopulation[0])

        if first:                                       #To reduce the time of processing we can set the
            last_ptr=evaluatedPopulation[0][0]          #maximum number of iterations after which if the  
            first=False                                 #GA does not find better solution it will stop
        else:
            if last_ptr == evaluatedPopulation[0][0]:
                same_cost-=1
                if same_cost == 0:
                    print("There has been no change in best solutions in the last {} iterations".format(sameL))
                    end=time.time()
                    break
            else:
                last_ptr=evaluatedPopulation[0][0]
                same_cost=sameL

        if evaluatedPopulation[0][0] <= precision:
            notFind=False
            break

        #Selecting choromosms to mate and replacing old poplation with the new one
        parents=select_parenst(evaluatedPopulation)
        children=children_gen(parents)
        mutate(children)
        popultion=parents+children
        popultion=decode_population(popultion)
    end=time.time()



    if notFind:
        print("GA could not find solution")
        print("Best result | cost: {}\tchromosom: {}".format(result[1][0],decode_chromosom(result[1][1])))
    else:
        print('Iteration: ', result[0])
        

    print("Target: ",target)
    print('Time: ',end-start)
    print("\nFirst population: \n",firstPopulation)
    print("\nLast population: \n",popultion)


    plt.plot(range(i+1),bestSolutions)
    plt.xlabel('Iteration')
    plt.ylabel('Difference')
    plt.title(target,fontsize=20)
    plt.savefig('plot.png')