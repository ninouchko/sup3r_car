#!/usr/bin/env micropython
# coding: utf-8

# Import the EV3-robot library
from ev3dev2.motor import MediumMotor, LargeMotor
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.button import Button
from ev3dev2.led import Leds 
from ev3dev2.sound import Sound
# Import time
from time import sleep

# Appels des autres classes
from motorization import Motorization
from direction import Direction



class Car:
    """
    Une classe représentant notre voiture suiveuse de ligne.
    """
    # Constructor
    def __init__(self, name = ''):
        self.name = name
        self.btn = Button()
        self.leds = Leds()
        self.sound = Sound()
        self.voice_options = '-a 200 -s 100 -v fr+f2' # voir https://sites.google.com/site/ev3devpython/learn_ev3_python/sound 
        # Capteur de couleur
        self.cs = ColorSensor()
        self.light = None               # Initialisation de la partie claire à None
        self.dark = None                # Initialisation de la partie foncée à None
        # motorization
        self.motorization = Motorization()
        
        # direction
        self.direction = Direction()
        
    def set_name(self, name):
        """
        Set the name of the follower
        """
        self.name = name

    def get_threshold(self):
        """
        Retourne la valeur de consigne, None si non calculable
        """
        if self.light and self.dark:
            return (self.light+self.dark)//2

    def speak(self, message, display = True):
        """
        Speak the message.
        if display is True, print the message
        """
        if display:
            print(message)
        self.sound.speak(message, espeak_opts = self.voice_options)

    ###############################################
    #
    #  PARTIE CALIBRATION DU CAPTEUR
    #
    ###############################################
    def calibrate(self):
        """
        Launch the calibration of the color sensor
        """

        def calibrate_light(state):
            if state:
                self._calibrate_zone(1)

        def calibrate_dark(state):
            if state:
                self._calibrate_zone(0)

        self.cs.MODE_REFLECT = 'REFLECT'

        self.leds.all_off()
        self.speak("Calibration du capteur de couleur.")
        self.leds.set_color('LEFT', 'GREEN')
        print("Mettez le capteur de couleur sur la partie claire et appuyez sur le bouton gauche pour démarrer.")
        self.light = None
        while self.light == None:
            self.btn.on_left = calibrate_light
            self.btn.process()
            sleep(0.01)
        print("Mettez le capteur de couleur sur la partie foncée et appuyez sur le bouton gauche pour demarrer.")
        self.dark = None
        while self.dark == None:
            self.btn.on_left = calibrate_dark
            self.btn.process()
            sleep(0.01)
        if self.name:
            self.speak("Calibration de " + self.name + " terminée")
        else:
            self.speak("Calibration terminée")
        self.speak("La valeur de consigne est "+str(self.get_threshold()))
















    ###############################################
    #
    #  NE PAS UTILISER CES FONCTIONS
    #
    ###############################################


    def _calibrate_zone(self, zone):
        """
        Calibration de la zone.
        zone : 1 pour la partie claire, 0 pour la partie foncée
        """
        self.leds.all_off()
        measures = []
        for i in range(5):
            self.leds.set_color('RIGHT', 'GREEN')
            sleep(0.2)
            measure = self.cs.reflected_light_intensity
            print(measure)
            measures.append(measure)
            self.leds.set_color('RIGHT', 'BLACK')
            sleep(0.2)
        # calcul de la moyenne des mesures
        average = int(sum(measures)/len(measures))
        # Partie claire
        if zone == 1:
            self.light = average
            message = "Partie claire : "+str(self.light)
        # Partie foncée
        elif zone == 0:
            self.dark = average
            message = "Partie foncée : "+str(self.dark)
        self.speak(message)
