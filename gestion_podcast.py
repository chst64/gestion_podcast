#!/usr/bin/env python3

"""
File:  gestion_podcast.py
Author: Pablo J
Email: chst64@gmail.com
Github: https://github.com/yourname
Description: 
    Este es un programa que lee un fichero xml con todos los capitulos del
    podcast y descarga todos los capitulos y los guarda en formato:
    20201003_titulo del podcast.mp3, donde 20201003 es año2020, mes10 y dia 03
    tambien se escribe los datos de los IDTags del mp3


=== TODO ===
- Elegir el directorio donde guardar los podcast
- Algunos podcast como 6minutesEnglish estan en otro formato (formato itunes??)
"""


import eyed3
from xml.dom import minidom
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
import string
import unicodedata
import os
import sys
import argparse



PODCAST = ""
FILENAME = ""

# Diccionario donde se guardan la URL del podcast y como se guardara en local
# Formato: palabra_clave:["url del xml","fichero como se guarda en xml","Autor"]
DICC_PODCAST = {"nieves":["http://fapi-top.prisasd.com/podcast/playser/cualquier_tiempo_pasado_fue_anterior/itunestfp/podcast.xml",
            "./todo_concostrina.xml", "Nieves Concostrina", "Todo concostrina"],
        "nadie":["https://fapi-top.prisasd.com/podcast/playser/nadie_sabe_nada/itunestfp/podcast.xml",
            "./nadie.xml","Buenafuente y Romero","Nadie sabe nada"],
        "linux":["https://podcastlinux.com/feed_mp3","./linux.xml","Juan Febles","nada"],
        "vaughan":["https://www.ivoox.com/feed_fg_f180769_filtro_1.xml","vaughan.xml","Vaughan","Album"],
        "dragones":[ "http://fapi-top.prisasd.com/podcast/podium/aqui_hay_dragones.xml","dragones.xml","Artista","Album"],
        "6min":[ "https://podcasts.files.bbci.co.uk/p02pc9tn.rss","6min.xml","Artista","Album"],
        "domotica":[ "https://www.ivoox.com/domotica-compatible_fg_f11161752_filtro_1.xml","domotica.xml","domotica","Album"],
        "tp":[ "https://www.ivoox.com/todopoderosos_fg_f1147805_filtro_1.xml","todopoderosos.xml","todopoderosos","Album"],
        "pythones":[ "https://podcast.jcea.es/python.xml","pythones.xml","pythones","Album"],
        "programar":[ "https://www.ivoox.com/podcast-programar-es-mierda_fg_f1432444_filtro_1.xml","programar.xml","programar","Album"],
        "realpython":[ "https://realpython.com/podcasts/rpp/feed","realpython.xml","real python","Album"],
        "talkpython":[ "https://talkpython.fm/subscribe/rss","talkpython.xml","talk python","Album"],
        "pythonpodcast":[ "https://www.pythonpodcast.com/rss","python.xml","python podcast","Album"]
        }


#if os.path.exists(FILENAME):
#    doc_xml = ET.parse(FILENAME)
#    raiz = doc_xml.getroot()

lista_episodios = [] # Lista de instancias de Episodios donde se guarda la informacion de cada episodio


def removeDisallowedFilenameChars(filename):
    """
    Elimina los caracteres que no son validos para un fichero y devuelve el nombre corregido
    """
    
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(chr(c) for c in cleanedFilename if chr(c) in validFilenameChars)

class Episodio():

    """Clase de Episodios.

    Args:
        titulo (str): Titulo
        descripcion
        mp3
        fecha
    """

    def __init__(self,titulo,descripcion,mp3,fecha):
        # Si hay un | en el titulo cojo el principio
        if '|' in titulo:
            self.titulo=titulo.split("|")[1] 
        else:
            self.titulo=titulo

        self.titulo = removeDisallowedFilenameChars(self.titulo)

        self.descripcion = descripcion
        self.mp3 = mp3
        self.fecha = fecha
        self.pubdate = self.fecha.strftime('%d-%m-%y')
        self.salida_mp3 = self.fecha.strftime('%y%m%d')+'_'+self.titulo+".mp3"

    def __str__(self):
        cad = f"""
        ***********************
        Titulo: {self.titulo}
        MP3: {self.mp3}
        FicheroMP3: {self.salida_mp3}
        Fecha: {self.fecha}
        ***********************
        """
        return(cad)

    def descarga(self):
        #subprocess.call(["wget","-O",salida_mp3,self.mp3])
        print("Voy a descargar el fichero",self.mp3,"y lo guardo como ",self.salida_mp3)
        resultado = subprocess.run(["wget", "-nv", "-O",self.salida_mp3,self.mp3])
        return(resultado)

def cargar_datos_podcast(fichero_podcast:str) -> list:
    """
    Cargo los datos del fichero.xml de podcast, con los datos creo instancias de la clase Episodio y guardo todas esas instancias en lista_episodios[]
    
    """
    lista_episodios = []
    try:
        doc_xml = ET.parse(FILENAME)
    except Exception as e:
        print("!!! Ha ocurrido un ERROR: !!!",e)
        sys.exit(1)


    raiz = doc_xml.getroot()

    for episodio in raiz.iter('item'):
        titulo = episodio.find("title").text
        descripcion = episodio.find("description").text
        mp3 = episodio.find("enclosure").get("url")
        fecha = episodio.find("pubDate").text
        fecha = fecha[:16] # Recorto la fecha para dejar solo en formato Tue, 28 Jun 2016
        pubDate = datetime.strptime(fecha,"%a, %d %b %Y")

        # Creo una instancia de episodio con los datos
        mi_episodio=Episodio(titulo, descripcion, mp3, pubDate)

        # Meto el episodio en la lista e episodios
        lista_episodios.append(mi_episodio)

    return lista_episodios



def imprime_info_episodios(rango):
    """
    Imprime los ultimos NUMERO episodios
    """
    
    if len(rango)==2:
        for n in range(rango[0],rango[1]):
            print("=== Episodio ",n,"===")
            print( lista_episodios[n] )

    else:
        print(lista_episodios[rango[0]])
    

def descarga_episodios(episodios,artista=None,album=None):
    """
    Descarga los ultimos NUMERO episodios
    """
    #if len(rango)==2:
    #    for n in range(rango[0],rango[1]):
    #        print("=== Descargando episodio ",n,"===")
    #        lista_episodios[n].descarga()

    #else:
    #    print("=== Descargando episodio ",rango[0],"===")
    #    lista_episodios[rango[0]].descarga()
    
    for epi in episodios:
        epi.descarga()
        modifica_tag(epi,artista,album)





def modifica_tag(episodio,artista,album):
    """
    Modifica el idtag de un fichero mp3.
    Se sobreescribe el artista, el album y el titulo.
    El artista y el album son fijos pero el titulo lo coje de la informacion
    de la instancia de la clase "Episodio" 

    Parametros:
    fichero: es una instancia de la clase Episodio
    artista: el valor de artista que hay que poner
    album: el valor de album que hay que poner

    """

    
    print("********************")
    print("Modifica tag:",episodio.salida_mp3)
    print("********************")

    try:
        audiofile = eyed3.load(episodio.salida_mp3)
    except OSError:
        print("No se encuentra el fichero",episodio.salida_mp3)
    else:
        audiofile.tag.artist = artista 
        audiofile.tag.album = album 
        audiofile.tag.title = episodio.titulo.lstrip(' ') #Quito los espacios de la izquierda
        audiofile.release_date = episodio.pubdate
        audiofile.tag.save()

# *****************************
# * PROGRAMA PRINCIPAL *
# *****************************

if __name__=="__main__":
    
    # Configuracion de parametros
    parser = argparse.ArgumentParser(description="Descarga de podcast",
            epilog="""Programa para actualizar los podcast (gestion_podcast.py nieves -u )descargar los podcast(gestion_podcast nieves -d 0 9), renombrarlos y modificar su id3tag
            """)

    parser.add_argument('podcast',
            help="""Podcast a gestionar.Las opciones son:
            nieves = podcast de "Nieves Concostrina"
            nadie = Podcast de "Nadie Sabe Nada"
            linux = Podcast Linux de Juan Febles
            6min = Podcast de 6 minutes English
            dragones = Podcast Aqui hay dragones
            vaughan = Podcast Vaughan
            domotica = Domotica compatible
            """
            )
    parser.add_argument('--actualiza',
            '-u',
            action='store_true',
            help="Actualiza el fichero xml de podcast"
            )

    parser.add_argument('--info','-i', type=int, 
            help="informacion de los ultimos N episodios, donde 0 es el ultimo episodio. Ej: ./gestion_podcast.py nieves -i 2 ",
            nargs="+")

    parser.add_argument('--descarga', '-d',  type=int,
            help="descarga el episodio N ó un rango entre 2 episodios",
            nargs="*")
    

    args = parser.parse_args()


    if args.podcast:
        if args.podcast in DICC_PODCAST:
            print("Podcast ",DICC_PODCAST[args.podcast][0])
            FILENAME = DICC_PODCAST[args.podcast][1]
            PODCAST = DICC_PODCAST[args.podcast][0]
            print("Filename:",FILENAME)
            print("Podcast:",PODCAST)

    if args.actualiza:
        print("Actualizando fichero xml")
        resultado = subprocess.run(["wget", "-nv", PODCAST, "-O",FILENAME])

    if args.info:

        # Primero cargo los datos del fichero xml a lista_episodios[]
        lista_episodios = cargar_datos_podcast(FILENAME)

        print("info:",args.info)
        imprime_info_episodios(args.info)

    if args.descarga:
        if len(args.descarga) != 2:
            print(f"""ERROR: Tienes que pasar 2 numeros al rango de descargas
                    Ejecuta gestion_podcast.py nombre_podcast -d 2 4 para descargar los episodios del 2 al 4""")

            sys.exit(0)

        else :
           # Primero cargo los datos del fichero xml a lista_episodios[]
            # print("*** args.descarga: ",args.descarga)
            lista_episodios = cargar_datos_podcast(FILENAME)
            descarga_episodios(
                    lista_episodios[args.descarga[0]:args.descarga[1]],
                    artista=DICC_PODCAST[args.podcast][2],
                    album=DICC_PODCAST[args.podcast][3])


