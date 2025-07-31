#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal SSH pour Raspberry Pi 5 - Compatible Pythonista 3 (Version Corrigée)
Auteur: Assistant IA
Description: Interface terminal SSH avec UI native Pythonista - Anti-crash
"""

import ui
import console
import threading
import time
import socket
import sys
import os
import queue

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
        self.output_queue = queue.Queue()
        self.command_history = []
        self.history_index = 0
        self.running = True
        
        # Paramètres de connexion par défaut
        self.hostname = "raspberrypi.local"
        self.port = 22
        self.username = "tom"
        self.password = ""
        
        self.setup_ui()
        self.start_ui_updater()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Vue principale
        self.view = ui.View()
        self.view.name = 'Terminal SSH - Raspberry Pi'
        self.view.background_color = '#1e1e1e'
        self.view.frame = (0, 0, 400, 600)
        self.view.will_close = self.will_close
        
        # Barre de connexion
        connection_view = ui.View()
        connection_view.frame = (0, 0, 400, 120)
        connection_view.background_color = '#2d2d2d'
        
        # Champs de connexion avec meilleure visibilité
        ui.Label(frame=(10, 10, 80, 32), text='Host:', text_color='#FFFFFF', 
                font=('Helvetica-Bold', 14), parent=connection_view)
        self.host_field = ui.TextField(frame=(100, 10, 200, 32), text=self.hostname, 
                                      background_color='#5d5d5d', text_color='#FFFFFF', 
                                      placeholder='raspberrypi.local', border_width=2, 
                                      border_color='#888888', corner_radius=4)
        connection_view.add_subview(self.host_field)
        
        ui.Label(frame=(10, 50, 80, 32), text='User:', text_color='#FFFFFF', 
                font=('Helvetica-Bold', 14), parent=connection_view)
        self.user_field = ui.TextField(frame=(100, 50, 100, 32), text=self.username,
                                      background_color='#5d5d5d', text_color='#FFFFFF',
                                      placeholder='tom', border_width=2, 
                                      border_color='#888888', corner_radius=4)
        connection_view.add_subview(self.user_field)
        
        ui.Label(frame=(210, 50, 80, 32), text='Pass:', text_color='#FFFFFF', 
                font=('Helvetica-Bold', 14), parent=connection_view)
        self.pass_field = ui.TextField(frame=(290, 50, 100, 32), secure=True,
                                      background_color='#5d5d5d', text_color='#FFFFFF',
                                      placeholder='password', border_width=2, 
                                      border_color='#888888', corner_radius=4)
        connection_view.add_subview(self.pass_field)
        
        # Status label
        self.status_label = ui.Label(frame=(10, 85, 300, 25), text='Prêt à se connecter', 
                                    text_color='#00FF00', font=('Helvetica', 12))
        connection_view.add_subview(self.status_label)
        
        # Bouton de connexion
        self.connect_btn = ui.Button(frame=(310, 10, 80, 72), title='Connect')
        self.connect_btn.background_color = '#007AFF'
        self.connect_btn.action = self.toggle_connection
        self.connect_btn.corner_radius = 8
        connection_view.add_subview(self.connect_btn)
        
        self.view.add_subview(connection_view)
        
        # Zone d'affichage du terminal
        self.terminal_view = ui.TextView()
        self.terminal_view.frame = (0, 120, 400, 380)
        self.terminal_view.background_color = '#000000'
        self.terminal_view.text_color = '#00ff00'
        self.terminal_view.font = ('Courier', 11)
        self.terminal_view.editable = False
        self.terminal_view.text = "=== Terminal SSH - Raspberry Pi ===\nPrêt à se connecter...\n\n"
        self.view.add_subview(self.terminal_view)
        
        # Zone de saisie des commandes
        command_view = ui.View()
        command_view.frame = (0, 500, 400, 100)
        command_view.background_color = '#2d2d2d'
        
        # Prompt
        ui.Label(frame=(10, 10, 30, 32), text='$', text_color='#00ff00', 
                font=('Courier-Bold', 16), parent=command_view)
        
        # Champ de commande
        self.command_field = ui.TextField()
        self.command_field.frame = (40, 10, 250, 32)
        self.command_field.background_color = '#000000'
        self.command_field.text_color = '#00ff00'
        self.command_field.font = ('Courier', 12)
        self.command_field.delegate = self
        self.command_field.border_width = 1
        self.command_field.border_color = '#444444'
        self.command_field.corner_radius = 4
        command_view.add_subview(self.command_field)
        
        # Bouton d'envoi
        send_btn = ui.Button(frame=(300, 10, 90, 32), title='Send')
        send_btn.background_color = '#007AFF'
        send_btn.action = self.send_command
        send_btn.corner_radius = 4
        command_view.add_subview(send_btn)
        
        # Boutons de contrôle
        clear_btn = ui.Button(frame=(10, 50, 80, 30), title='Clear')
        clear_btn.background_color = '#FF3B30'
        clear_btn.action = self.clear_terminal
        clear_btn.corner_radius = 4
        command_view.add_subview(clear_btn)
        
        history_btn = ui.Button(frame=(100, 50, 80, 30), title='History')
        history_btn.background_color = '#FF9500'
        history_btn.action = self.show_history
        history_btn.corner_radius = 4
        command_view.add_subview(history_btn)
        
        disconnect_btn = ui.Button(frame=(190, 50, 100, 30), title='Force Close')
        disconnect_btn.background_color = '#8E8E93'
        disconnect_btn.action = self.force_disconnect
        disconnect_btn.corner_radius = 4
        command_view.add_subview(disconnect_btn)
        
        self.view.add_subview(command_view)
    
    def start_ui_updater(self):
        """Démarrer le thread de mise à jour de l'UI"""
        def ui_updater():
            while self.running:
                try:
                    # Traiter les messages en attente
                    while not self.output_queue.empty():
                        try:
                            message = self.output_queue.get_nowait()
                            self.update_terminal_safe(message)
                        except queue.Empty:
                            break
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Erreur UI updater: {e}")
                    
        threading.Thread(target=ui_updater, daemon=True).start()
    
    def update_terminal_safe(self, text):
        """Mise à jour sécurisée du terminal"""
        try:
            current_text = self.terminal_view.text or ""
            new_text = current_text + text
            
            # Limiter la taille du buffer (garder les 1000 dernières lignes)
            lines = new_text.split('\n')
            if len(lines) > 1000:
                lines = lines[-1000:]
                new_text = '\n'.join(lines)
            
            self.terminal_view.text = new_text
            
            # Auto-scroll vers le bas
            content_height = self.terminal_view.content_size[1]
            frame_height = self.terminal_view.frame[3]
            if content_height > frame_height:
                self.terminal_view.content_offset = (0, content_height - frame_height)
                
        except Exception as e:
            print(f"Erreur update terminal: {e}")
    
    def add_output(self, text):
        """Ajouter du texte au terminal via la queue"""
        try:
            self.output_queue.put(text)
        except Exception as e:
            print(f"Erreur add_output: {e}")
    
    def update_status(self, status, color='#00FF00'):
        """Mettre à jour le status"""
        try:
            self.status_label.text = status
            self.status_label.text_color = color
        except:
            pass
    
    def textfield_should_return(self, textfield):
        """Gestion de la touche Entrée dans le champ de commande"""
        if textfield == self.command_field:
            self.send_command(None)
            return False
        return True
    
    def toggle_connection(self, sender):
        """Basculer la connexion SSH"""
        if not PARAMIKO_AVAILABLE:
            self.add_output("❌ Erreur: Paramiko non installé.\n")
            self.add_output("💡 Installation: pip.main(['install', 'paramiko'])\n\n")
            return
            
        if not self.connected:
            self.connect_ssh()
        else:
            self.disconnect_ssh()
    
    def connect_ssh(self):
        """Établir la connexion SSH"""
        self.hostname = self.host_field.text.strip() or "raspberrypi.local"
        self.username = self.user_field.text.strip() or "tom"
        self.password = self.pass_field.text
        
        if not self.password:
            self.add_output("❌ Erreur: Mot de passe requis\n\n")
            self.update_status("Mot de passe requis", '#FF3B30')
            return
        
        self.add_output(f"🔄 Connexion à {self.username}@{self.hostname}...\n")
        self.update_status("Connexion en cours...", '#FF9500')
        
        # Désactiver le bouton pendant la connexion
        self.connect_btn.enabled = False
        
        # Connexion en thread séparé
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        """Thread de connexion SSH avec gestion d'erreurs robuste"""
        try:
            self.add_output("📡 Initialisation du client SSH...\n")
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.add_output(f"🔐 Tentative de connexion à {self.hostname}:{self.port}...\n")
            
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=15,
                banner_timeout=30
            )
            
            self.add_output("✅ Authentification réussie!\n")
            self.add_output("🚀 Création du shell interactif...\n")
            
            # Créer un canal shell interactif
            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm', width=80, height=24)
            self.ssh_channel.settimeout(0.5)
            
            self.connected = True
            
            # Mettre à jour l'UI de manière sécurisée
            self.update_connection_ui(True)
            
            self.add_output(f"🎉 Connecté à {self.hostname} avec succès!\n")
            self.add_output("💬 Tapez vos commandes ci-dessous.\n")
            self.add_output("="*50 + "\n\n")
            
            self.update_status(f"Connecté à {self.hostname}", '#00FF00')
            
            # Démarrer la lecture des données du serveur
            threading.Thread(target=self._read_ssh_output, daemon=True).start()
            
        except paramiko.AuthenticationException:
            self.add_output("❌ Erreur d'authentification: Vérifiez nom d'utilisateur/mot de passe\n\n")
            self.update_status("Erreur d'authentification", '#FF3B30')
        except paramiko.SSHException as e:
            self.add_output(f"❌ Erreur SSH: {str(e)}\n\n")
            self.update_status("Erreur SSH", '#FF3B30')
        except socket.timeout:
            self.add_output("❌ Timeout: Vérifiez l'adresse IP/réseau\n\n")
            self.update_status("Timeout de connexion", '#FF3B30')
        except Exception as e:
            self.add_output(f"❌ Erreur de connexion: {str(e)}\n\n")
            self.update_status("Erreur de connexion", '#FF3B30')
        finally:
            # Réactiver le bouton
            self.connect_btn.enabled = True
            if not self.connected:
                self.update_connection_ui(False)
    
    def update_connection_ui(self, connected):
        """Mettre à jour l'interface selon l'état de connexion"""
        try:
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
        except Exception as e:
            print(f"Erreur update_connection_ui: {e}")
    
    def _read_ssh_output(self):
        """Lire en continu la sortie du serveur SSH"""
        buffer = ""
        while self.connected and self.ssh_channel:
            try:
                if self.ssh_channel.recv_ready():
                    data = self.ssh_channel.recv(4096)
                    if data:
                        text = data.decode('utf-8', errors='replace')
                        buffer += text
                        
                        # Traiter les données par lignes complètes
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            self.add_output(line + '\n')
                        
                        # Ajouter le reste du buffer s'il n'est pas vide
                        if buffer and len(buffer) > 100:  # Éviter l'accumulation
                            self.add_output(buffer)
                            buffer = ""
                            
                time.sleep(0.05)  # Réduire la charge CPU
                
            except socket.timeout:
                continue  # Normal, pas de données disponibles
            except Exception as e:
                if self.connected:  # Éviter les erreurs lors de la déconnexion
                    self.add_output(f"\n❌ Erreur de lecture: {str(e)}\n")
                    self.update_status("Erreur de lecture", '#FF3B30')
                break
        
        # Ajouter le buffer restant
        if buffer:
            self.add_output(buffer)
    
    def disconnect_ssh(self):
        """Fermer la connexion SSH"""
        self.connected = False
        
        try:
            if self.ssh_channel:
                self.ssh_channel.close()
                self.ssh_channel = None
            
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
        except:
            pass  # Ignorer les erreurs de fermeture
        
        self.update_connection_ui(False)
        self.add_output("\n🔌 Connexion fermée.\n\n")
        self.update_status("Déconnecté", '#8E8E93')
    
    def force_disconnect(self, sender):
        """Forcer la déconnexion en cas de problème"""
        self.disconnect_ssh()
        self.add_output("🔧 Déconnexion forcée effectuée.\n\n")
    
    def send_command(self, sender):
        """Envoyer une commande au serveur SSH"""
        command = self.command_field.text.strip()
        if not command:
            return
        
        if not self.connected or not self.ssh_channel:
            self.add_output("❌ Erreur: Non connecté au serveur\n")
            return
        
        try:
            # Ajouter la commande à l'historique
            if command not in self.command_history:
                self.command_history.append(command)
                if len(self.command_history) > 50:  # Limiter l'historique
                    self.command_history = self.command_history[-50:]
            self.history_index = len(self.command_history)
            
            # Envoyer la commande
            self.ssh_channel.send(command + '\n')
            
            # Vider le champ de saisie
            self.command_field.text = ""
            
        except Exception as e:
            self.add_output(f"❌ Erreur d'envoi: {str(e)}\n")
    
    def clear_terminal(self, sender):
        """Vider l'affichage du terminal"""
        self.terminal_view.text = "=== Terminal SSH - Raspberry Pi ===\n"
        if self.connected:
            self.terminal_view.text += f"Connecté à {self.hostname}\n\n"
        else:
            self.terminal_view.text += "Prêt à se connecter...\n\n"
    
    def show_history(self, sender):
        """Afficher l'historique des commandes"""
        if not self.command_history:
            self.add_output("📝 Aucun historique de commandes\n\n")
            return
        
        self.add_output("\n📋 === Historique des commandes ===\n")
        for i, cmd in enumerate(self.command_history[-10:], 1):  # 10 dernières commandes
            self.add_output(f"  {i}. {cmd}\n")
        self.add_output("=====================================\n\n")
    
    def present(self):
        """Afficher l'interface"""
        self.view.present('fullscreen')
    
    def will_close(self):
        """Nettoyage avant fermeture"""
        self.running = False
        if self.connected:
            self.disconnect_ssh()
        # Petit délai pour laisser les threads se terminer
        time.sleep(0.5)

def main():
    """Fonction principale"""
    # Vérifier la disponibilité de paramiko
    if not PARAMIKO_AVAILABLE:
        print("⚠️  Installation de paramiko requise:")
        print("import pip")
        print("pip.main(['install', 'paramiko'])")
        
        # Proposer l'installation automatique
        try:
            response = console.alert("Paramiko manquant", 
                                   "Voulez-vous installer paramiko maintenant?", 
                                   "Installer", "Annuler")
            if response == 1:
                try:
                    import pip
                    pip.main(['install', 'paramiko'])
                    console.alert("Installation", "Paramiko installé! Redémarrez l'application.")
                    return
                except Exception as e:
                    console.alert("Erreur", f"Impossible d'installer paramiko: {e}")
                    return
        except:
            pass
    
    # Créer et lancer l'application
    try:
        terminal = SSHTerminal()
        terminal.present()
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        console.alert("Erreur", f"Impossible de lancer l'application: {e}")

if __name__ == '__main__':
    main()