#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal SSH pour Raspberry Pi 5 - Compatible Pythonista 3
Auteur: Assistant IA
Description: Interface terminal SSH avec UI native Pythonista
"""

import ui
import console
import threading
import time
import socket
import sys
import os

# Tentative d'import de paramiko (si disponible)
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    print("Paramiko non disponible. Installation requise.")

class SSHTerminal:
    def __init__(self):
        self.ssh_client = None
        self.ssh_channel = None
        self.connected = False
        self.output_buffer = []
        self.command_history = []
        self.history_index = 0
        
        # Paramètres de connexion par défaut
        self.hostname = "raspberrypi.local"
        self.port = 22
        self.username = "pi"
        self.password = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Vue principale
        self.view = ui.View()
        self.view.name = 'Terminal SSH - Raspberry Pi'
        self.view.background_color = '#1e1e1e'
        self.view.frame = (0, 0, 400, 600)
        
        # Barre de connexion
        connection_view = ui.View()
        connection_view.frame = (0, 0, 400, 120)
        connection_view.background_color = '#2d2d2d'
        
        # Champs de connexion
        ui.Label(frame=(10, 10, 80, 32), text='Host:', text_color='white', parent=connection_view)
        self.host_field = ui.TextField(frame=(100, 10, 200, 32), text=self.hostname, 
                                      background_color='#3d3d3d', text_color='white')
        connection_view.add_subview(self.host_field)
        
        ui.Label(frame=(10, 50, 80, 32), text='User:', text_color='white', parent=connection_view)
        self.user_field = ui.TextField(frame=(100, 50, 100, 32), text=self.username,
                                      background_color='#3d3d3d', text_color='white')
        connection_view.add_subview(self.user_field)
        
        ui.Label(frame=(210, 50, 80, 32), text='Pass:', text_color='white', parent=connection_view)
        self.pass_field = ui.TextField(frame=(250, 50, 100, 32), secure=True,
                                      background_color='#3d3d3d', text_color='white')
        connection_view.add_subview(self.pass_field)
        
        # Bouton de connexion
        self.connect_btn = ui.Button(frame=(310, 10, 80, 72), title='Connect')
        self.connect_btn.background_color = '#007AFF'
        self.connect_btn.action = self.toggle_connection
        connection_view.add_subview(self.connect_btn)
        
        self.view.add_subview(connection_view)
        
        # Zone d'affichage du terminal
        self.terminal_view = ui.TextView()
        self.terminal_view.frame = (0, 120, 400, 400)
        self.terminal_view.background_color = '#000000'
        self.terminal_view.text_color = '#00ff00'
        self.terminal_view.font = ('Courier', 12)
        self.terminal_view.editable = False
        self.terminal_view.text = "Terminal SSH - Prêt à se connecter\n"
        self.view.add_subview(self.terminal_view)
        
        # Zone de saisie des commandes
        command_view = ui.View()
        command_view.frame = (0, 520, 400, 80)
        command_view.background_color = '#2d2d2d'
        
        ui.Label(frame=(10, 10, 30, 32), text='$', text_color='#00ff00', 
                font=('Courier', 14), parent=command_view)
        
        self.command_field = ui.TextField()
        self.command_field.frame = (40, 10, 270, 32)
        self.command_field.background_color = '#000000'
        self.command_field.text_color = '#00ff00'
        self.command_field.font = ('Courier', 12)
        self.command_field.delegate = self
        command_view.add_subview(self.command_field)
        
        # Bouton d'envoi
        send_btn = ui.Button(frame=(320, 10, 70, 32), title='Send')
        send_btn.background_color = '#007AFF'
        send_btn.action = self.send_command
        command_view.add_subview(send_btn)
        
        # Boutons de contrôle
        clear_btn = ui.Button(frame=(10, 45, 70, 25), title='Clear')
        clear_btn.background_color = '#FF3B30'
        clear_btn.action = self.clear_terminal
        command_view.add_subview(clear_btn)
        
        history_btn = ui.Button(frame=(90, 45, 70, 25), title='History')
        history_btn.background_color = '#FF9500'
        history_btn.action = self.show_history
        command_view.add_subview(history_btn)
        
        self.view.add_subview(command_view)
    
    def textfield_should_return(self, textfield):
        """Gestion de la touche Entrée dans le champ de commande"""
        if textfield == self.command_field:
            self.send_command(None)
            return False
        return True
    
    def toggle_connection(self, sender):
        """Basculer la connexion SSH"""
        if not PARAMIKO_AVAILABLE:
            self.add_output("Erreur: Paramiko non installé. Installez-le via pip.\n")
            return
            
        if not self.connected:
            self.connect_ssh()
        else:
            self.disconnect_ssh()
    
    def connect_ssh(self):
        """Établir la connexion SSH"""
        self.hostname = self.host_field.text or "raspberrypi.local"
        self.username = self.user_field.text or "pi"
        self.password = self.pass_field.text
        
        if not self.password:
            self.add_output("Erreur: Mot de passe requis\n")
            return
        
        self.add_output(f"Connexion à {self.username}@{self.hostname}...\n")
        
        # Connexion en thread séparé pour éviter le blocage de l'UI
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        """Thread de connexion SSH"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            
            # Créer un canal shell interactif
            self.ssh_channel = self.ssh_client.invoke_shell()
            self.ssh_channel.settimeout(0.1)
            
            self.connected = True
            
            # Mettre à jour l'UI sur le thread principal
            ui.delay(lambda: self._update_connection_ui(True), 0)
            
            self.add_output(f"Connecté à {self.hostname} avec succès!\n")
            self.add_output("Tapez vos commandes ci-dessous.\n\n")
            
            # Démarrer la lecture des données du serveur
            threading.Thread(target=self._read_ssh_output, daemon=True).start()
            
        except Exception as e:
            self.add_output(f"Erreur de connexion: {str(e)}\n")
            ui.delay(lambda: self._update_connection_ui(False), 0)
    
    def _update_connection_ui(self, connected):
        """Mettre à jour l'interface selon l'état de connexion"""
        if connected:
            self.connect_btn.title = 'Disconnect'
            self.connect_btn.background_color = '#FF3B30'
            self.host_field.enabled = False
            self.user_field.enabled = False
            self.pass_field.enabled = False
        else:
            self.connect_btn.title = 'Connect'
            self.connect_btn.background_color = '#007AFF'
            self.host_field.enabled = True
            self.user_field.enabled = True
            self.pass_field.enabled = True
    
    def _read_ssh_output(self):
        """Lire en continu la sortie du serveur SSH"""
        while self.connected and self.ssh_channel:
            try:
                if self.ssh_channel.recv_ready():
                    data = self.ssh_channel.recv(1024).decode('utf-8', errors='ignore')
                    if data:
                        self.add_output(data)
                time.sleep(0.1)
            except Exception as e:
                if self.connected:  # Éviter les erreurs lors de la déconnexion
                    self.add_output(f"Erreur de lecture: {str(e)}\n")
                break
    
    def disconnect_ssh(self):
        """Fermer la connexion SSH"""
        self.connected = False
        
        if self.ssh_channel:
            self.ssh_channel.close()
            self.ssh_channel = None
        
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        
        self._update_connection_ui(False)
        self.add_output("Connexion fermée.\n")
    
    def send_command(self, sender):
        """Envoyer une commande au serveur SSH"""
        command = self.command_field.text.strip()
        if not command:
            return
        
        if not self.connected or not self.ssh_channel:
            self.add_output("Erreur: Non connecté au serveur\n")
            return
        
        try:
            # Ajouter la commande à l'historique
            if command not in self.command_history:
                self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # Afficher la commande dans le terminal
            self.add_output(f"$ {command}\n")
            
            # Envoyer la commande
            self.ssh_channel.send(command + '\n')
            
            # Vider le champ de saisie
            self.command_field.text = ""
            
        except Exception as e:
            self.add_output(f"Erreur d'envoi: {str(e)}\n")
    
    def add_output(self, text):
        """Ajouter du texte au terminal"""
        def update_ui():
            current_text = self.terminal_view.text
            self.terminal_view.text = current_text + text
            # Faire défiler vers le bas
            self.terminal_view.content_offset = (0, max(0, self.terminal_view.content_size[1] - self.terminal_view.frame[3]))
        
        if threading.current_thread() != threading.main_thread():
            ui.delay(update_ui, 0)
        else:
            update_ui()
    
    def clear_terminal(self, sender):
        """Vider l'affichage du terminal"""
        self.terminal_view.text = ""
    
    def show_history(self, sender):
        """Afficher l'historique des commandes"""
        if not self.command_history:
            self.add_output("Aucun historique de commandes\n")
            return
        
        self.add_output("\n=== Historique des commandes ===\n")
        for i, cmd in enumerate(self.command_history[-10:], 1):  # 10 dernières commandes
            self.add_output(f"{i}. {cmd}\n")
        self.add_output("================================\n\n")
    
    def present(self):
        """Afficher l'interface"""
        self.view.present('fullscreen')
    
    def will_close(self):
        """Nettoyage avant fermeture"""
        if self.connected:
            self.disconnect_ssh()

def main():
    """Fonction principale"""
    # Vérifier la disponibilité de paramiko
    if not PARAMIKO_AVAILABLE:
        print("Installation de paramiko requise:")
        print("pip install paramiko")
        print("\nOu dans Pythonista:")
        print("import pip")
        print("pip.main(['install', 'paramiko'])")
        
        # Proposer l'installation automatique
        try:
            import pip
            response = console.alert("Paramiko manquant", 
                                   "Voulez-vous installer paramiko maintenant?", 
                                   "Installer", "Annuler")
            if response == 1:
                pip.main(['install', 'paramiko'])
                console.alert("Installation", "Redémarrez l'application après installation")
                return
        except:
            pass
    
    # Créer et lancer l'application
    terminal = SSHTerminal()
    terminal.present()

if __name__ == '__main__':
    main()