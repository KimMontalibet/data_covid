# Génération de rapports d'incohérence sur les données Covid 19 sur Data.Gouv.fr



## Introduction

Ce script Python permet de générer un résumé des incohérences présentes dans les données de suivi de l'épidémie Covid-19 en France, mises à disposition sur le site data.gouv.fr. Les fichiers concernés sont les suivants: 

### Données hospitalières relatives à l'épidémie de COVID-19 (disponibles [ici](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/))
- **donnees-hospitalieres-covid19-2020-xx-xx-xxhxx.csv** : données hospitalières quotidiennes relatives à l'épidémie du COVID-19 par département et sexe du patient : nombre de patients hospitalisés, nombre de personnes actuellement en réanimation ou soins intensifs, nombre cumulé de personnes retournées à domicile, nombre cumulé de personnes décédées
- **donnees-hospitalieres-etablissements-covid19-2020-xx-xx-xxhxx.csv** : données quotidiennes relatives aux établissements hospitaliers par département (nombre cumulé de services ayant déclaré au moins un cas)


### Données des urgences hospitalières et de SOS médecins relatives à l'épidémie de COVID-19 (disponibles [ici](https://www.data.gouv.fr/fr/datasets/donnees-des-urgences-hospitalieres-et-de-sos-medecins-relatives-a-lepidemie-de-covid-19/))
- **sursaud-covid19-quotidien-2020-xx-xx-xxhxx.csv** : données hospitalières quotidiennes relatives à l'épidémie du COVID-19 par département et sexe du patient : nombre de patients hospitalisés, nombre de personnes actuellement en réanimation ou soins intensifs, nombre cumulé de personnes retournées à domicile, nombre cumulé de personnes décédées
- **sursaud-covid19-hebdomadaire-2020-xx-xx-xxhxx.csv**:  données hebdomadaires de SOS médecins et des urgences hospitalières par département et par tranches d’âge des patients (nombre de passages aux urgences pour suspicion de COVID-19, nombre total de passages aux urgences, nombre d’hospitalisations parmi les passages aux urgences pour suspicion de COVID-19, nombres total d’actes médicaux SOS Médecins pour suspicion de COVID-19, nombres d’actes médicaux SOS Médecins)

Pour chacun de ces fichiers, le script génère un rapport avec les incohérences liées aux totaux par genre et par tranche d'âges. 

## Faire tourner le script  

1 - Pré-requis

Python 3 


2 - Récupération du dépôt 

$ git clone https://github.com/KimMontalibet/data_covid
$ cd data_covid

3 - Lancer le script 

Il faut spécifier le **dossier_input** contenant les fichiers *.csv* mentionnés en introduction, l'**dossier_output** dans lequel enregistrer les rapports d'incohérences (au format *.xlsx*), la **date** des fichiers au format.

```
python3 ./src/main.py dossier_input dossier_output date
```
 

## Les rapports d'incohérences générés 

Les fichiers contiennent des variables de comptage (nombre de patients hospitalisés pour cause de covid19, nombre de décès liés au covid19) qui sont données par total et par décomposition en fonction du genre et des classes d'âges. Les tests de cohérences effectués permettent de vérifier que la somme des comptages par genre et/ou classe d'âges est égal au total. Si pour une ligne donnée, la somme diffère, alors on calcule l'écart (total - somme sur le genre et/ou classe d'âge). 

Plus précisément pour chaque fichier, le rapport d'incohérence contient deux 

