from simpleai.search import (SearchProblem,astar,)
    # Tenemos que saber: 
    # donde esta el robot 
    # - cual es el camino que ya recorrio (conocer cuales casilleros ya fueron recorridos)
    # - que tipo de robot es (mapeador - soporte)

    # - escaneador -> puede moverse un máximo de 10 movimientos (1000 mAh / 100 mah por movimiento)
    # - soporte -> mismo consumo de movientos (costo), que el mapeador
    # soporte carga en 5 min al mapeador (por ende, debemos tener guardada la posicion que logro recorrer el mapeador)
    # llevar constancia del nivel de bateria del mapeador (ya que no necesariamente debe ser cargado al agotar su bateria)
    # la bateria del mapeador se carga en su totalidad

# Return a list of robots filtered by id.
def search_robot(robots, id):                                                                      
    return list(filter(lambda robot: robot[1][0] == id, enumerate(robots)))

# Convert tuple to lists.  
def to_list(tuples):
    return [list(x) for x in tuples]

# Convert list to tuples.
def to_tuple(lists):
    return tuple([tuple(x) for x in lists])

def planear_escaneo(tuneles, robots):
    # Our initial state was a tuple where the first part are tunnels, and the second,
    # a tuple with the list of robots.
    initial_state = (tuneles, []) 

    for robot in robots: # recorremos la lista de robots
        if(robot[1] == "escaneador"):
            initial_state[1].append((robot[0],(5,0), 1000)) #id robot, posicion, bateria, tipo
        else:
            initial_state[1].append((robot[0],(5,0), 10000)) #nro para diferenciar el de la bateria

    initial_state = to_tuple(initial_state)


    # Clase del problema
    class RobotsMineriaProblem(SearchProblem):
        
        # Las acciones son tuplas de 3 elementos: (id_robot_realiza_accion, tipo_accion, nueva_posicion o id_robot_cargar)
        def actions(self, state):
            available_actions = []

            # separamos tuneles de los robots del estado
            pending_tunnels, robots = state

            for actual_robot in robots:

                # Desglosar la información de los robots
                id_robot, position, batery = actual_robot
                posible_move = []

                if  batery >= 100: # vemos las distintas posiciones donde se movera no importa el tipo ya que ambos se deben mover
                    row_robot, col_robot = position #separamos la posicion en fila y columna
                    
                    new_position = (row_robot - 1, col_robot) # vemos la de arriba
                    posible_move.append((new_position))         
                    new_position = (row_robot + 1, col_robot) # vemos la de abajo
                    posible_move.append((new_position))
                    new_position = (row_robot, col_robot - 1) # vemos a la izq
                    posible_move.append((new_position))  
                    new_position = (row_robot, col_robot + 1) # vemos a la derecha
                    posible_move.append((new_position))

                    # de aca, algunas no son posibles acceder, por ende hay que filtrarlas:
                    for new_position in posible_move:
                        # si la casilla que nos pasaron en el mapa, existe en el mismo
                        # agregamos una acción nueva
                        if new_position in tuneles:
                            available_actions.append((id_robot, 'mover', new_position))

                # generar acciones de carga para los robots de carga
                if batery == 10000:
                    for robot_to_charge in robots:
                        id_robot_to_charge, position_charge, batery_to_charge = robot_to_charge 
                        if position_charge == position and batery_to_charge < 1000:
                            available_actions.append((id_robot, 'cargar', id_robot_to_charge))

            return available_actions

        def result(self, state, action):
            # separar estado
            pending_tunnels, robots = state
            # Pasamos a lista para poder modificar
            pending_tunnels = list(pending_tunnels)
            
            # Convertir a listas las tuplas de estado robots para luego poder modificarlas
            robots = to_list(robots)
            
            # Separamos las distintas partes del action
            id_robot, action_type, new_position_id_robot_carga = action

            # Si el tipo de acción es mover, 
            if(action_type == 'mover'):
                # buscamos en la lista de robots el robot que hace la accion
                robot_to_move = search_robot(robots,id_robot)
                robot = robot_to_move[0] 
                id_robot_move = robot[0] #asignamos el id para luego buscar en la lista
                robots[id_robot_move][1] = new_position_id_robot_carga #asignamos nueva posicion

                # Si es escaneador hay que restar la bateria
                if(robot[1][2] != 10000):
                    robots[id_robot_move][2] -= 100
                    if new_position_id_robot_carga in pending_tunnels:
                                pending_tunnels.remove(new_position_id_robot_carga) #borramos el tunel de los pendientes
            else:
                # Action: 'cargar'
                robot_to_charge = search_robot(robots,new_position_id_robot_carga)#buscamos el robot a cargar
                robot_charge = robot_to_charge[0]  
                id_robot_charged = robot_charge[0] #asignamos el id para luego buscar en la lista
                robots[id_robot_charged][2] = 1000 #llenamos bateria

            # Covert to tuple
            pending_tunnels = tuple(pending_tunnels)
            robots = to_tuple(robots)

            return (pending_tunnels, robots)
        
        def cost(self, state1, action, state2):

            id_robot, action_type, new_position_id_robot_cargar = action

            if(action_type == 'mover'):
                return 1
            return 5

        def is_goal(self, state):
            boxes, robots = state
            # If the state have boxes unvisited, return false.
            return len(boxes) == 0
        
        def heuristic(self, state):
            # The heurisc is the sum of boxes that we have to visit.
            boxes, robots = state
            boxes_not_visited = 0

            for box in boxes:
                boxes_not_visited += 1
            return boxes_not_visited
                    
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

# plan = planear_escaneo(
#     tuneles = [ # lista de tuplas de coordenadas de todos los casilleros que son túneles, en formato (fila, columna),
#                 # usando  los índices del dibujo. No incluye la entrada (5, 0), que no es necesario escanear.
#         (5, 1),
#         (6, 1),
#         (6, 2),
#     ],
#     robots = [ # lista de tuplas con la estructura (id del robot, tipo de robot)
#         ("s1", "soporte"), 
#         ("e1", "escaneador"),
#         ("e2", "escaneador"),
#         ("e3", "escaneador"),
#     ],
# )
# print(plan)


