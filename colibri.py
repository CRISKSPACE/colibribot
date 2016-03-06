# -*- coding: UTF-8 -*-
from itertools import izip
import Image,os,glob,time,sys,random
from twython import Twython
from datetime import datetime

#fonction de comparaison de photo
#retourne un pourcentage de difference
def compare_photo(image1,image2) :
	i1 = Image.open(image1)
	i2 = Image.open(image2)
	assert i1.mode == i2.mode, "Different kinds of images."
	assert i1.size == i2.size, "Different sizes."
	pairs = izip(i1.getdata(), i2.getdata())
	if len(i1.getbands()) == 1:
   	 # for gray-scale jpegs
    		dif = sum(abs(p1-p2) for p1,p2 in pairs)
	else:
    		dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
	ncomponents = i1.size[0] * i1.size[1] * 3
	#print "Difference (percentage):", (dif / 255.0 * 100) / ncomponents
	return (dif / 255.0 * 100) / ncomponents


#liste de photo de references
dico = {}
dico["absent"] = ["/home/pi/colibri/ref_parti_oeuf.jpg",100.0]
dico["couve face"] = ["/home/pi/colibri/ref_couve_face.jpg",100.0]
dico["nuit"] = ["/home/pi/colibri/ref_nuit.jpg",100.0]
dico["couve dos"] = ["/home/pi/colibri/ref_couve_dos.jpg",100.0]
dico["repas"] = ["/home/pi/colibri/ref_repas.jpg",100.0]
dico["fly"] = ["/home/pi/colibri/ref_fly.jpg",100.0]

#ouverture fichier de log
fichier_log = open("/home/pi/colibri/colibri_log.txt", "a")
fichier_log.write("-------------------------\n")
fichier_log.write("Start script at %r\n" % time.strftime('%d/%m/%y %H:%M:%S',time.localtime()))

#recuperation de l'image la plus recente fournie par motion
newest = max(glob.iglob('/var/lib/motion/*.jpg'), key=os.path.getctime)
fichier_log.write('Image en cours d\'analyse :%r\n' % newest)

#comparer la photo avec la banque de references
for key, value in dico.iteritems():
	value[1] = compare_photo(value[0],newest)
	fichier_log.write('Difference avec %r : %r \n' % (key,value[1]))

#determination de la photo de reference la plus proche
current_rate = 100.0
current_status = "status inconnu ..."
for key, value in dico.iteritems():
	if current_rate > value[1]:
		current_rate = value[1]
		current_status = key

fichier_log.write('*** %r ***\n' % current_status)

#recuperation du status precedent
last_status = "status inconnu ..."
fichier = open("/home/pi/colibri/last_colibri_status.txt", "r")
last_status = fichier.readline()
fichier.close()

if current_rate > 20.0:
	current_status = last_status

if (last_status == "status inconnu ...") or (last_status != current_status):
	fichier = open("/home/pi/colibri/last_colibri_status.txt", "w")
	fichier.write(current_status)
	fichier.close()
	fichier_log.write("sauvegarde d'un nouveau status\n")
	fichier_historique = open("/home/pi/colibri/colibri_status_historique.txt", "a")
	fichier_historique.close()
	#twitter (a remplir)
	CONSUMER_KEY = ''
	CONSUMER_SECRET = ''
	ACCESS_KEY = ''
	ACCESS_SECRET = ''
	api = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)

	transitions = {}
	transitions_absent = {}
	transitions_couve_dos = {}
	transitions_couve_face = {}
	transitions_nuit = {}
	transitions_repas = {}
	transitions_fly = {}

	# -> couve face
	transitions_absent	["couve face"]=["De retour au nid, il faut bien prôtéger mes deux petits oisillons #bot",
						"Fini la balade il faut surveiller ce nid #bot",
						"Je suis parti longtemps ? #bot",
						"Un petit nid douillet #bot #humour",
						"C'est quoi cette grosse boule noire qui me regarde ? #bot #suspicieux",
						"Il parait que l'on ai observé ... #bot"]
	transitions_couve_dos	["couve face"]=["Allez on change de côté #bot",
						"Retour à mon meilleur profil ! #bot"]
	transitions_nuit	["couve face"]=["Une nouvelle journée commence ! #bot",
						"On se réveille les oisillons ! #bot"]
	transitions_repas	["couve face"]=["Petite sieste pour la digestion #bot",
						"Restez au chaud j'ai senti quelques goutes de pluie ... #bot #saisondespluies #merepoule"]
	transitions_fly		["couve face"]=["Atterissage maîtrisé ... #bot #artofflight",
					        "J'arriiiiiiive #bot",
					        "Colibri, vous avez l'autorisation d'atterrir, roger #bot"]

	
	# -> couve dos
	transitions_absent	["couve dos"]=transitions_absent["couve face"]
	transitions_couve_face	["couve dos"]=["On tourne on tourne, je commence à avoir les ailes engourdies #bot",
					       "Tiens j'ai entendu un bruit par là ... #bot"]
	transitions_nuit	["couve dos"]=transitions_nuit["couve face"]
	transitions_repas	["couve dos"]=transitions_repas["couve face"]
	transitions_fly		["couve dos"]=transitions_fly["couve face"]

	# -> nuit
	transitions_absent	["nuit"]=["Bonne nuit ! #bot",
					  "Allez dodo #bot",
					  "Rude journée, au repos ! #bot"]
	transitions_couve_face	["nuit"]=transitions_absent["nuit"]
	transitions_couve_dos	["nuit"]=transitions_absent["nuit"]
	transitions_repas	["nuit"]=transitions_absent["nuit"]
	transitions_fly		["nuit"]=transitions_fly["couve face"]

	# -> absent
	transitions_couve_dos	["absent"]=["Regardez mes deux petits #colibri, ils sont pas mignons ? #bot #nouvellemaman",
					    "Parti me dégourdir les ailes #bot",
					    "Prenez un peu l'air mes petits je vais faire un tour ! #bot",
					    "Maman ? Maman !! Tu es où ? #bot",
					    "J'ai trop faim, je reviens tout à l'heure #bot"]
	transitions_couve_face	["absent"]=transitions_couve_dos["absent"]
	transitions_nuit	["absent"]=transitions_nuit["couve face"]
	transitions_repas	["absent"]=["Ils ont encore faim ... Je retourne chercher un peu de nectar #bot",
					    "Prenez un peu l'air il fait si chaud #bot #tropiques"]
	transitions_fly		["absent"]=["I believe I can fly ! #bot",
					    "Décollage ! #bot"]
	
	# -> fly
	transitions_absent	["fly"]=transitions_fly["couve face"]
	transitions_couve_face	["fly"]=transitions_fly["couve face"]
	transitions_couve_dos	["fly"]=transitions_fly["couve face"]
	transitions_nuit	["fly"]=transitions_fly["couve face"]
	transitions_repas	["fly"]=transitions_fly["couve face"]

	# -> repas
	transitions_absent	["repas"]=["Miam ! Regardez ce que je vous ai ramenez ! #bot",
					   "Bon appétit mes petits #colibri #bot #atable",
					   "Goutez moi ça et prenez des forces vous en aurez besoin ... #bot",
					   "La becquée ! La becquée ! #bot #faim"]
	transitions_couve_face	["repas"]=transitions_absent["repas"]
	transitions_couve_dos	["repas"]=transitions_absent["repas"]
	transitions_nuit	["repas"]=transitions_absent["repas"]
	transitions_fly		["repas"]=transitions_absent["repas"]

	#transitions
	transitions["absent"]=transitions_absent
	transitions["nuit"]=transitions_nuit
	transitions["couve face"]=transitions_couve_face
	transitions["couve dos"]=transitions_couve_dos
	transitions["repas"]=transitions_repas
	transitions["fly"]=transitions_fly

	random.seed(datetime.now())
	#recherche dans les transitions le nouveau tweet à envoyer
	for trans_avant, trans_apres_all in transitions.iteritems():
		for trans_apres, messages in trans_apres_all.iteritems():
			if (last_status == trans_avant) and (current_status == trans_apres):
				i = random.randint(0, len(messages) - 1)  		
				elem = messages[i] 
				fichier_log.write('Nouveau twitt : %r' % elem)
				photo = open(newest,'rb')
				api.update_status_with_media(media=photo, status=elem)

#fermeture fichier de log
fichier_log.write("End script at %r\n" % time.strftime('%d/%m/%y %H:%M:%S',time.localtime()))
fichier_log.write("-------------------------\n")

