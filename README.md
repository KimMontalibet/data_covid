# Génération de rapports d'incohérence sur les données Covid 19 sur [Data.Gouv.fr](https://www.data.gouv.fr/fr/)



## Introduction

Ce script Python permet de générer un résumé des incohérences présentes dans les données de suivi de l'épidémie Covid-19 en France, mises à disposition sur le site data.gouv.fr. Les fichiers concernés sont les suivants: 

### Données hospitalières relatives à l'épidémie de COVID-19 (disponibles [ici](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/))
- **donnees-hospitalieres-covid19-2020-xx-xx-xxhxx.csv** : données hospitalières quotidiennes relatives à l'épidémie du COVID-19 par département et sexe du patient : nombre de patients hospitalisés, nombre de personnes actuellement en réanimation ou soins intensifs, nombre cumulé de personnes retournées à domicile, nombre cumulé de personnes décédées
- **donnees-hospitalieres-etablissements-covid19-2020-xx-xx-xxhxx.csv** : données quotidiennes relatives aux établissements hospitaliers par département (nombre cumulé de services ayant déclaré au moins un cas)


### Données des urgences hospitalières et de SOS médecins relatives à l'épidémie de COVID-19 (disponibles [ici](https://www.data.gouv.fr/fr/datasets/donnees-des-urgences-hospitalieres-et-de-sos-medecins-relatives-a-lepidemie-de-covid-19/))
- **sursaud-covid19-quotidien-2020-xx-xx-19h00-departement.csv** : données hospitalières quotidiennes relatives à l'épidémie du COVID-19 par département et sexe du patient : nombre de patients hospitalisés, nombre de personnes actuellement en réanimation ou soins intensifs, nombre cumulé de personnes retournées à domicile, nombre cumulé de personnes décédées
- **sursaud-covid19-hebdomadaire-2020-xx-xx-xxhxx.csv**:  données hebdomadaires de SOS médecins et des urgences hospitalières par département et par tranches d’âge des patients (nombre de passages aux urgences pour suspicion de COVID-19, nombre total de passages aux urgences, nombre d’hospitalisations parmi les passages aux urgences pour suspicion de COVID-19, nombres total d’actes médicaux SOS Médecins pour suspicion de COVID-19, nombres d’actes médicaux SOS Médecins)

Pour chacun de ces fichiers, le script génère un rapport avec les incohérences liées aux totaux par genre et par tranche d'âges. 

## Faire tourner le script  

### 1 - Pré-requis

Python 3 


### 2 - Récupération du dépôt 

```
$ git clone https://github.com/KimMontalibet/data_covid
$ cd data_covid
```

### 3 - Lancer le script 

Les fichiers d'inputs sont lus directement via les url du site data.gouv.fr. 
```
python3 ./src/main.py 
```
 

## Les rapports d'incohérences générés 

Les fichiers contiennent des variables de comptage (nombre de patients hospitalisés pour cause de covid19, nombre de décès liés au covid19) qui sont données par total et par décomposition en fonction du genre et des classes d'âges. Les tests de cohérences effectués permettent de vérifier que la somme des comptages par genre et/ou classe d'âges est égal au total. Si pour une ligne donnée, la somme diffère, alors on calcule l'écart (total - somme sur le genre et/ou classe d'âge). 

Plus précisément pour chaque fichier, le rapport d'incohérence contient deux onglets: 

### Un onglet avec des métriques synthétiques (appelé *synthèse*) 
Pour le fichier, on donne: 
- le nombre total de lignes
- le nombre total de lignes avec au moins une incohérence

Pour chaque variable, on donne: 
- le nombre de lignes avec une incohérence
- le moyenne, le minimum et le maximum de la différence entre le total et la somme

### Un onglet avec les lignes comportant des incohérences (appelé *erreurs*)

Cet onglet comporte toutes les lignes avec au moins une incohérence. On a rajouté les colonnes suivantes: 
- *numero_ligne*: donne le numéro de la ligne dans le fichier initial (numérotées de 1 à n) 
- *columnn_test*: pour la colonne de nom *column* vaut 0 si la ligne ne comporte pas d'erreur et 1 si elle comporte une erreur 
- *column_diff*: pour la colonne de nom *column*, la différence entre le total et la somme 
- *sum_test*: la somme de toutes les colonnes de type *column_test* et qui correspond donc au nombre de colonnes avec une erreur de cohérence pour la ligne considérée


## Détail des rapports par fichier 

### Fichier sursaud_corona_quot : 
- Le nombre d’erreurs de sommes hommes + femmes, avec une déclinaison par indicateur (feuille 1)
- La liste des lignes erronées détectées pour les sommes par genre (feuille 2)
- Le nombre d’erreurs de sommes des tranches d’âges, avec déclinaison par indicateur (feuille 3)
- La liste des lignes erronées détectées pour les sommes par tranches d'âges (feuille 4)

### Fichier sursaud_corona_hebdo : 
- Le nombre d’erreurs de sommes des tranches d’âges, avec déclinaison par indicateur (feuille 1)
- La liste des lignes erronées détectées par tranche d'âges (feuille 2)

### Fichier covid_hospi_29 :
- Le nombre d’erreurs de sommes hommes + femmes, avec une déclinaison par indicateur (feuille 1)
- La liste des lignes erronées détectées par genre (feuille 2)

### Fichier donnees-hospitalieres-etablissements: 
- Le nombre de lignes avec une incohérence sur les sommes cumulées (somme *jour n+1* inférieure à la somme du *jour n* (feuille 1) 
- La liste des lignes erronnées détectées pour les sommes cumulées (feuille 2)







