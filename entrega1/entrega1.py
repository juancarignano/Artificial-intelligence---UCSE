from simpleai.search import (
    SearchProblem,
    breadth_first,
    depth_first,
    uniform_cost,
    limited_depth_first,
    iterative_limited_depth_first,
    # informed search
    greedy,
    astar,
)
from simpleai.search.viewers import WebViewer, BaseViewer

# Tenemos que saber: 
# OK- donde esta el robot 
# - cual es el camino que ya recorrio (conocer cuales casilleros ya fueron recorridos)
# - que tipo de robot es (mapeador - soporte)

# - escaneador -> puede moverse un máximo de 10 movimientos (1000 mAh / 100 mah por movimiento)
# - soporte -> mismo consumo de movientos (costo), que el mapeador
# soporte carga en 5 min al mapeador (por ende, debemos tener guardada la posicion que logro recorrer el mapeador)
# llevar constancia del nivel de bateria del mapeador (ya que no necesariamente debe ser cargado al agotar su bateria)
# la bateria del mapeador se carga en su totalidad

# 1 robot a la vez (turnos)

"""
Determinar si una casilla existen en el recorrido planteado para la mina.
"""
def exists(position, boxs):
    for boxes in boxs:
        if position == boxes[0]:
            return True
    return False

class RobotsMineriaProblem(SearchProblem):
    def __init__(self, tunnels, robots):

        initial_tunnels = []
        initial_robots = []

        # Recorremos los túneles y los agregamos al initial_state.
        # False que pasamos en la tupla = casillero no recorrido.
        for box in tunnels:
            initial_tunnels.append((box, False))
        
        # Recorremos los robots y los agregamos al initial_state (robot, posición, batería).
        for robot in robots:
            id_robot, robot_type = robot
            battery = 10 # 10 de bateria = 100% (llena)
            initial_robots.append((id_robot, robot_type, (5, 0), battery))

        initial_state = (tuple(initial_tunnels), tuple(initial_robots))

        super().__init__(initial_state=initial_state)

    def cost(self, state1, action, state2):
        if action[1] == "Mover":
            return 1
        else: 
            return 5 # costo de cargar = 5

    def is_goal(self, state):
        boxs, robots = state

        for box in boxs:
            if box[1] == False:
                return False
        return True # todas las casillas con box[1] = True, quiere decir que recorrió todas las casillas.


    """
    mapeador -> moverse
    soporte -> cargar 
    accion = robot -> (
        id robot que hace la accion,
        tipo de acción,
        nueva posición del robot/id robot a cargar
    )
    """

    def actions(self, state):
        available_actions = []
        boxs, robots = state
        
        for actual_robot in robots:

            id_robot, robot_type, robot_position, battery = actual_robot # id, tipo de robot, posición y batería.
            row_robot, col_robot = robot_position #fila, columna

            if robot_type ==  "escaneador" and battery > 0:
                    #filas de la nro 1 hasta la 11 ya que la 0 no tiene otra atras 
                    if row_robot > 0:
                        new_position = (row_robot - 1, col_robot)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))         
                    #filas de la nro 0 hasta la 10 ya que la 11 no tiene otra siguiente
                    if row_robot < 11:
                        new_position = (row_robot + 1, col_robot)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))
                    #columna de la nro 1 hasta la 11 ya que la 0 no tiene una a la izq.
                    if col_robot > 0:
                        new_position = (row_robot, col_robot - 1)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))  
                    #columna de la nro 0 hasta la 10 ya que la 11 no tiene una a la izq.
                    if col_robot < 11:
                        new_position = (row_robot, col_robot + 1)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))

            else: # robot soporte
                for robot in robots:
                    if robot[1] == "escaneador" and robot[3] < 10 and robot[2] == robot_position :  #si el robot soporte esta en la misma posicion que un escaneador que no tiene bateria full, da la opcion de recargarlo
                        available_actions.append((id_robot, "Cargar", robot[0])) 
                
                #ahora le pasamos los distintos lugares donde se puede mover el soporte.
                #filas de la nro 1 hasta la 11 ya que la 0 no tiene otra atras
                if row_robot > 0:
                    new_position = (row_robot - 1, col_robot) #vemos si el casillero de abajo esta disponible
                    if exists(new_position, boxs):
                        available_actions.append((id_robot, "Mover", new_position))         
                #filas de la nro 0 hasta la 10 ya que la 11 no tiene otra siguiente
                if row_robot < 11:
                    new_position = (row_robot + 1, col_robot)
                    if exists(new_position, boxs):
                        available_actions.append((id_robot, "Mover", new_position))
                #columna de la nro 1 hasta la 11 ya que la 0 no tiene una a la izq.
                if col_robot > 0:
                    new_position = (row_robot, col_robot - 1)
                    if exists(new_position, boxs):
                        available_actions.append((id_robot, "Mover", new_position))  
                #columna de la nro 0 hasta la 10 ya que la 11 no tiene una a la izq.
                if col_robot < 11:
                    new_position = (row_robot, col_robot + 1)
                    if exists(new_position, boxs):
                        available_actions.append((id_robot, "Mover", new_position))
        
        
        return available_actions

    def result(self, state, action):
        state_as_lists = list(list(row) for row in state)
        boxs, robots = state_as_lists

        boxs_as_lists = list(list(row) for row in boxs)
        robots_as_lists = list(list(row) for row in robots)

        # 1- ver que tipo de accion es
        if action[1] == "Mover":
            #asigno al robot la nueva ubicacion 
            for robot in robots_as_lists:
                if robot[0] == action[0]: #encontramos al robot que indica la accion
                    robot[2] = action[2]  #el robot en la pos 2 tiene la ubicacion actual, accion en 2 tiene la ubicacion nueva
                     # revisamos si el tipo 
                    if robot[1] == "escaneador":
                        #restamos bateria
                        robot[3] -= 10
                        #indico que la nueva casilla a la que se movio el robot pasa a ser escaneada
                        for box in boxs_as_lists:   # recorremos las casillas 
                            if box[0] == action[2]: # encontramos la posición nueva
                                box[1] = True       # asignamos true al [1] de box --> ya está escaneada


        else: #es cargar
            for robot in robots_as_lists:
                if robot[0] == action[0]: # encontramos el robot soporte que va a cargar
                    for scanners in robots_as_lists:
                        if scanners[0] == action[2]: #encontramos el robot al que se le va cargar la bateria
                            scanners[3] = 10       
 
        #pasamos a tupla para que quede como el estado.
        # Casilleros (posicion, recorrido true/false)
        # Robots (id, tipo, posicion, cant bateria)
        new_boxs = tuple(tuple(row) for row in boxs_as_lists)
        new_robots = tuple(tuple(row) for row in robots_as_lists)

        new_state = (new_boxs, new_robots)
    
        return new_state


    """
    Cantidad de casillas no visitas.
    """
    def heuristic(self, state):
        boxs, robots = state
        boxs_not_visited = 0

        for box in boxs:
            if box[1] == False:
                boxs_not_visited += 1
        return boxs_not_visited
        
viewer = BaseViewer()

def planear_escaneo(tuneles, robots):
    
    problem = RobotsMineriaProblem(tuneles, robots)
    result = astar(problem, graph_search=True, viewer=viewer)
    return result

plan = planear_escaneo(
    tuneles = [ # lista de tuplas de coordenadas de todos los casilleros que son túneles, en formato (fila, columna),
                # usando ​los índices del dibujo. No incluye la entrada (5, 0), que no es necesario escanear.
        (5, 1),
        (6, 1),
        (6, 2),
    ],
    robots = [ # lista de tuplas con la estructura (id del robot, tipo de robot)
        ("s1", "soporte"), 
        ("e1", "escaneador"),
        ("e2", "escaneador"),
        ("e3", "escaneador"),
    ],
)