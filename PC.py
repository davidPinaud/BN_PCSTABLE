import pyAgrum as gum
from itertools  import product,combinations

class PC():
    def __init__(self,n : int) -> None:
        self.G,self.sepSet=self.initialisation(n)
        
    def initialisation(self,n:int):
        """initialise l'algorithme PC : 
        Parameters
        ----------
        n : int
            nombre de noeuds dans le BN

        Returns
        -------
        Mixed Graph et Dict
            un graphe G complet non orienté et
            un dictionnaire d'ensemble séparant vides pour toutes paires de neouds
        """        
        G=gum.MixedGraph()
        G.addNode(n)
        sepSet=dict()
        for node1,node2 in list(product(self.G.nodes(),self.G.nodes())): #produit cartésien de G.nodes
            G.addEdge(node1,node2)
            sepSet[(node1,node2)]=[]
        return G,sepSet
    
    def phase1(self):
        """ Phase 1 de l'algorithme PC
        """        
        d=0
        ConditionOnAdjX=True
        while ConditionOnAdjX:
            for X,Y in self.G.edges():  # Ligne 5 :
                adjX=self.G.adjacents(X)# foreach arête X-Y tq |Adj(X)\{Y}|≥d
                if len(adjX)-1 >=d:     #
                    adjSansY=adjX.copy()                     # Ligne 6,7 et 12 :
                    adjSansY.remove(Y)                       # Choisir un Z in Adj(X)\{Y} tq |Z|=d
                    for Z in list(combinations(adjSansY,d)): # until tous les Z de taille d ont été testés
                        if(True): #TODO : si X indep Y | Z
                            self.G.eraseEdge(X,Y)
                            self.sepSet[(X,Y)].append(Z)
                            break
            d+=1
            compteur=0
            for X in self.G.nodes():            # Ligne 14
                if len(self.G.adjacents(X))<=d: #
                    compteur+=1                 # compter pour combien de X |Adj(X)|≤d
            if(len(self.G.nodes())==compteur):  # Si tous les noeuds vérifie on arrête
                ConditionOnAdjX=False           #

    def phase2(self):
        pass

    def findUnshieldedTriple(self)->list:
        triple=[]
        for node in self.G.nodes():
            pass
        return triple
            

                    


if __name__== "__main__":
    G=gum.MixedGraph()
    #G.addNodes(5)
    #G.addEdge(0,1)
    #G.addEdge(1,2)
    #G.addArc(3,4)
    #print(G.adjacents(3))
    #print(G.adjacents(1))
