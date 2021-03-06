# Projet MADI - Implémentation de PC et PC-Stable
Projet réalisé dans le cadre de l'UE Modèles et algorithmes pour la décision dans l'incertain (MADI).

Sujet du projet : Graphe essentiel dans les réseaux bayésiens, comparaison d'algorithmes d'apprentissages basés sur des contraintes

But : Implémenter différentes variantes de l'algorithme PC, permettant d'obtenir le graphe essentiel d'un BN, en python (avec PyAgrum), les tester sur différentes instances puis comparer les performances des approches.
Ce projet se décline comme un rapport de recherche sur des algorithmes de l'état de l'art. L'objectif est de se donner les moyens de décider l'algorithme efficace à utiliser. 

Ce repository est constitué de plusieurs fichiers : Le dossier res recense les résultats obtenus, MADI_AideProjet.pdf est un document d'aide pour ce projet (notamment concernant la syntaxe), PC.py et presentation_resultats_et_demonstrations.ipynb sont les codes sources et presentation_resultats_et_demonstrations.ipynb fait également office de rapport, test.csv est une instance de test.

### Algorithmes à comparer :
PC (voir Spirtes, P.; and Glymour, C. 1991. 
An algorithm for fast recovery of sparse causal graphs. 
Social Science Computer Review 9: 62–72.)

PC stable (voir Colombo, D.; Maathuis, M. H.; Kalisch, M.; and Richardson, T. S. 2012. 
Learning high-dimensional directed acyclic graphs with latent and selection variables. 
Ann. Statist. 40(1): 294–321. doi:10.1214/11-aos940. URL http://dx.doi. org/10.1214/11-AOS940.)

PC-CSS (voir Li, H.; Cabeli, V.; Sella, N.; and Isambert, H. 2019.
Constraint-based Causal Structure Learning with Consistent Separating Sets.
In Advances in Neural Information Processing Systems 32. Curran Associates, Inc. 
http://papers.nips.cc/paper/9573-constraint-based-causal-structure-learning-with-consistent-separating-sets.pdf.)

### Quelques critères de comparaison :
En fonction de la taille de la base et/ou du nombre de variables dans le BN

Qualité de l'apprentissage : Structural Hamming, F-score, dist2opt, etc.

Rapidité de l'apprentissage 

etc.
