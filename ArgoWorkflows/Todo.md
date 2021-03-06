# TODO list

- Evaluer [HERA workflows](https://github.com/argoproj-labs/hera-workflows)
- Aller voir le [langage BEPL](https://www.tutorialspoint.com/bpel)
- Aller voir Kaniko

- Pour le pb postgres
  - piste 1: ne pas faire pas de volumeMount (pas de PGDATA, ce qui limite les
    use case au niveau data-file) mais utiliser un pgdump dans un autre
    conteneur.
  - piste 2: l'usage d'une bd devant être sorti du contexte exprimable dans le
    workflow lancer postgres avec un helm chart

- Peut-on faire des bind mount autrement qu'avec Minikube cf
  la remarque d'Olivier sur s3 ci-dessous
  
- Regarder les options de minikube mount

- Peut-on faire reference a un step qui se trouve dans une loop ? (dans une
  structure iterative). Et peut-on faire reference relativement au contexte ?
  (i.e. le step d'avant dans cet boucle?)
  Tip: pythonsay a l'interieur de la boucle

- A mettre dans les Lesson learned d'Expedata:
  - il faut systématiquement promouvoir tous les fichiers de sortie en
    paramètre d'un traitement
  - de manière générale, c'est une bonne pratique que toutes les entrees et
    sorties doivent être paramétrables.
  - Écrire la logique de systématiquement décrire un fichier décrivant les
    sorties d'un traitement en json. Le penser comme une feature imposé d'un
    traitement ? i.e. généraliser l'approche de AW a d'autres modes d'écriture
    de workflow ?

- Mettre dans les Lessons Learned d'AW:
  - utiliser emptyDir (cf example-loop-faning-in-results-through-emptydir.yml)
    pour collecter les resultats de boucle.

- Use case: restart partiel on fail (re-execution partielle)
  - Peut-on changer l'entrypoint comme un argument de la ligne de commande
  - Peut-on lui dire de re-utiliser le même volume.

Olivier said:

- apprendre à monter un FS s3 remote avec le client local
  [goofys](https://github.com/kahing/goofys#installation)
- regarder comment AW peut faire usage d'un S3 bucket

## Done

- Regarder si on peut élégamment et conjointement définir les paramètres du
  workflow en laissant leur valeur dans le yml de de param. Cela aiderait le
  linter.
  Reponse: oui, on peut, cf e.g. just-import-to-3dcitydb-and-dump.yml

- Constatons que l'exemple AW de loop qui fait un withParam sur la sortie d'un
  job Python est effectif pour
  - README_REALLY_FIRST (that is before the following README_FIRS): en fait
    le travail ci-dessous est déjà fait (cf example-loading-json-with-python.yml).
    Il suffit de le completer avec un exemple illustrant que l'on peut profiter
    de l'occasion d'un read au niveau python pour faire un traitement.
    En fait
     1. on utilise la méthode fromValue (cf example-loading-json-fromValue.yml)
        quand on a pas de traitement à faire sur les sorties précédentes (mais
        juste les utiliser)
     2. on utilise la méthode loading-json-with-python quand on doit pré-traiter
        élégamment (i.e. par opposition avec Expr/sprig) les outputs précédents
        pour en faire des inputs du suivant (i.e. faire un dataflow mapping
        entre deux steps).
  - README_FIRST: en fait le bout de python DOIT faire l'extraction/traitement
     puisque cela merdoie avec expt/templatelib
  - fabriquer a la mano  un fichier /data/host/input.tx
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
