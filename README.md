# Terminal SSH pour Raspberry Pi 5 - Pythonista 3

## Description
Application de terminal SSH avec interface utilisateur native pour Pythonista 3, permettant de se connecter et d'interagir avec un Raspberry Pi 5 via SSH.

## Fonctionnalités
- ✅ Interface utilisateur native Pythonista 3
- ✅ Connexion SSH sécurisée
- ✅ Terminal interactif en temps réel
- ✅ Historique des commandes
- ✅ Gestion des sessions SSH
- ✅ Interface sombre optimisée pour mobile

## Prérequis

### Installation des dépendances
Dans Pythonista 3, exécutez le code suivant pour installer les dépendances :

```python
import pip
pip.main(['install', 'paramiko'])
```

Ou alternativement :
```python
import subprocess
import sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'paramiko'])
```

## Configuration du Raspberry Pi 5

### 1. Activer SSH sur le Raspberry Pi
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### 2. Configuration réseau (optionnel)
Pour une connexion plus stable, configurez une IP statique sur votre Raspberry Pi :

```bash
sudo nano /etc/dhcpcd.conf
```

Ajoutez :
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

## Utilisation

### 1. Lancement de l'application
```python
python ssh_terminal_pythonista.py
```

### 2. Connexion
1. **Host** : Entrez l'adresse IP ou le nom d'hôte de votre Raspberry Pi
   - Par défaut : `raspberrypi.local`
   - Exemple IP : `192.168.1.100`

2. **User** : Nom d'utilisateur SSH
   - Par défaut : `pi`

3. **Pass** : Mot de passe de l'utilisateur

4. Appuyez sur **Connect**

### 3. Utilisation du terminal
- Tapez vos commandes dans le champ de saisie en bas
- Appuyez sur **Send** ou **Entrée** pour exécuter
- Utilisez **Clear** pour vider l'affichage
- **History** affiche les dernières commandes

## Interface

### Zone de connexion (haut)
- Champs de saisie pour host, utilisateur et mot de passe
- Bouton Connect/Disconnect

### Zone terminal (centre)
- Affichage des commandes et résultats
- Couleurs de terminal classiques (fond noir, texte vert)
- Défilement automatique

### Zone de commande (bas)
- Champ de saisie avec prompt `$`
- Boutons Send, Clear, History

## Commandes utiles sur Raspberry Pi

### Système
```bash
# Informations système
uname -a
cat /proc/cpuinfo
free -h
df -h

# Processus
top
ps aux

# Réseau
ifconfig
ip addr show
```

### GPIO (spécifique Raspberry Pi)
```bash
# Installer wiringPi si nécessaire
sudo apt update
sudo apt install wiringpi

# État des GPIO
gpio readall
```

### Services
```bash
# État des services
sudo systemctl status ssh
sudo systemctl status networking

# Redémarrage
sudo reboot
sudo shutdown -h now
```

## Dépannage

### Problème de connexion
1. Vérifiez que SSH est activé sur le Raspberry Pi
2. Testez la connexion réseau : `ping raspberrypi.local`
3. Vérifiez les identifiants utilisateur/mot de passe
4. Essayez avec l'adresse IP directe au lieu du nom d'hôte

### Erreur "Paramiko non disponible"
```python
# Dans Pythonista 3
import pip
pip.main(['install', 'paramiko'])
```

### Problèmes d'affichage
- L'application est optimisée pour iPhone/iPad en mode portrait
- Si l'affichage est tronqué, redémarrez l'application

## Sécurité

⚠️ **Important** :
- Ne stockez jamais vos mots de passe en dur dans le code
- Utilisez des clés SSH plutôt que des mots de passe pour plus de sécurité
- Changez les mots de passe par défaut du Raspberry Pi

### Configuration avec clés SSH (recommandé)
```bash
# Sur votre machine de développement
ssh-keygen -t rsa -b 4096
ssh-copy-id pi@raspberrypi.local
```

## Limitations
- Pas de support des clés SSH dans cette version (authentification par mot de passe uniquement)
- Pas de transfert de fichiers intégré
- Terminal basique sans support complet des séquences d'échappement

## Développement

### Structure du code
- `SSHTerminal` : Classe principale avec interface UI
- `setup_ui()` : Configuration de l'interface
- `connect_ssh()` : Gestion de la connexion SSH
- `send_command()` : Envoi des commandes
- Threading pour éviter le blocage de l'UI

### Personnalisation
Vous pouvez modifier :
- Les couleurs dans `setup_ui()`
- La taille de la fenêtre
- Les paramètres de connexion par défaut
- L'historique des commandes

## Licence
Script libre d'utilisation et de modification.

## Support
Pour des questions spécifiques à Pythonista 3, consultez la documentation officielle : https://omz-software.com/pythonista/