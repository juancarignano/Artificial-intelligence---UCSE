from simpleai.search import (SearchProblem,astar)
from simpleai.search.viewers import BaseViewer

    # Tenemos que saber: 
    # donde esta el robot 
    # - cual es el camino que ya recorrio (conocer cuales casilleros ya fueron recorridos)
    # - que tipo de robot es (mapeador - soporte)

    # - escaneador -> puede moverse un máximo de 10 movimientos (1000 mAh / 100 mah por movimiento)
    # - soporte -> mismo consumo de movientos (costo), que el mapeador
    # soporte carga en 5 min al mapeador (por ende, debemos tener guardada la posicion que logro recorrer el mapeador)
    # llevar constancia del nivel de bateria del mapeador (ya que no necesariamente debe ser cargado al agotar su bateria)
    # la bateria del mapeador se carga en su totalidad

def search_robot(robots,id):
    return list(filter(lambda robot: robot[1][0] == id, enumerate(robots)))

# Convertidor de tuplas a listas  
def to_list(tuplas):
    return [list(x) for x in tuplas]

# Convertidor de listas a tuplas
def to_tuple(listas):
    return tuple([tuple(x) for x in listas])

def planear_escaneo(tuneles, robots):
    #nuestro estado inicial sera una tupla donde la primer parte de la tupla son los tuneles, y en la segunda, una tupla con el listado de robots  
    initial_state = (tuneles,[]) #le agregamos la lista de tuplas con las posiciones de los casilleros

    for robot in robots: #recorremos la lista de robots
        if(robot[1] == "escaneador"):
            initial_state[1].append((robot[0],"escaneador", (5,0), 1000)) #id robot, posicion, bateria, tipo
        else:
            initial_state[1].append((robot[0],"soporte", (5,0), 10000))
            
    initial_state = to_tuple(initial_state)


    # Clase del problema
    class RobotsMineriaProblem(SearchProblem):

        # El costo sera los minutos a moverse o el tiempo en cargar
        def cost(self, state1, action, state2):
            id_robot, action_type, new_position_id_robot_cargar = action
            if(action_type == 'mover'):
                return 1
            return 5
        
        # Las acciones son tuplas de 3 elementos: (id_robot_realiza_accion, tipo_accion, nueva_posicion o id_robot_cargar)
        def actions(self, state):
            available_actions = []

            # separamos tuneles de los robots del estado
            tuneles_pendientes, robots = state

            for actual_robot in robots:

                # Desglosar la información de los robots
                id_robot, type, position, batery = actual_robot
                
                if  batery >=100: # vemos las distintas posiciones donde se movera no importa el tipo ya que ambos se deben mover
                    posible_move = [] #Lista de posible movimientos
                    posible_move.append((position[0]-1, position[1])) # movimiento hacia abajo
                    posible_move.append((position[0]+1, position[1])) #movimienito hacia arriba
                    posible_move.append((position[0], position[1]-1)) #movimiento hacia izquierda
                    posible_move.append((position[0], position[1]+1)) #movimiento hacia derecha
                    # de aca, algunas no son posibles acceder, por ende hay que filtrarlas:
                    for new_position in posible_move:
                        if new_position in tuneles:
                            available_actions.append((id_robot, 'mover', new_position))

                # generar acciones de carga para los robots de carga
                if type == "soporte":
                    for robot_to_charge in robots:
                        if robot_to_charge[2] == position and robot_to_charge[3] < 1000 and robot_to_charge[3] >= 0:
                            available_actions.append((id_robot, 'cargar', robot_to_charge[0]))

            return available_actions

        def result(self, state, action):
            # separar estado
            pending_tunnels, robots = state
            # Pasamos a lista para poder modificar
            pending_tunnels = list(pending_tunnels)
            
            # Convertir a listas las tuplas de estado robots para luego poder modificarlas
            robots = to_list(robots)
            
            # separamos las distintas partes del action
            id_robot, action_type, new_position_id_robot_carga = action

            # Si el tipo de acción es mover, 
            # modificar el estado asignándole al robot correspondiente la nueva posición
            if(action_type == 'mover'):
                # buscamos en la lista de robots el robot que hace la accion
                robot_to_move = search_robot(robots,id_robot)
                robot = robot_to_move[0] 
                id_robot_move = robot[0]
                robots[id_robot_move][2] = new_position_id_robot_carga

                # Si es escaneador (no de soporte) restar 100 a la batería
                if(robot[1][1] == "soporte"):
                    robots[id_robot_move][3] -= 100
                    # Eliminar la coordenada del túnel que se está escaneando de 
                    # la lista de túneles pendientes
                    if new_position_id_robot_carga in pending_tunnels:
                                pending_tunnels.remove(new_position_id_robot_carga)
            else:
                # Si el tipo de acción es cargar, modificar la batería del robot que se quiere cargar a 1000 new_position_id_robot_carga
                robot_to_charge = search_robot(robots,new_position_id_robot_carga)
                robot_charge = robot_to_charge[0] 
                id_robot_charged = robot_charge[0]
                robots[id_robot_charged][3] = 1000

            # Convertir a tuplas los elementos del estado
            pending_tunnels = tuple(pending_tunnels)
            robots = to_tuple(robots)

            return (pending_tunnels, robots)
        
        def is_goal(self, state):
            #separamos estado de robots
            boxs, robots = state
            #si quedan en el estado casillas por recorrrer devolvera false, sino true.
            return len(boxs) == 0
        
        def heuristic(self, state):
            # La heurística es la cantidad de túneles que faltan recorrer
            # multiplicados por 1 minuto
            return (len(state[0]))
                    
    problema = RobotsMineriaProblem(initial_state)

    resultado = astar(problema, graph_search=True)

    plan = []

    # Recorrer el resultado agregando a la lista plan, 
    # las acciones seleccionadas por el algoritmo
    for action, state in resultado.path():
        # Descartar la primera acción que es None
        if (action is not None):
            plan.append(action)
    return plan
