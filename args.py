import sys, os, argparse

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--commit', help='[nom de commit] sauvegarde le travail en package pour versionning')
    parser.add_argument('-p', '--production', help='[0 = local] [1 = production] génère les fichiers html dans le répertoire local ou production', default=0)
    parser.add_argument('-v', '--verbose', help='[1] log en mode debug', default=0)
    parser.add_argument('-i', '--idx', help='[1] do just indexes', default=0)
    args = parser.parse_args()


    
