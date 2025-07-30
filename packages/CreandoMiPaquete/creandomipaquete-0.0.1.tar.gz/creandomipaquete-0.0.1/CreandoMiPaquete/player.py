# creando documentacion
"""
Este es el modulo que incluye la clase de 
reproductor de musica
"""

class Player:
    """
    Esta clase crea un reproductor de musica
    """
    def reproducir(self, cancion):
        """
        Reproduce la cancion que recibio

        parametros:
        cancion(str): es un string con el path de la cancion

        returns:
        int: devuleve 1, con exito, 0 si en caso de fracaso
        """
        print(f'reproduciedo la cancion {cancion}')

    def stop(self, cancion):
        """
        Detiene la ejecucion de una cancion
        """
        print(f'stoping de la cancion {cancion}')
