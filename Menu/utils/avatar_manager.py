from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.tools import get_screen_size, apply_circular_mask
import json
import pygame

# Classe pour la gestion de l'avatar
class AvatarManager:
    
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = get_screen_size()
        self.avatar_size = 100
        with open("data/player_data.json") as f:
            self.player_data = json.load(f)
        self.input_text = self.player_data["pseudo"]
        
        # Charger ou créer l'avatar
        self.avatar_path = "assets/avatar.bmp"
        try:
            self.avatar_original = pygame.image.load(self.avatar_path).convert_alpha()
            self.avatar_original = pygame.transform.scale(self.avatar_original, (100, 100))
        except:
            # Créer un avatar par défaut
            self.avatar_original = pygame.Surface((100, 100), pygame.SRCALPHA)
            self.avatar_original.fill((100, 100, 255, 255))  # Bleu par défaut
            pygame.draw.circle(self.avatar_original, ORANGE, (50, 50), 50)
            
        self.avatar = self.avatar_original.copy()
        
        # Historique des modifications
        self.history = [self.avatar.copy()]
        self.redo_stack = []
        
        # Positions
        self.avatar_start_pos = (self.W - self.avatar_size - 25, 20)
        self.pseudo_start_pos = (self.W - self.avatar_size - 35, self.avatar_size + 30)
        
        # Positions cibles pour l'édition
        self.avatar_target_size = int(0.71 * self.H)
        self.avatar_target_pos = ((self.W - self.avatar_target_size) // 2, (self.H - self.avatar_target_size) // 2-70)
        self.pseudo_target_pos = (self.W // 2 - 50, self.avatar_target_pos[1] + self.avatar_target_size + 25)
        self.avatar_target_size_ratio=self.avatar_target_size/self.avatar.get_size()[0]
        
        # État d'animation
        self.anim_progress = 0
        self.is_expanding = False
        self.is_retracting = False
        self.pseudo_editable = False
        self.show_buttons = False
        
        # Propriétés du pinceau
        self.drawing = False
        self.brush_size = 5
        self.size_min = 5
        self.size_max = 40
        
        self.colors = [ (255, 255, 255), (0, 0, 0)]
        # Palette de couleurs pour l'édition d'avatar

        self.brush_color = self.colors[0]

        # Bordure d'avatar

        with open("data/shop_items.json") as f:
            self.shop_item = json.load(f)

        for i in range(len(self.shop_item)):
            if self.shop_item[i]["category"] == "Bordures" and self.shop_item[i]["selected"]:
                self.base_avatar_bordure = pygame.image.load(self.shop_item[i]["image_path"])
                self.avatar_bordure = pygame.transform.scale(self.base_avatar_bordure, (109, 109))

        
        # Boutons
        button_width, button_height = 160, 50
        self.cancel_button_rect = pygame.Rect(self.W // 2 - 150, self.pseudo_target_pos[1] + 45, 
                                             button_width, button_height)
        self.validate_button_rect = pygame.Rect(self.W // 2 + 30, self.pseudo_target_pos[1] + 45, 
                                               button_width, button_height)
        
        # Boutons de taille de pinceau
        size_button_width = 60
        size_button_height = 50
        self.decrease_button_rect = pygame.Rect(self.avatar_target_pos[0] + self.avatar_target_size - size_button_width, 
                                              self.avatar_start_pos[1] + size_button_height // 2 - 10, 
                                              size_button_width, size_button_height)
        self.increase_button_rect = pygame.Rect(self.avatar_target_pos[0] + self.avatar_target_size - size_button_width + 70, 
                                              self.avatar_start_pos[1] + size_button_height // 2 - 10, 
                                              size_button_width, size_button_height)
        
<<<<<<< HEAD

=======
        # Ajouter l'affichage de la bordure actuelle
        self.border_icon = None
        try:
            self.border_icon = pygame.image.load("assets/bordures/bordures_profil/bronze_border.png").convert_alpha()
            self.border_icon = pygame.transform.scale(self.border_icon, (70, 70))
        except:
            # Créer une icône par défaut si l'image n'est pas disponible
            self.border_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.border_icon, ORANGE, (15, 15), 15, width=3)
>>>>>>> 6d94e543b6df9e22599cf6b3cac1ce49ea5809d8
            
        # Modification: Déplacer la position du texte et de l'icône de bordure au milieu à gauche
        self.border_text_pos = (20, self.H // 2 - 15)  # Position du texte au milieu à gauche
        self.border_icon_pos = (self.border_text_pos[0] + 350, self.border_text_pos[1] - 5)  # Icône à côté du texte
        
    def save_state(self):
        self.history.append(self.avatar.copy())
        if len(self.history) > 20:  # Limite historique
            self.history.pop(0)
        self.redo_stack.clear()  # Reset REDo
        
    def size_button(self, rect, text, hover):
        # Ombre
        offset = 3
        pygame.draw.rect(self.screen, DARK_BEIGE if not hover else GRAY,
                       (rect.x + offset, rect.y + offset, rect.width, rect.height),
                       border_radius=30)

        # Bouton principal
        button_color = ORANGE if not hover else SOFT_ORANGE
        pygame.draw.rect(self.screen, button_color, rect, border_radius=30)

        # Texte du bouton
        text_surface = SMALL_FONT.render(text, True, BLACK)
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2 - (2 if hover else 0)
        self.screen.blit(text_surface, (text_x, text_y))
        
    def handle_event(self, event, mouse_pos, mouse_pressed):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_buttons:  # Si pas déjà en mode édition
                if self.avatar_start_pos[0] < mouse_pos[0] < self.avatar_start_pos[0] + self.avatar_size and \
                   self.avatar_start_pos[1] < mouse_pos[1] < self.avatar_start_pos[1] + self.avatar_size:
                    self.input_text = self.player_data["pseudo"]
                    self.is_expanding = True
                    self.pseudo_editable = True
                    return True
            else:
                if self.decrease_button_rect.collidepoint(mouse_pos):
                    self.brush_size = max(self.size_min, self.brush_size - 5)
                    return True

                elif self.increase_button_rect.collidepoint(mouse_pos):
                    self.brush_size = min(self.size_max, self.brush_size + 5)
                    return True

                elif self.validate_button_rect.collidepoint(mouse_pos):  # Valider
                    pygame.image.save(self.avatar, self.avatar_path)
                    self.player_data["pseudo"] = self.input_text
                    self.show_buttons = False
                    self.pseudo_editable = False
                    self.is_retracting = True
                    with open("data/player_data.json", "w") as f:
                        json.dump(self.player_data, f)

                    return True

                elif self.cancel_button_rect.collidepoint(mouse_pos) and self.input_text!="":  # Annuler
                    self.avatar = self.avatar_original.copy()
                    self.is_retracting = True
                    self.show_buttons = False
                    return True

                # Sélection de couleur
                for i, rect in enumerate(self.color_rects):
                    if rect.collidepoint(mouse_pos):
                        self.brush_color = self.colors[i]
                        return True
                        
                # Vérifier si on dessine sur l'avatar
                avatar_pos = self.get_current_avatar_position()
                avatar_size = self.get_current_avatar_size()
                
                rel_x = (mouse_pos[0] - avatar_pos[0]) / avatar_size
                rel_y = (mouse_pos[1] - avatar_pos[1]) / avatar_size
                if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
                    px = int(rel_x * self.avatar.get_width())
                    py = int(rel_y * self.avatar.get_height())
                    pygame.draw.circle(self.avatar, self.brush_color, (px, py), self.brush_size//self.avatar_target_size_ratio)
                    return True
                
        elif event.type == pygame.MOUSEBUTTONUP and self.show_buttons:
            self.save_state()
            return True
            
        elif event.type == pygame.KEYDOWN and self.pseudo_editable:
            if event.key == pygame.K_RETURN:  # Valider avec ENTER
                pygame.image.save(self.avatar, self.avatar_path)
                self.player_data["pseudo"] = self.input_text
                self.show_buttons = False
                self.pseudo_editable = False
                self.is_retracting = True
                with open("data/player_data.json", "w") as f:
                    json.dump(self.player_data, f)
                return True
            elif event.key == pygame.K_ESCAPE and self.input_text!="":  # Annuler avec ESC
                self.avatar = self.avatar_original.copy()
                self.is_retracting = True
                self.show_buttons = False
                return True
            elif event.key == pygame.K_UP:
                self.brush_size = min(self.size_max, self.brush_size + 5)
                return True
            elif event.key == pygame.K_DOWN:
                self.brush_size = max(self.size_max, self.brush_size - 5)
                return True
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z (Undo)
                if len(self.history) > 1:
                    self.redo_stack.append(self.history.pop())
                    self.avatar = self.history[-1].copy()
                return True
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y (REDo)
                if self.redo_stack:
                    self.avatar = self.redo_stack.pop()
                    self.history.append(self.avatar.copy())
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.unicode:
                self.input_text += event.unicode
                return True
                
        return False  # L'événement n'a pas été géré
        
    def update(self, mouse_pos, mouse_pressed):
        # Dessin sur l'avatar si en mode édition et que la souris est appuyée
        avatar_size = self.get_current_avatar_size()
        if self.show_buttons and True in mouse_pressed:
            avatar_pos = self.get_current_avatar_position()
            
            rel_x = (mouse_pos[0] - avatar_pos[0]) / avatar_size
            rel_y = (mouse_pos[1] - avatar_pos[1]) / avatar_size
            if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
                px = int(rel_x * self.avatar.get_width())
                py = int(rel_y * self.avatar.get_height())
                pygame.draw.circle(self.avatar, self.brush_color, (px, py), max(1,self.brush_size/self.avatar_target_size_ratio))
        
        # Animation Expansion
        if self.is_expanding:
            self.anim_progress += 0.1
            self.avatar_bordure = pygame.transform.scale(self.base_avatar_bordure, (avatar_size*1.09, avatar_size*1.09))
            if self.anim_progress >= 1:
                self.anim_progress = 1
                self.is_expanding = False
                self.show_buttons = True
                self.pseudo_editable = True


                for i in range(len(self.player_data["achievements"])):
                    if self.player_data["achievements"][i]["succeed"]:
                        if not self.player_data["achievements"][i]["couleurs"] in self.colors:
                            self.colors.append(self.player_data["achievements"][i]["couleurs"])

                            self.color_rects = [pygame.Rect(self.avatar_target_pos[0] + i * 60, 
                                self.avatar_target_pos[1] - 70, 50, 50) 
                                for i in range(len(self.colors))]
                
        # Animation Retrait
        if self.is_retracting:
            self.anim_progress -= 0.1
            self.avatar_bordure = pygame.transform.scale(self.base_avatar_bordure, (avatar_size*1.09, avatar_size*1.09))
            if self.anim_progress <= 0:
                self.anim_progress = 0
                self.is_retracting = False
                self.pseudo_editable = False
    
    def get_current_avatar_position(self):
        return (
            int(self.avatar_start_pos[0] + (self.avatar_target_pos[0] - self.avatar_start_pos[0]) * self.anim_progress),
            int(self.avatar_start_pos[1] + (self.avatar_target_pos[1] - self.avatar_start_pos[1]) * self.anim_progress)
        )
        
    def get_current_avatar_size(self):
        return int(100 + (self.avatar_target_size - 100) * self.anim_progress)
        
    def get_current_pseudo_position(self):
        return (
            int(self.pseudo_start_pos[0] + (self.pseudo_target_pos[0] - self.pseudo_start_pos[0]) * self.anim_progress),
            int(self.pseudo_start_pos[1] + (self.pseudo_target_pos[1] - self.pseudo_start_pos[1]) * self.anim_progress)
        )
    
    def draw(self):
        # Dessiner l'avatar
        avatar_pos = self.get_current_avatar_position()
        avatar_size = self.get_current_avatar_size()
        pseudo_pos = self.get_current_pseudo_position()
        
<<<<<<< HEAD
        #pygame.draw.circle(self.screen, ORANGE, 
         #                 (avatar_pos[0] + avatar_size // 2, avatar_pos[1] + avatar_size // 2), 
          #                avatar_size // 2 + 4 + (8 * self.anim_progress))
=======
        # Contour ORANGE de l'avatar
        pygame.draw.circle(self.screen, ORANGE, 
                          (avatar_pos[0] + avatar_size // 2, avatar_pos[1] + avatar_size // 2), 
                          avatar_size // 2 + 4 + (8 * self.anim_progress))
>>>>>>> 6d94e543b6df9e22599cf6b3cac1ce49ea5809d8
        
        # Afficher l'avatar avec masque circulaire
        temp_avatar = pygame.transform.scale(self.avatar, (avatar_size, avatar_size))
        apply_circular_mask(temp_avatar)
        self.screen.blit(temp_avatar, avatar_pos)

        # Bordure d'avatar
        self.screen.blit(self.avatar_bordure, (avatar_pos[0]-avatar_size*0.045, avatar_pos[1]-avatar_size*0.045))
        
        # Afficher le pseudo
        pseudo_surf = MEDIUM_FONT.render(self.input_text + "|" if self.pseudo_editable else self.player_data["pseudo"], True, WHITE)
        self.screen.blit(pseudo_surf, pseudo_pos)
        
        # Afficher les boutons et contrôles d'édition si activés
        if self.show_buttons:
            # Palette de couleurs
            for i, rect in enumerate(self.color_rects):
                pygame.draw.rect(self.screen, self.colors[i], rect, border_radius=8)
                
            # Aperçu de la taille du pinceau
            pygame.draw.circle(self.screen, self.brush_color, 
                              (self.avatar_target_pos[0] + self.avatar_target_size + 5, 
                               self.avatar_start_pos[1] + 50 + 60), 
                              self.brush_size + 5, width=5)
            
            # Boutons de taille du pinceau
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            for rect, label in [(self.increase_button_rect, "+"), (self.decrease_button_rect, "-")]:
                hover = rect.collidepoint(mouse_x, mouse_y)
                self.size_button(rect, label, hover)
            
            # Boutons valider/annuler
            pygame.draw.rect(self.screen, GREEN, self.validate_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, RED, self.cancel_button_rect, border_radius=10)
            
            validate_text = SMALL_FONT.render("✔ Valider", True, WHITE)
            cancel_text = SMALL_FONT.render("✕ Annuler", True, WHITE)
            
            self.screen.blit(validate_text, (self.validate_button_rect.x + 20, self.validate_button_rect.y + 10))
            self.screen.blit(cancel_text, (self.cancel_button_rect.x + 20, self.cancel_button_rect.y + 10))