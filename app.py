import ui
import time
import threading

class LightCard(ui.View):
    def __init__(self, name, ip, on_edit_callback):
        super().__init__()
        self.name = name
        self.ip = ip
        self.on_edit_callback = on_edit_callback
        self.setup_ui()
        
    def setup_ui(self):
        self.background_color = '#ffffff'
        self.border_width = 1
        self.border_color = '#e0e0e0'
        self.corner_radius = 12
        self.frame = (0, 0, 300, 120)
        
        # Nom de la lampe
        name_label = ui.Label()
        name_label.text = self.name
        name_label.font = ('Avenir Next', 16)
        name_label.text_color = '#333333'
        name_label.frame = (16, 16, 200, 24)
        self.add_subview(name_label)
        
        # Adresse IP
        ip_label = ui.Label()
        ip_label.text = f'IP: {self.ip}'
        ip_label.font = ('Avenir Next', 12)
        ip_label.text_color = '#666666'
        ip_label.frame = (16, 40, 200, 16)
        self.add_subview(ip_label)
        
        # Interrupteur
        self.switch = ui.Switch()
        self.switch.frame = (240, 16, 51, 31)
        self.switch.action = self.toggle_light
        self.add_subview(self.switch)
        
        # Curseur de luminosité
        brightness_label = ui.Label()
        brightness_label.text = 'Luminosité'
        brightness_label.font = ('Avenir Next', 12)
        brightness_label.text_color = '#666666'
        brightness_label.frame = (16, 70, 80, 16)
        self.add_subview(brightness_label)
        
        self.brightness_slider = ui.Slider()
        self.brightness_slider.frame = (16, 88, 200, 24)
        self.brightness_slider.value = 0.5
        self.brightness_slider.action = self.brightness_changed
        self.add_subview(self.brightness_slider)
        
        self.brightness_value_label = ui.Label()
        self.brightness_value_label.text = '50%'
        self.brightness_value_label.font = ('Avenir Next', 12)
        self.brightness_value_label.text_color = '#666666'
        self.brightness_value_label.frame = (230, 88, 50, 24)
        self.brightness_value_label.alignment = ui.ALIGN_CENTER
        self.add_subview(self.brightness_value_label)
        
    def toggle_light(self, sender):
        status = "allumée" if sender.value else "éteinte"
        show_toast(f"💡 {self.name} {status}")
        
    def brightness_changed(self, sender):
        value = int(sender.value * 100)
        self.brightness_value_label.text = f'{value}%'
        show_toast(f"💡 Luminosité de {self.name}: {value}%")
        
    def touch_began(self, touch):
        if self.on_edit_callback:
            self.on_edit_callback(self)

class AddLightModal(ui.View):
    def __init__(self, on_add_callback):
        super().__init__()
        self.on_add_callback = on_add_callback
        self.setup_ui()
        
    def setup_ui(self):
        self.background_color = '#f8f8f8'
        self.corner_radius = 16
        self.frame = (0, 0, 300, 280)
        
        # Titre
        title_label = ui.Label()
        title_label.text = 'Ajouter une lampe'
        title_label.font = ('Avenir Next', 18)
        title_label.text_color = '#333333'
        title_label.frame = (20, 20, 260, 30)
        title_label.alignment = ui.ALIGN_CENTER
        self.add_subview(title_label)
        
        # Champ nom
        name_label = ui.Label()
        name_label.text = 'Nom de la lampe'
        name_label.font = ('Avenir Next', 14)
        name_label.text_color = '#666666'
        name_label.frame = (20, 70, 260, 20)
        self.add_subview(name_label)
        
        self.name_field = ui.TextField()
        self.name_field.placeholder = 'Ex: Salon'
        self.name_field.frame = (20, 95, 260, 32)
        self.name_field.border_width = 1
        self.name_field.border_color = '#cccccc'
        self.name_field.corner_radius = 8
        self.add_subview(self.name_field)
        
        # Champ IP
        ip_label = ui.Label()
        ip_label.text = 'Adresse IP'
        ip_label.font = ('Avenir Next', 14)
        ip_label.text_color = '#666666'
        ip_label.frame = (20, 140, 260, 20)
        self.add_subview(ip_label)
        
        self.ip_field = ui.TextField()
        self.ip_field.placeholder = 'Ex: 192.168.1.100'
        self.ip_field.frame = (20, 165, 260, 32)
        self.ip_field.border_width = 1
        self.ip_field.border_color = '#cccccc'
        self.ip_field.corner_radius = 8
        self.add_subview(self.ip_field)
        
        # Boutons
        cancel_btn = ui.Button()
        cancel_btn.title = 'Annuler'
        cancel_btn.frame = (20, 220, 120, 40)
        cancel_btn.background_color = '#e0e0e0'
        cancel_btn.tint_color = '#666666'
        cancel_btn.corner_radius = 8
        cancel_btn.action = self.cancel_action
        self.add_subview(cancel_btn)
        
        add_btn = ui.Button()
        add_btn.title = 'Ajouter'
        add_btn.frame = (160, 220, 120, 40)
        add_btn.background_color = '#007AFF'
        add_btn.tint_color = '#ffffff'
        add_btn.corner_radius = 8
        add_btn.action = self.add_action
        self.add_subview(add_btn)
        
    def cancel_action(self, sender):
        self.superview.remove_subview(self)
        
    def add_action(self, sender):
        name = self.name_field.text or 'Nouvelle lampe'
        ip = self.ip_field.text or '192.168.1.100'
        if self.on_add_callback:
            self.on_add_callback(name, ip)
        self.superview.remove_subview(self)

class ModernButton(ui.Button):
    def __init__(self, title, icon, color):
        super().__init__()
        self.title = f'{icon} {title}'
        self.background_color = color
        self.tint_color = '#ffffff'
        self.corner_radius = 25
        self.font = ('Avenir Next', 16)
        self.frame = (0, 0, 200, 50)

def show_toast(message):
    """Affiche un message toast en bas de l'écran"""
    def show_and_hide():
        toast = ui.Label()
        toast.text = message
        toast.background_color = '#333333'
        toast.text_color = '#ffffff'
        toast.font = ('Avenir Next', 14)
        toast.corner_radius = 8
        toast.alignment = ui.ALIGN_CENTER
        
        # Calculer la taille du texte
        text_width = len(message) * 8 + 40
        toast.frame = (ui.get_screen_size()[0]/2 - text_width/2, ui.get_screen_size()[1] - 150, text_width, 40)
        
        # Ajouter à la vue principale
        main_view = ui.get_main_view()
        if main_view:
            main_view.add_subview(toast)
            
            # Supprimer après 2 secondes
            def remove_toast():
                time.sleep(2)
                if toast.superview:
                    toast.superview.remove_subview(toast)
            
            threading.Thread(target=remove_toast).start()

class MainApp(ui.View):
    def __init__(self):
        super().__init__()
        self.lights = []
        self.setup_ui()
        
    def setup_ui(self):
        self.background_color = '#f0f0f0'
        self.frame = (0, 0, ui.get_screen_size()[0], ui.get_screen_size()[1])
        
        # Barre segmentée
        self.segmented_control = ui.SegmentedControl()
        self.segmented_control.segments = ['💡 Lumière', '🛠️ Gestion']
        self.segmented_control.selected_index = 0
        self.segmented_control.frame = (20, 60, self.frame[2] - 40, 32)
        self.segmented_control.action = self.segment_changed
        self.add_subview(self.segmented_control)
        
        # Container pour les onglets
        self.content_view = ui.View()
        self.content_view.frame = (0, 110, self.frame[2], self.frame[3] - 110)
        self.add_subview(self.content_view)
        
        # Setup des onglets
        self.setup_light_tab()
        self.setup_management_tab()
        
        # Afficher l'onglet lumière par défaut
        self.show_light_tab()
        
    def setup_light_tab(self):
        self.light_tab = ui.View()
        self.light_tab.background_color = '#f0f0f0'
        self.light_tab.frame = self.content_view.frame
        
        # ScrollView pour les cartes de lampes
        self.lights_scroll = ui.ScrollView()
        self.lights_scroll.frame = (0, 0, self.light_tab.frame[2], self.light_tab.frame[3] - 80)
        self.lights_scroll.content_size = (self.light_tab.frame[2], 0)
        self.light_tab.add_subview(self.lights_scroll)
        
        # Bouton + pour ajouter une lampe
        add_button = ui.Button()
        add_button.title = '+'
        add_button.background_color = '#007AFF'
        add_button.tint_color = '#ffffff'
        add_button.corner_radius = 30
        add_button.font = ('Avenir Next', 24)
        add_button.frame = (self.light_tab.frame[2]/2 - 30, self.light_tab.frame[3] - 80, 60, 60)
        add_button.action = self.show_add_light_modal
        self.light_tab.add_subview(add_button)
        
    def setup_management_tab(self):
        self.management_tab = ui.View()
        self.management_tab.background_color = '#f0f0f0'
        self.management_tab.frame = self.content_view.frame
        
        # Bouton VPN
        vpn_button = ModernButton('VPN', '🔒', '#34C759')
        vpn_button.frame = (self.management_tab.frame[2]/2 - 100, 100, 200, 50)
        vpn_button.action = self.vpn_action
        self.management_tab.add_subview(vpn_button)
        
        # Bouton Adblock
        adblock_button = ModernButton('Adblock', '🚫', '#FF3B30')
        adblock_button.frame = (self.management_tab.frame[2]/2 - 100, 180, 200, 50)
        adblock_button.action = self.adblock_action
        self.management_tab.add_subview(adblock_button)
        
    def segment_changed(self, sender):
        if sender.selected_index == 0:
            self.show_light_tab()
        else:
            self.show_management_tab()
            
    def show_light_tab(self):
        self.content_view.remove_subview(self.management_tab)
        self.content_view.add_subview(self.light_tab)
        
    def show_management_tab(self):
        self.content_view.remove_subview(self.light_tab)
        self.content_view.add_subview(self.management_tab)
        
    def show_add_light_modal(self, sender):
        modal = AddLightModal(self.add_light)
        
        # Créer un overlay semi-transparent
        overlay = ui.View()
        overlay.background_color = '#000000'
        overlay.alpha = 0.5
        overlay.frame = self.frame
        self.add_subview(overlay)
        
        # Centrer la modal
        modal.frame = (
            self.frame[2]/2 - 150,
            self.frame[3]/2 - 140,
            300,
            280
        )
        self.add_subview(modal)
        
        # Supprimer l'overlay quand la modal se ferme
        original_remove = modal.superview.remove_subview
        def new_remove(view):
            if view == modal:
                self.remove_subview(overlay)
            original_remove(view)
        modal.superview.remove_subview = new_remove
        
    def add_light(self, name, ip):
        light_card = LightCard(name, ip, self.edit_light)
        
        # Positionner la carte
        y_position = len(self.lights) * 140 + 20
        light_card.frame = (20, y_position, self.light_tab.frame[2] - 40, 120)
        
        self.lights.append(light_card)
        self.lights_scroll.add_subview(light_card)
        
        # Mettre à jour la taille du contenu du scroll
        self.lights_scroll.content_size = (
            self.light_tab.frame[2],
            len(self.lights) * 140 + 40
        )
        
        show_toast(f"💡 {name} ajoutée")
        
    def edit_light(self, light_card):
        show_toast(f"✏️ Modification de {light_card.name}")
        
    def vpn_action(self, sender):
        show_toast("🔒 VPN activé")
        
    def adblock_action(self, sender):
        show_toast("🚫 Publicités bloquées")

if __name__ == '__main__':
    app = MainApp()
    app.present('fullscreen')