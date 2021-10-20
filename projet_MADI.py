import pyAgrum as gum
from itertools  import product,combinations

class PC():
    def __init__(self,n : int) -> None:
        self.G,self.sepSet=self.initialisation(n)
        #self.learner=gum.BNLearner("out/sample_score.csv")
        
    def initialisation(self,n:int):
        """ Initialise l'algorithme PC : 
        Parameters
        ----------
        n : int
            nombre de noeuds dans le BN

        Returns
        -------
        Mixed Graph et Dict
            G : un graphe complet non orienté et
            sepSet : un dictionnaire d'ensemble séparant vides pour toutes paires de noeuds
        """        
        G=gum.MixedGraph()
        G.addNode(n)
        sepSet=dict()
        for node1,node2 in list(product(self.G.nodes(),self.G.nodes())): #produit cartésien de G.nodes
            G.addEdge(node1,node2)
            sepSet[(node1,node2)]=[]
        return G,sepSet
    
    def testIndepChi2(self, var1, var2, kno=[], nivRisque):
        """ Effectue un test chi2 d'indépendance entre var1 et var2 conditionnellement à l'ensemble kno
        Parameters
        ----------
        var1 : int
            L'id de la première variable avec laquelle tester l'indépendance
        var2 : int
            L'id de la deuxième variable avec laquelle tester l'indépendance
        kno=[] : list[int] 
            La liste des ids des variables qui conditionnent l'indépendance à tester
        nivRisque : float
            Le niveau de risque (souvent 5%)

        Returns
        -------
        bool
            Vrai si il y a indépendance et faux sinon
        """
        stat,pvalue=self.learner.chi2(var1,var2,kno)
        
        if len(kno)==0:
            print("Le test Chi2 indique que '{}' indépendant de '{}' ==> {}".format(var1,var2,pvalue>=nivRisque))
        else:
            print("Le test Chi2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(var1,var2,kno,pvalue>=nivRisque))
            
        if pvalue>=nivRisque:
            return True
        return False
    
    def testIndepG2(self, var1, var2, kno=[], nivRisque):
        """ Effectue un test G2 d'indépendance entre var1 et var2 conditionnellement à l'ensemble kno
        Parameters
        ----------
        var1 : int
            L'id de la première variable avec laquelle tester l'indépendance
        var2 : int
            L'id de la deuxième variable avec laquelle tester l'indépendance
        kno=[] : list[int] 
            La liste des ids des variables qui conditionnent l'indépendance à tester
        nivRisque : float
            Le niveau de risque (souvent 5%)

        Returns
        -------
        bool
            Vrai si il y a indépendance et faux sinon
        """
        stat,pvalue=self.learner.G2(var1,var2,kno)
        
        if len(kno)==0:
            print("Le test G2 indique que '{}' indépendant de '{}' ==> {}".format(var1,var2,pvalue>=nivRisque))
        else:
            print("Le test G2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(var1,var2,kno,pvalue>=nivRisque))
            
        if pvalue>=nivRisque:
            return True
        return False
    
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
                        if(testIndepChi2(self.learner, X, Y, kno=Z, 0.05)): # Si X indep Y | Z #On peut utiliser Chi2 ou G2 PB TODO
                            self.G.eraseEdge(X,Y)
                            self.sepSet[(X,Y)].append(Z)
                            break
            d+=1
            compteur=0
            for X in self.G.nodes():            # Ligne 14
                if len(self.G.adjacents(X))<=d: #
                    compteur+=1                 # compter pour combien de X |Adj(X)|≤d
                else:
                    break # Si un noeud a plus de d noeuds adjacents, on n'a pas besoin de regarder les autres
            if(len(self.G.nodes())==compteur):  # Si tous les noeuds vérifie on arrête
                ConditionOnAdjX=False           #

    def phase2(self):
        """ Phase 2 de l'algorithme PC
        """ 
        # Orientation des v-structures
        Gpdag = self.G #.copy() ? PB TODO
        for (X,Y,Z) in findUnshieldedTriple(self):
            if Z not in self.sepSet[(X,Y)]:
                Gpdag.eraseEdge(X,Z)
                Gpdag.eraseEdge(Z,Y)
                Gpdag.addArc(X, Z)
                Gpdag.addArc(Z, Y)
                
        # Propagations
        ConditionArreteOrient = True
        while ConditionArreteOrient :
            for X in Gpdag.nodes():
                for Y in Gpad.nodes():
                    if Y == X:
                        break
                    if not Gpdag.existsEdge(X, Y):
                        for Z in Gpdag.edges():
                            if Gpdag.existesArc(X,Z) and Gpdag.existsEdge(Z, Y):
                                Gpdag.eraseEdge(Z,Y)
                                Gpdag.addArc(Z, Y)
                    if Gpdag.existsEdge(X, Y) and Gpad.hasDirectedPath(X,Y):  
                        Gpdag.eraseEdge(X,Y)
                        Gpdag.addArc(X, Y)
        
        #TODO PB sur ConditionArreteOrient
        

    def findUnshieldedTriple(self)->list:
        """ Permet de trouver les unshielded triple
        Renvoie la liste des id des triplets concernés
        """   
        triple=[]
        for Z in self.G.nodes():
            for X in self.G.nodes():
                if Z == X or not self.G.existsEdge(X,Z):
                    break
                for Y in self.G.nodes():
                    if Y == X or Y == Z or not self.G.existsEdge(Y,Z) or self.G.existsEdge(X,Y):
                        break
                    triple.append((X,Z,Y))
        return triple
            

                    


if __name__== "__main__":
    G=gum.MixedGraph()
    #G.addNodes(5)
    #G.addEdge(0,1)
    #G.addEdge(1,2)
    #G.addArc(3,4)
    #print(G.adjacents(3))
    #print(G.adjacents(1))
