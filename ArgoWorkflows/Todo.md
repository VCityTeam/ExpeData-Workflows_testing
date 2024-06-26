# TODO list

New entries are now within the
[ExpeData repository issues](https://github.com/VCityTeam/ExpeData-Workflows_testing/issues/9)

## Todo at HERA LEVEL (to be ported in issues)

- Factoriser la création des conteneurs des WorflowTemplates (check_db)
  Le travail est commencé (dans test_threedcitydb_start_db.py ). Le finir
  pour d'autres occurrences e.g. test_import_gml.py en faisant
  "grep threedcitydb_containers \*.py" )

- Tester les scripts sur minikube, afin de s'assurer que les scripts sont bien
  cluster independants (mais ne depends que args et/ou hera.config) au travers
  de environment

- Regarder si il reste des créations des conteneurs dont le nom est
  décliné par des vintages/boroughs.

## Done at AW level

- Regarder si on peut élégamment et conjointement définir les paramètres du
  workflow en laissant leur valeur dans le yml de param. Cela aiderait pour
  linter.
  Réponse: oui, on peut, cf e.g. just-import-to-3dcitydb-and-dump.yml

- Constatons que l'exemple AW de loop qui fait un withParam sur la sortie d'un
  job Python est effectif pour

  - README_REALLY_FIRST (that is before the following README_FIRST): en fait
    le travail ci-dessous est déjà fait (cf example-loading-json-with-python.yml).
    Il suffit de le completer avec un exemple illustrant que l'on peut profiter
    de l'occasion d'un read au niveau python pour faire un traitement.
    En fait
    1.  on utilise la méthode fromValue (cf example-loading-json-fromValue.yml)
        quand on a pas de traitement à faire sur les sorties précédentes (mais
        juste les utiliser)
    2.  on utilise la méthode loading-json-with-python quand on doit pré-traiter
        élégamment (i.e. par opposition avec Expr/sprig) les outputs précédents
        pour en faire des inputs du suivant (i.e. faire un dataflow mapping
        entre deux steps).
  - README_FIRST: en fait le bout de python DOIT faire l'extraction/traitement
    puisque cela merdoie avec expt/templatelib
  - fabriquer a la mano un fichier /data/host/input.tx
  - faire un step python qui lit ce fichier /data/host/input.txt, puis
    envoie sur std-ouput un json (comme le fait l'exemple de loop)
  - prendre cela comme entree de withParam de la tache suivante
  - Note: la logique est ici d'avoir un bout de python qui fait le mapping
    entre deux tâches et qui produit le json pour le withParam suivant

- Pour une boucle on doit différencier les noms des fichiers intermédiaires
  ou on fera le valueFrom LORSQUE "le" fichier de sortie est sur la partition
  partagée. Afin d'éviter cette différenciation, peut-on utiliser des
  répertoires différents dans chacun des conteneurs (avec e.g. la directive
  emptyDir ?)

- Regarder si on peut faire des boucles en sequences

- Deuxième piste: éviter d'avoir a utiliser sprig.last()
  - Pour les boucles faire que chaque run produise un fichiers d'output
    différents (par exemple indexé avec un identifiant automatique)
  - aller striper les attributs qu'il faut dans le résultat de la boucle.
