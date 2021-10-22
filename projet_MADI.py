import pyAgrum as gum
from itertools  import product,combinations

class PC():
    def __init__(self,file_bn_csv:str) -> None:
        self.learner=gum.BNLearner(file_bn_csv)
        self.namesToID=dict()
        self.IDtoName=dict()
        for name in self.learner.names():
            self.namesToID[name]=self.learner.idFromName(name)
            self.IDtoName[self.learner.idFromName(name)]=name
        self.G,self.sepSet,self.G_directed=self.initialisation()
        
        
        
    def initialisation(self):
        """ Initialise l'algorithme PC : 

        Returns
        -------
        UndiGraph Graph et Dict
            G : un graphe complet non orienté et
            sepSet : un dictionnaire d'ensemble séparant vides pour toutes paires de noeuds
        """        
        G=gum.UndiGraph()
        G_directed=gum.DAG()
        G.addNodes(len(self.namesToID))
        G_directed.addNodes(len(self.namesToID))
        sepSet=dict()
        for node1,node2 in list(product(G.nodes(),G.nodes())): #produit cartésien de G.nodes
            if(not G.existsEdge(node2,node1) and node1!=node2):
                G.addEdge(node1,node2)
                sepSet[(node1,node2)]=[]
                sepSet[(node2,node1)]=sepSet[(node1,node2)]
        return G,sepSet,G_directed
    
    def testIndepChi2(self, var1, var2, kno=[], nivRisque=0.05,verbose=False):
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
        nameVar1=self.learner.nameFromId(var1)
        nameVar2=self.learner.nameFromId(var2)
        names_kno=[self.learner.nameFromId(var) for var in kno]
        stat,pvalue=self.learner.chi2(nameVar1,self.learner.nameFromId(var2),names_kno)
        0
        if(verbose):
            if len(kno)==0:
                print("Le test Chi2 indique que '{}' indépendant de '{}' ==> {}".format(nameVar1,nameVar2,pvalue>=nivRisque))
            else:
                print("Le test Chi2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(nameVar1,nameVar2,names_kno,pvalue>=nivRisque))
            
        if pvalue>=nivRisque:
            return True
        return False
    
    def testIndepG2(self, var1, var2, kno=[], nivRisque=0.05,verbose=False):
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
        nameVar1=self.learner.nameFromId(var1)
        nameVar2=self.learner.nameFromId(var2)
        names_kno=[self.learner.nameFromId(var) for var in kno]
        stat,pvalue=self.learner.G2(nameVar1,nameVar2,names_kno)
        
        if(verbose):
            if len(kno)==0:
                print("Le test G2 indique que '{}' indépendant de '{}' ==> {}".format(nameVar1,nameVar2,pvalue>=nivRisque))
            else:
                print("Le test G2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(nameVar1,nameVar2,names_kno,pvalue>=nivRisque))
                
        if pvalue>=nivRisque:
            return True
        return False
    
    def phase1(self,nivRisque=0.05):
        """ Phase 1 de l'algorithme PC
        """        
        d=0
        ConditionOnAdjX=True
        while ConditionOnAdjX:
            for X,Y in self.G.edges():  # Ligne 5 :
                adjX=self.G.neighbours(X)# foreach arête X-Y tq |Adj(X)\{Y}|≥d
                if len(adjX)-1 >=d:     #
                    adjSansY=adjX.copy()                     # Ligne 6,7 et 12 :
                    adjSansY.remove(Y)                       # Choisir un Z in Adj(X)\{Y} tq |Z|=d
                    for Z in list(combinations(adjSansY,d)): # until tous les Z de taille d ont été testés
                        if(self.testIndepChi2(X, Y, kno=Z, nivRisque=nivRisque)): # Si X indep Y | Z #On peut utiliser Chi2 ou G2 PB TODO
                            self.G.eraseEdge(X,Y)
                            self.sepSet[(X,Y)].append(Z)
                            break
            d+=1
            compteur=0
            for X in self.G.nodes():            # Ligne 14
                if len(self.G.neighbours(X))<=d: #
                    compteur+=1                 # compter pour combien de X |Adj(X)|≤d
                else:
                    break # Si un noeud a plus de d noeuds neighbours, on n'a pas besoin de regarder les autres
            if(len(self.G.nodes())==compteur):  # Si tous les noeuds vérifie on arrête
                ConditionOnAdjX=False           #

    def phase2(self):
        """ Phase 2 de l'algorithme PC
        """ 
        # Orientation des v-structures
        for (X,Y,Z) in self.findUnshieldedTriple():
            if Z not in self.sepSet[(X,Y)]:
                self.G.eraseEdge(X,Z)
                self.G.eraseEdge(Z,Y)
                self.G_directed.addArc(X, Z)
                self.G_directed.addArc(Z, Y)
                
        # Propagations
        ConditionArreteOrient = True
        while ConditionArreteOrient :
            i=0
            for (X,Y) in list(product(self.G.nodes(),self.G.nodes())):
                    hasAddedOne=False
                    if Y == X:
                        continue
                    if not self.G.existsEdge(X, Y):
                        for Z in self.G_directed.nodes():
                            if self.G_directed.existsArc(X,Z) and self.G.existsEdge(Z, Y):
                                i+=1
                                hasAddedOne=True
                                self.G.eraseEdge(Z,Y)
                                self.G_directed.addArc(Z, Y)
                    if self.G.existsEdge(X, Y) and self.G_directed.hasDirectedPath(X,Y):  
                        self.G.eraseEdge(X,Y)
                        self.G_directed.addArc(X, Y)
                        if(not hasAddedOne):
                            i+=1
            if(i==0):
                ConditionArreteOrient=False
        
        #TODO PB sur ConditionArreteOrient
        

    def findUnshieldedTriple(self)->list:
        """ Permet de trouver les unshielded triple
        Renvoie la liste des id des triplets concernés
        """   
        triples=[]
        for Z in self.G.nodes():
            for X in self.G.nodes():
                if Z == X or not self.G.existsEdge(X,Z): #X-Z : X est connecté à Z
                    continue
                for Y in self.G.nodes():
                    if Y == X or Y == Z or (not self.G.existsEdge(Y,Z)) or self.G.existsEdge(X,Y): #X-Z-Y : X est connecté à Z et Z connecté à Y
                        continue
                    triples.append((X,Z,Y))
        l=[]
        for i in range(len(triples)):
            triple1=triples[i]
            for j in range(i+1,len(triples)):
                triple2=triples[j]
                #print(triple1,triple2,triple1[0] in triple2 and triple1[1] in triple2 and triple1[2] in triple2)
                if(triple1[0] in triple2 and triple1[1] in triple2 and triple1[2] in triple2):
                    l.append(triple2)
        for triple in l:
            if triple in triples:
                triples.remove(triple)
        return triples

    def getG(self):
        return self.G
    def getSepSet(self):
        return self.sepSet
    def getG_directed(self):
        return self.G_directed



            

                    


if __name__== "__main__":
    pass
    #G.addNodes(5)
    #G.addEdge(0,1)
    #G.addEdge(1,2)
    #G.addArc(3,4)
    #print(G.neighbours(3))
    #print(G.neighbours(1))
