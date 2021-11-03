from typing import Tuple
from simpleai.search import CspProblem, backtrack

#Mejoras
#En baterias, ruedas, carga extra, comunicacion

#Variable
#Mejora baterias:
    #Dominio:
    # Bateria chica: aumneta a 5000 mAh y costo moverse +10
    # Bateria mediana: aumneta a 7500 mAh y costo moverse +20
    # Bateria grande: aumneta a 10000 mAh y costo moverse +50 y necesita en mejora ruedas + oruga
#Mejora Ruedas:
    #Dominios:
    # Patas extras: costo + 15
    # motores extra: costo + 25
#Mejora carga extra:
    #Dominios:
    # suministros humanitarios ARRIBA: Costo movimiento + 10
    # ATRAS: NO SE PUEDE PONER EN RUEDAS EXTRA PATAS Y COSTO +10
    
def rediseñar_robot():

    #Variables del problema son cada una de las mejoras posibles.
    variables = [
        "Mejora_Bateria",
        "Mejora_Ruedas",
        "Mejora_carga_extra",
        "Mejora_comunicacion"
    ]
    #El dominio esta compuesto por: variable = ("nombre mejora", aumento de bateria, aumento en costo por movimiento)
    domains = {
            "Mejora_Bateria": [("baterias_chicas", 5000, 10), ("baterias_medianas", 7500, 20), ("baterias_grandes", 10000, 50)],
            "Mejora_Ruedas": [("patas_extras", 0, 15), ("mejores_motores", 0, 25), ("orugas", 0, 50)],
            "Mejora_carga_extra": [("caja_superior", 0, 10), ("caja_trasera", 0, 10)],
            "Mejora_comunicacion": [("radios", 0, 5), ("video_llamadas", 0, 10)]
        }

    # Solo se puede tener 1 mejora de cada tipo. 
    # Restricciones:
    constraints = []
    # Si Merjora_bateria = baterias_grandes <==> Mejora_Ruedas = orugas
    def validar_bateriagrande_oruga(variables, values):
        mejoraBateria,mejoraRueda, mejoracargaExtra, mejoraComunicacion = values
        if mejoraBateria[0] == "baterias_grandes":
            if mejoraRueda[0] != "orugas":
                return False

        return True                 

    constraints.append((variables, validar_bateriagrande_oruga))

    # si Mejora_carga_extra = caja_trasera <==> Mejora_patas != patas extra
    def validar_no_patas_extras(variables, values):
        mejoraBateria,mejoraRueda, mejoracargaExtra, mejoraComunicacion = values
        if mejoracargaExtra[0] == "caja_trasera":
            if mejoraRueda[0] ==  "patas_extras":
                return False

        return True
            

    constraints.append((variables, validar_no_patas_extras))

    #Si hay radios, no hay mejoras en los motores 
    # —> Mejora comunicacion = radio <==> mejora rueda != mejores motores
    def validar_radio_sin_motores(variables, values):
        mejoraBateria,mejoraRueda, mejoracargaExtra, mejoraComunicacion = values
        if mejoraComunicacion[0] == "radios":
            if mejoraRueda[0] == "mejores_motores":
                return False
        
        return True

    constraints.append((variables, validar_radio_sin_motores))

    #si hay videollamadas, se necesita par extras de patas u orugas 
    # —> Mejora comunicacion = videollamada <==> mejora rueda = patas extras o mejora rueda = oruga
    def validar_videollamada_con_patas_extra(variables, values):
        mejoraBateria,mejoraRueda, mejoracargaExtra, mejoraComunicacion = values
        if mejoraComunicacion[0] == "video_llamadas":
            if mejoraRueda[0] == "patas_extras" or mejoraRueda[0] == "orugas":
                return True
            else:
                return False

        return True
    
    constraints.append((variables, validar_videollamada_con_patas_extra))

    # la autonomia debe ser de 50 min —> autunomia >= 50
    def validar_autonomia(variables, values):
        mejoraBateria,mejoraRueda, mejoracargaExtra, mejoraComunicacion = values
        bateria = 1000 + mejoraBateria[1]
        costos_movimientos = 100 + mejoraBateria[2] + mejoraRueda[2] + mejoracargaExtra[2] + mejoraComunicacion[2]
        return (bateria / costos_movimientos) >= 50
    
    constraints.append((variables, validar_autonomia))
    

    problem = CspProblem(variables, domains, constraints)
    result = backtrack(problem)
    if result is None:
        return "result is None"
    return [actualizacion[0] for mejora, actualizacion in result.items()]


if __name__ == '__main__':
    print('Trabajo Práctico Inteligencia Artificial')
    adaptaciones = rediseñar_robot()
    print(adaptaciones)
    

    



