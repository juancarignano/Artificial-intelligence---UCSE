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

# - mapeador -> puede moverse un máximo de 10 movimientos (1000 mAh / 100 mah por movimiento)
# - soporte -> mismo consumo de movientos (costo), que el mapeador
# soporte carga en 5 min al mapeador (por ende, debemos tener guardada la posicion que logro recorrer el mapeador)
# llevar constancia del nivel de bateria del mapeador (ya que no necesariamente debe ser cargado al agotar su bateria)
# la bateria del mapeador se carga en su totalidad

# 1 robot a la vez (turnos)

"""
Determinar si una casilla existen en el recorrido planteado para la mina.
"""
def exists(position, boxs):
    if position in boxs[0]:
        return True

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
        nueva posición del robot
    )
    """

    def actions(self, state):
        available_actions = []
        boxs, robots = state
        
        for actual_robot in robots:

            id_robot, robot_type, robot_position, battery = actual_robot # tipo de robot, posición y batería.
            row_robot, col_robot = robot_position 

            if robot_type ==  "escaneador" and battery > 0:
                    # the piece above
                    if row_robot > 0:
                        new_position = (row_robot - 1, col_robot)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))         
                    # the piece below
                    if row_robot < 9:
                        new_position = (row_robot + 1, col_robot)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))
                    # the piece to the left
                    if col_robot > 0:
                        new_position = (row_robot, col_robot - 1)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))  
                    # the piece to the right
                    if col_robot < 9:
                        new_position = (row_robot, col_robot + 1)
                        if exists(new_position, boxs):
                            available_actions.append((id_robot, "Mover", new_position))

            else: # robot soporte
                for robot in robots:
                    if robot[1] == "escaneador" and robot[3] < 10:
                        available_actions.append(id_robot, "Cargar", robot[2]) # la posición es robot[2] ya que es la actual del robot al cual se va a cargar.

        return available_actions

    def result(self, state, action):
        state_as_lists = list(list(row) for row in state)
        boxs, robots = state_as_lists

        boxs_as_lists = list(list(row) for row in boxs)
        robots_as_lists = list(list(row) for row in robots)

        # 1- actualizar posición del robot que esta ejecutando la acción (OK)
        # 2- decirle a la nueva casilla que ya esta escaneada

        for robot in robots_as_lists:
            if robot[0] == action[0]:
                robot[2] = action[2] # asigno al robot que hace la acción, la posición nueva (generada en el acción).
            

        if action[1] == "Mover":
            for box in boxs_as_lists:            # recorremos las casillas 
                if box[0] == action[2]: # encontramos la posición nueva
                    box[1] = True       # asignamos true al [1] de box --> ya está escaneada

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
