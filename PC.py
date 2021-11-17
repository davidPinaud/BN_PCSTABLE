import pyAgrum as gum
from itertools  import product,combinations

class PC():
    def __init__(self,csvFilePath:str) -> None:        
        self.learner=gum.BNLearner(csvFilePath)
        self.G,self.sepSet=self.initialisation()
        self.verbose=""
        self.GPhase21=None

####### PHASE 1 ####### 

    def phase1(self,nivRisque=0.05):
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
                        if(self.testIndepG2(X, Y, kno=Z, nivRisque=nivRisque)): # Si X indep Y | Z #On peut utiliser Chi2 ou G2 PB TODO
                            self.G.eraseEdge(X,Y)
                            for z in Z:
                                self.sepSet[(X,Y)].add(z)
                                self.sepSet[(Y,X)].add(z)
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
    def phase1_PC_CSS(self,nivRisque=0.05,G1=gum.MixedGraph(),G2=gum.MixedGraph()):
        """ NewStep1(G1|G2) de PC-CSS
        Les self.G sont remplacé par G1
        aSansY est remplacé par set(aSansY).intersection(self.findConsistentSet(X,Y,G2))  
        """
        d=0
        ConditionOnAdjX=True
        while ConditionOnAdjX:
            a=dict()
            for X in G1.nodes():
                a[X]=G1.adjacents(X)
            for X,Y in G1.edges():
                if len(a[X])-1 >=d:     
                    aSansY=a[X].copy()                     
                    aSansY.remove(Y)
                    aSansYEtConsist=set(aSansY).intersection(self.findConsistentSet(X,Y,G2))                
                    for Z in list(combinations(aSansYEtConsist,d)): 
                        if(self.testIndepG2(X, Y, kno=Z, nivRisque=nivRisque)): 
                            G1.eraseEdge(X,Y)
                            for z in Z:
                                self.sepSet[(X,Y)].add(z)
                                self.sepSet[(Y,X)].add(z)
                            break
            d+=1
            compteur=0
            for X in G1.nodes():            # Ligne 14
                if len(G1.adjacents(X))<=d: #
                    compteur+=1                 # compter pour combien de X |Adj(X)|≤d
                else:
                    break # Si un noeud a plus de d noeuds adjacents, on n'a pas besoin de regarder les autres
            if(len(G1.nodes())==compteur):  # Si tous les noeuds vérifie on arrête
                ConditionOnAdjX=False
    def phase1_STABLE(self,nivRisque=0.05):
        """ Phase 1 de l'algorithme PC-Stable 
        """
        ##print("Avant Phase 1")
        # #gnb.sideBySide(self.G)
        d=0
        ConditionOnAdjX=True
        while ConditionOnAdjX:
            a=dict()
            for X in self.G.nodes():
                a[X]=self.G.adjacents(X)
            for X,Y in self.G.edges():
                if len(a[X])-1 >=d:     
                    aSansY=a[X].copy()                     
                    aSansY.remove(Y)                       
                    for Z in list(combinations(aSansY,d)): 
                        if(self.testIndepG2(X, Y, kno=Z, nivRisque=nivRisque)): 
                            self.G.eraseEdge(X,Y)
                            for z in Z:
                                self.sepSet[(X,Y)].add(z)
                                self.sepSet[(Y,X)].add(z)
                            break
            d+=1
            compteur=0
            for X in self.G.nodes():            # Ligne 14
                if len(self.G.adjacents(X))<=d: #
                    compteur+=1                 # compter pour combien de X |Adj(X)|≤d
                else:
                    break # Si un noeud a plus de d noeuds adjacents, on n'a pas besoin de regarder les autres
            if(len(self.G.nodes())==compteur):  # Si tous les noeuds vérifie on arrête
                ConditionOnAdjX=False 

####### PHASE 2 ####### 

    def phase2(self):
        """ Phase 2 de l'algorithme PC, elle permet d'orienter des arêtes pour ne pas avoir plus de V-Struct et de cycles
        Après cette phase, G est un graphe essentiel 
        """ 
        L=self.findUnshieldedTriple()
        hasGoneIn=True
        #Phase 2.1 : Orientation des V-Struct
        while(hasGoneIn):#Step 2
            hasGoneIn=False
            for (X,Z,Y) in L:
                if Z not in self.sepSet[(X,Y)]:
                    self.G.eraseEdge(X,Z)
                    self.G.eraseEdge(Y,Z)
                    self.G.addArc(X,Z)
                    self.G.addArc(Y,Z)
                    L=self.findUnshieldedTriple() #on doit recalculer les UnshieldedTriple dynamiquement dès qu'on change le graphe G... 
                                                #sinon il se peut qu'un des triple ait des éléments en commun avec le triple 
                                                #pour lequel on a introduit une V-Structure et cela peut mener à la création d'un cycle
                    hasGoneIn=True #Pour ne pas avoir une boucle infinie quand on ne peut pas orienter des arcs
                    break

        # Phase 2.2 : Propagations, les orientation que la phase 2.1 implique
        
        self.GPhase21=gum.MixedGraph(self.G)#Pour la verbose
        self.verbose+="\n"+"Phase 2"        #Pour la verbose
        nb_iteration=1                      #Pour la verbose
        
        plusDarreteOrientable = False #Condition d'arrêt
        
        

        while not plusDarreteOrientable : #Step3
            #Verbose
            self.verbose+="\n"+f"Itération n°{nb_iteration}"
            nb_iteration+=1
            #Condition d'arrêt
            plusDarreteOrientable=True

            tripletsTemp=list(product(self.G.nodes(),self.G.nodes(),self.G.nodes()))
            toDelete=[]
            for (i,j,k) in tripletsTemp: #Enlever les triplets avec les mêmes composantes
                if(i==j or i==k or j==k):
                    toDelete.append((i,j,k))
            for triple in toDelete:
                tripletsTemp.remove(triple)
                # if triple in tripletsTemp:
                #     tripletsTemp.remove(triple)

             #Liste de tous les quadruplets
            quadrupletsTemp=list(product(self.G.nodes(),self.G.nodes(),self.G.nodes(),self.G.nodes()))
            toDelete=[]
            for (i,j,k,l) in quadrupletsTemp:#Enlever les quadruplets avec les mêmes composantes
                if(i==j or i==k or i==l or j==k or j==l or k==l):
                    toDelete.append((i,j,k,l))
            for quadruple in toDelete:
                quadrupletsTemp.remove(quadruple)
                # if quadruple in quadrupletsTemp:
                #     quadrupletsTemp.remove(quadruple)
            
            
            #R2 (R3 dans pseudo code prof)
            # Ici c'est R3 dans le pseudo code du cours, le R2 du papier n'empechait que les
            # cycles de taille 3
            for (X,Y) in list(product(self.G.nodes(),self.G.nodes())):
                self.verbose+="\n"+f"in R2 : (X,Y)={(X,Y)}"
                if self.G.existsEdge(X,Y) and self.G.hasDirectedPath(X,Y):
                    self.verbose+="\n"+f"in R2 : (X,Y)={(X,Y)}, on oriente {X}->{Y}"
                    self.G.eraseEdge(X,Y)
                    self.G.addArc(X, Y)

            #R3 : une règle pas dans le pseudo code du cours qui évite les "nouvelles" v-struct OU un cycle
            for (i,j,k,l) in quadrupletsTemp:
                if(self.G.existsEdge(i,j) and self.G.existsEdge(i,k) and self.G.existsArc(k,j) and self.G.existsArc(l,j) and self.G.existsEdge(i,l) and not self.G.existsEdge(k,l)):
                    self.G.eraseEdge(i,j)
                    self.G.addArc(i,j)
                    plusDarreteOrientable=False
                    break
            #R1 (R2 dans pseudo code prof) pour éviter la création de v-struct
            for (i,j,k) in tripletsTemp:
                self.verbose+="\n"+f"in R1 : (i,j,k)={(i,j,k)}"
                if(self.G.existsArc(i,j) and self.G.existsEdge(j,k) and not self.G.existsEdge(i,k)):
                    self.verbose+="\n"+f"in R1 : (i,j,k)={(i,j,k)}, on oriente {j}->{k}"
                    self.G.eraseEdge(j,k)
                    self.G.addArc(j, k)
                    plusDarreteOrientable=False
                    break
                
            # Nous avons choisis de mettre R2 et R3 avant R1 pour limiter la création de cycle
            # Pendant l'exécution de l'algorithme. La règle R3, si appliquée, en particulier construit 
            # de "nouvelles" v-struct qui interdise l'ajout d'un nouveau cycle.
            # 
            # Dans les situations où nous allons appliquer R3, il est en effet préférable d'introduire 
            # ces v-struct plutôt que de possiblement d'introduire des cycles en faisant R1 avant.

####### FONCTIONS UTILITAIRES #######

    def initialisation(self):
        """ Initialise l'algorithme PC : 
        crée un graphe non orienté complet et initialise les sepset vides
        Returns
        -------
        UndiGraph Graph et Dict
            G : un graphe complet non orienté et
            sepSet : un dictionnaire d'ensemble séparant vides pour toutes paires de noeuds
        """        
        G=gum.MixedGraph()
        G.addNodes(len(self.learner.names()))
        sepSet=dict()

        for node1,node2 in list(product(G.nodes(),G.nodes())): #produit cartésien de G.nodes
            if(not G.existsEdge(node2,node1) and node1!=node2):
                G.addEdge(node1,node2)
                sepSet[(node1,node2)]=set()
                sepSet[(node2,node1)]=sepSet[(node1,node2)]

        return G,sepSet#,G_directed

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
                    if Y == X or Y == Z or (not self.G.existsEdge(Y,Z)) or self.G.existsEdge(X,Y) or self.G.existsArc(X, Y) or self.G.existsArc(Y,X): #X-Z-Y : X est connecté à Z et Z connecté à Y
                        continue
                    triples.append((X,Z,Y))
        l=[]#Enlever les doublons
        for i in range(len(triples)):
            triple1=triples[i]
            for j in range(i+1,len(triples)):
                triple2=triples[j]
                ##print(triple1,triple2,triple1[0] in triple2 and triple1[1] in triple2 and triple1[2] in triple2)
                if(triple1[0] in triple2 and triple1[1] in triple2 and triple1[2] in triple2):
                    l.append(triple2)
        for triple in l:
            if triple in triples:
                triples.remove(triple)
        return triples


    def findConsistentSet(self,X,Y,G2):
        """Fonction qui trouve le consistent set de deux noeuds X,Y dans un graphe G2

        Parameters
        ----------
        X : int
            id d'un noeud dans G
        Y : int
            id d'un noeud dans G
        G2 : pyAgrum.MixedGraph
            Graphe dans lequel calculer le consistent set

        Returns
        -------
        set
            l'ensemble consistent de x et y dans G2
        """        
        consistentSet=set()
        for Z in G2.adjacents(X):
            if Z!=Y and not G2.existsArc(X,Z):
                if len(G2.mixedUnorientedPath(X,Z))!=0 and len(G2.mixedUnorientedPath(Z,Y))!=0:
                    consistentSet.add(Z)
        return consistentSet
    
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
        nameVar1=f"n_{var1}"#=nom du noeud d'ID var 1 dans le BN, pour donner des visualisations cohérentes car id dans learner ≠ id dans bn
        nameVar2=f"n_{var2}"
        names_kno=[f"n_{var}" for var in kno]
        stat,pvalue=self.learner.chi2(nameVar1,nameVar2,names_kno)

        if(verbose):
            if len(kno)==0:
              print("Le test Chi2 indique que '{}' indépendant de '{}' ==> {}".format(nameVar1,nameVar2,pvalue>=nivRisque))
              pass
            else:
              print("Le test Chi2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(nameVar1,nameVar2,names_kno,pvalue>=nivRisque))
              pass
            
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
        nameVar1=f"n_{var1}"
        nameVar2=f"n_{var2}"
        names_kno=[f"n_{var}" for var in kno]
        stat,pvalue=self.learner.G2(nameVar1,nameVar2,names_kno)
        
        if(verbose):
            if len(kno)==0:
              print("Le test G2 indique que '{}' indépendant de '{}' ==> {}".format(nameVar1,nameVar2,pvalue>=nivRisque))
              pass
            else:
              print("Le test G2 indique que '{}' indépendant de '{}' étant donné {} ==> {}".format(nameVar1,nameVar2,names_kno,pvalue>=nivRisque))
              pass
                
        if pvalue>=nivRisque:
            return True
        return False
            

