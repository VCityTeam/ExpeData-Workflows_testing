## Done

### Concerning the uniqueness of Container names
The name argument of a `Container()` definition must be unique across a full
workflow as illustrated by the 
Failing_Or_Issues/issue_duplicate_container_name.py workflow.
If we thus need to "burn in" some parameters within a set of different
containers all sharing the same image (think of the database argument for the 
`db_isready_container()` container creation function), then we must generate 
different container names (in order to avoid container name collisions).
Refer to 
[issue_duplicate_container_name.py](./Failing_Or_Issues/issue_duplicate_container_name.py) 
for an illustration of this issue and a possible workaround.

### Asserting database availability in Hera
Discuss [this learned lesson](./LESSONS_LEARNED.md#concerning-the-difficulty-of-asserting-database-availability)

### Try to unify (at Hera level) of the notation of static vs dynamic loops.
The challenge was to consider a static (a loop were the parameter range is known
at Hera submission stage) for loop (that is a loop expressed at python/Hera 
level) and try to make it a dynamic for loop (that is a loop where the parameter
range is only known at AW run-time). 
The Failing_Or_Issues/issue_fanout_fanin_for_in_python.py script only 
illustrates the difficulty to deal with the fanout/fanin technique. 
But it does so in a FAKE DYNAMIC for loop context. 
Refer to the LESSONS LEARNED section of that example for a conclusion.

### Factoriser la création des conteneurs des WorflowTemplates (check_db)
Facile, une fois que 
- la limite sur la collision des noms de conteneur est contournée: voir par
  exemple send_command_to_postgres_container()
- le workflowTemplate est correctement paramétré i.e. que ses paramètres ne
  sont plus brulés dans différents avatars d'un même conteneur (mais passés en
  inputs au niveau AW)
   

## Todo
* Factoriser la création des conteneurs des WorflowTemplates (check_db)
  Le travail est commencé (dans test_threedcitydb_start_db.py ). Le finir
  pour d'autres occurrences e.g. test_import_gml.py en faisant 
  "grep threedcitydb_containers *.py" )

* Documenter (LESSONS LEARNED):
  1. que l'on ne peut pas toujours faire des nested loops car la boucle sur
     le vintage ne peut inclure la créations de la base (partir de 
     test_threedcitydb_start_db.py et suive le LIMITS juste avant le loop sur
     vintage
  2. que lorsque l'on peut alors IL FAUT néanmoins définir un workflowTemplate
     pour la boucle interne, ce qui est pénible, cf par exemple test_collect.py.
     

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
  NOTE: 
  1. on peut étendre arg_parse pour gérer simultanément le fichier
     de config et les variables d'environment, cf
     https://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
  2. d'autres librairies type https://pypi.org/project/ConfigArgParse/ ????????
     (d'ailleurs pointée dans le stackoverflow précédent)
  
* Regarder si il reste des créations des conteneurs dont le nom est
  décliné par des vintages/boroughs.
