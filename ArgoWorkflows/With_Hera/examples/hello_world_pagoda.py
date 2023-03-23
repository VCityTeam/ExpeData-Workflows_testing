import hello_world
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pagoda

pagoda.define_cluster()
hello_world.define_workflow()




