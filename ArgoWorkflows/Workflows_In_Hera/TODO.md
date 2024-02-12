## Done
* The name argument of a `Container()` definition must be unique across a full
  workflow as illustrated by the 
  Failing_Or_Issues/issue_duplicate_container_name.py workflow.
  If we thus need to "burn in" some parameters within a set of different
  containers all sharing the same image (think of the database argument
  for the `db_isready_container()` container creation function), we must
  then generate different container names.
  Refer to [issue_duplicate_container_name.py](./Failing_Or_Issues/issue_duplicate_container_name.py) for an illustration of this issue and
  a possible workaround.
* Discuss [this learned lesson](./LESSONS_LEARNED.md#concerning-the-difficulty-of-asserting-database-availability)

## Todo
* Tout refaire en dynamique i.e. sans devoir définir autant de 
  workflowTemplates qu'il y a de vintages mais définissant un unique 
  workflowTemplate acceptant (vintage,database.name) en argument.
  Potentiellement mettre du sucre syntactique pour les zones
  PARAMETER et INPUT.PARAMETER.VARIABLE

* Prendre un exemple de boucle for en statique (paramètres connus a la 
  soumission) pour en faire une boucle dynamique i.e exprimée en AW (with_item)
  Le but est d'unifier les boucles statiques et dynamiques.
  Attention: bien distinguer les deux contextes d'execution.
  Attention: le random doit etre dans une TACHE !!!!!!!!!!!!!!!

* Comment éviter que les scripts soient dupliqués pour chaque plateforme ?
  I.e. comment éviter qu'un script doive déclarer des lignes plateforme
  dépendantes du type
  ```python
  sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
  )
  from pagoda_environment_definition import environment
  ```
  TODO: faire le chemin sur minikube, puis rendre générique un équivalent de
  pagoda_definitions et la definition de l'environnement.
  Pour cela il faut que 
   - le script accepte un parser optionnel fournit par l'utilisateur en 
     argument. 
   - Si jamais un parser a été fourni en argument alors ne pas faire le 
     parse_args.
   - Retarder l'usage du parsing en laissant le soin à l'utilisateur de faire
     l'appel.
  Regarder si y'a mieux qu'arg_parse pour gérer simultanément le fichier
  de config et les variables d'environment.
  
* Factoriser la création des conteneurs des WorflowTemplates (check_db)

* Regarder comment factoriser la création des conteneurs dont le nom est
  décliné par des vintages.
