from shared.ui.common_ui import *
from shared.tools import get_screen_size, apply_circular_mask
from shared.utils.data_manager import *
import pygame
import shutil

# Classe pour la gestion de l'avatar


class AvatarManager:

    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = get_screen_size()
        self.avatar_size = 100
        self.input_text = PLAYER_DATA["pseudo"]

        # Charger ou créer l'avatar
        self.avatar_path = "data/avatar.bmp"
        try:
            self.avatar_original = pygame.image.load(
                self.avatar_path).convert_alpha()
            self.avatar_original = pygame.transform.scale(
                self.avatar_original, (self.avatar_size, self.avatar_size))
        except BaseException:
            # Créer un avatar par défaut
            self.avatar_original = pygame.Surface((self.avatar_size, self.avatar_size), pygame.SRCALPHA)
            self.avatar_original.fill((100, 100, 255, 255))  # Bleu par défaut
            pygame.draw.circle(self.avatar_original, ORANGE, (50, 50), 50)

        self.avatar = self.avatar_original.copy()

        # Historique des modifications
        self.history = [self.avatar.copy()]
        self.redo_stack = []

        # Positions
        self.avatar_start_pos = (self.W - self.avatar_size - 25, 20)
        self.pseudo_start_pos = (
            self.avatar_start_pos[0] +
            self.avatar_size //
            2 -
            SMALL_FONT.size(
                PLAYER_DATA["pseudo"])[0] //
            2,
            self.avatar_size +
            30)

        # Positions cibles pour l'édition
        self.avatar_target_size = int(0.71 * self.H)
        self.avatar_target_pos = (
            (self.W - self.avatar_target_size) // 2,
            (self.H - self.avatar_target_size) // 2 - 70)
        self.pseudo_target_pos = (
            self.W //
            2 -
            50,
            self.avatar_target_pos[1] +
            self.avatar_target_size +
            32)
        self.avatar_target_size_ratio = self.avatar_target_size / \
            self.avatar.get_size()[0]

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

        self.colors = [(255, 255, 255), (0, 0, 0)]
        self.color_rects = [pygame.Rect(self.avatar_target_pos[0] + i * 60,
                                        self.avatar_target_pos[1] - 80, 50, 50)
                            for i in range(len(self.colors))]
        # Palette de couleurs pour l'édition d'avatar

        self.brush_color = self.colors[0]

        # Bordure d'avatar
        self.avatar_bordure_id = PLAYER_DATA["selected_items"]["Bordures"]
        self.base_avatar_bordure = pygame.image.load(
            SHOP_ITEMS[PLAYER_DATA["selected_items"]["Bordures"]]["image_path"])
        self.avatar_bordure = pygame.transform.scale(
            self.base_avatar_bordure, (109, 109))

        # Boutons
        button_width, button_height = 160, 50
        self.cancel_button_rect = pygame.Rect(
            self.W // 2 - 150,
            self.pseudo_target_pos[1] + 45,
            button_width,
            button_height)
        self.validate_button_rect = pygame.Rect(
            self.W // 2 + 30,
            self.pseudo_target_pos[1] + 45,
            button_width,
            button_height)

        # Boutons de taille de pinceau
        size_button_width = 60
        size_button_height = 50
        self.decrease_button_rect = pygame.Rect(
            self.avatar_target_pos[0] +
            self.avatar_target_size -
            size_button_width,
            self.avatar_start_pos[1] +
            size_button_height //
            2 -
            10,
            size_button_width,
            size_button_height)
        self.increase_button_rect = pygame.Rect(
            self.avatar_target_pos[0] +
            self.avatar_target_size -
            size_button_width +
            70,
            self.avatar_start_pos[1] +
            size_button_height //
            2 -
            10,
            size_button_width,
            size_button_height)

        # Modification: Déplacer la position du texte et de l'icône de bordure
        # au milieu à gauche
        # Position du texte au milieu à gauche
        self.border_text_pos = (20, self.H // 2 - 15)
        self.border_icon_pos = (
            self.border_text_pos[0] +
            350,
            self.border_text_pos[1] -
            5)  # Icône à côté du texte

    def save_state(self):
        self.history.append(self.avatar.copy())
        if len(self.history) > 20:  # Limite historique
            self.history.pop(0)
        self.redo_stack.clear()  # Reset REDo

    def size_button(self, rect, text, hover):
        # Ombre
        offset = 3
        pygame.draw.rect(
            self.screen,
            DARK_BEIGE if not hover else GRAY,
            (rect.x + offset,
             rect.y + offset,
             rect.width,
             rect.height),
            border_radius=30)

        # Bouton principal
        button_color = ORANGE if not hover else SOFT_ORANGE
        pygame.draw.rect(self.screen, button_color, rect, border_radius=30)

        # Texte du bouton
        text_surface = SMALL_FONT.render(text, True, BLACK)
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + \
            (rect.height - text_surface.get_height()) // 2 - (2 if hover else 0)
        self.screen.blit(text_surface, (text_x, text_y))

    def handle_event(self, event, mouse_pos, achievements_manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_buttons:  # Si pas déjà en mode édition
                if self.avatar_start_pos[0] < mouse_pos[0] < self.avatar_start_pos[0] + self.avatar_size and \
                   self.avatar_start_pos[1] < mouse_pos[1] < self.avatar_start_pos[1] + self.avatar_size + 30:
                    self.input_text = PLAYER_DATA["pseudo"]
                    self.is_expanding = True
                    self.pseudo_editable = True
            else:
                if self.decrease_button_rect.collidepoint(mouse_pos):
                    self.brush_size = max(self.size_min, self.brush_size - 5)

                elif self.increase_button_rect.collidepoint(mouse_pos):
                    self.brush_size = min(self.size_max, self.brush_size + 5)

                # Valider
                elif self.validate_button_rect.collidepoint(mouse_pos):
                    pygame.image.save(self.avatar, self.avatar_path)
                    PLAYER_DATA["pseudo"] = self.input_text
                    self.show_buttons = False
                    self.pseudo_editable = False
                    self.is_retracting = True
                    self.pseudo_start_pos = (
                        self.avatar_start_pos[0] +
                        self.avatar_size //
                        2 -
                        SMALL_FONT.size(
                            PLAYER_DATA["pseudo"])[0] //
                        2,
                        self.avatar_size +
                        30)
                    save_data("PLAYER_DATA")

                    self.avatar_original = self.avatar.copy()
                    # achievement leleu
                    nom = PLAYER_DATA["pseudo"].lower()
                    if nom == "leleu" or nom == "fred leleu" or nom == "frederic leleu" or nom == "mr leleu":
                        achievements_manager.new_achievement(14)

                # Annuler
                elif self.cancel_button_rect.collidepoint(mouse_pos) and self.input_text != "":
                    self.avatar = self.avatar_original.copy()
                    self.is_retracting = True
                    self.show_buttons = False

                # Sélection de couleur
                for i, rect in enumerate(self.color_rects):
                    if rect.collidepoint(mouse_pos):
                        self.brush_color = self.colors[i]

                # Vérifier si on dessine sur l'avatar
                avatar_pos = self.get_current_avatar_position()
                avatar_size = self.get_current_avatar_size()

                rel_x = (mouse_pos[0] - avatar_pos[0]) / avatar_size
                rel_y = (mouse_pos[1] - avatar_pos[1]) / avatar_size
                if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
                    px = int(rel_x * self.avatar.get_width())
                    py = int(rel_y * self.avatar.get_height())
                    pygame.draw.circle(
                        self.avatar,
                        self.brush_color,
                        (px,
                         py),
                        self.brush_size //
                        self.avatar_target_size_ratio)

        elif event.type == pygame.MOUSEBUTTONUP and self.show_buttons:
            self.save_state()

        elif event.type == pygame.KEYDOWN and self.pseudo_editable:
            if event.key == pygame.K_RETURN:  # Valider avec ENTER
                pygame.image.save(self.avatar, self.avatar_path)
                PLAYER_DATA["pseudo"] = self.input_text
                self.show_buttons = False
                self.pseudo_editable = False
                self.is_retracting = True
                self.pseudo_start_pos = (
                    self.avatar_start_pos[0] +
                    self.avatar_size //
                    2 -
                    SMALL_FONT.size(
                        PLAYER_DATA["pseudo"])[0] //
                    2,
                    self.avatar_size +
                    30)
                nom = PLAYER_DATA["pseudo"].lower()
                save_data("PLAYER_DATA")

                self.avatar_original = self.avatar.copy()

                # achievement leleu
                nom = PLAYER_DATA["pseudo"].lower()
                if nom == "leleu" or nom == "fred leleu" or nom == "frederic leleu" or nom == "mr leleu":
                    achievements_manager.new_achievement(14)
            elif event.key == pygame.K_ESCAPE and self.input_text != "":  # Annuler avec ESC
                self.avatar = self.avatar_original.copy()
                self.is_retracting = True
                self.show_buttons = False
            elif event.key == pygame.K_UP:
                self.brush_size = min(self.size_max, self.brush_size + 5)
            elif event.key == pygame.K_DOWN:
                self.brush_size = max(self.size_max, self.brush_size - 5)
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z (Undo)
                if len(self.history) > 1:
                    self.redo_stack.append(self.history.pop())
                    self.avatar = self.history[-1].copy()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y (REDo)
                if self.redo_stack:
                    self.avatar = self.redo_stack.pop()
                    self.history.append(self.avatar.copy())
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode and len(self.input_text) < 10:
                self.input_text += event.unicode

                # easter eggs
                if self.input_text == "Alx":
                    self.avatar = pygame.image.load("assets/easter_eggs/alex.jpg").convert_alpha()

                if self.input_text == "Maxence":
                    self.avatar = pygame.image.load("assets/easter_eggs/maxence.png").convert_alpha()

                if self.input_text == "Plof":
                    self.avatar = pygame.image.load("assets/easter_eggs/plof.jpg").convert_alpha()

                if self.input_text == "Shrek":
                    self.avatar = pygame.image.load("assets/easter_eggs/shrek.png").convert_alpha()
                      
                self.avatar = pygame.transform.scale(self.avatar, (self.avatar_size, self.avatar_size))

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
                pygame.draw.circle(
                    self.avatar, self.brush_color, (px, py), max(
                        1, self.brush_size / self.avatar_target_size_ratio))

        # Animation Expansion
        if self.is_expanding:
            self.anim_progress += 0.1
            self.avatar_bordure = pygame.transform.scale(
                self.base_avatar_bordure, (avatar_size * 1.09, avatar_size * 1.09))
            if self.anim_progress >= 1:
                self.anim_progress = 1
                self.is_expanding = False
                self.show_buttons = True
                self.pseudo_editable = True

                self.colors = [(255, 255, 255), (0, 0, 0)]
                self.color_rects = []
                for i in range(len(PLAYER_DATA["achievements"])):
                    if PLAYER_DATA["achievements"][i]["succeed"]:
                        self.colors.append(
                            PLAYER_DATA["achievements"][i]["couleurs"])

                        self.color_rects.append(
                            pygame.Rect(
                                self.avatar_target_pos[0] + len(
                                    self.color_rects) * 60,
                                self.avatar_target_pos[1] - 80,
                                50,
                                50))

        # Animation Retrait
        if self.is_retracting:
            self.anim_progress -= 0.1
            self.avatar_bordure = pygame.transform.scale(
                self.base_avatar_bordure, (avatar_size * 1.09, avatar_size * 1.09))
            if self.anim_progress <= 0:
                self.anim_progress = 0
                self.is_retracting = False
                self.pseudo_editable = False

        if self.avatar_bordure_id != PLAYER_DATA["selected_items"]["Bordures"]:
            self.avatar_bordure_id = PLAYER_DATA["selected_items"]["Bordures"]
            self.base_avatar_bordure = pygame.image.load(
                SHOP_ITEMS[PLAYER_DATA["selected_items"]["Bordures"]]["image_path"])
            self.avatar_bordure = pygame.transform.scale(
                self.base_avatar_bordure, (109, 109))

    def get_current_avatar_position(self):
        return (int(self.avatar_start_pos[0] +
                    (self.avatar_target_pos[0] -
                     self.avatar_start_pos[0]) *
                    self.anim_progress), int(self.avatar_start_pos[1] +
                                             (self.avatar_target_pos[1] -
                                              self.avatar_start_pos[1]) *
                                             self.anim_progress))

    def get_current_avatar_size(self):
        return int(100 + (self.avatar_target_size - 100) * self.anim_progress)

    def get_current_pseudo_position(self):
        return (int(self.pseudo_start_pos[0] +
                    (self.pseudo_target_pos[0] -
                     self.pseudo_start_pos[0]) *
                    self.anim_progress), int(self.pseudo_start_pos[1] +
                                             (self.pseudo_target_pos[1] -
                                              self.pseudo_start_pos[1]) *
                                             self.anim_progress))

    def draw(self):
        # Dessiner l'avatar
        avatar_pos = self.get_current_avatar_position()
        avatar_size = self.get_current_avatar_size()
        pseudo_pos = self.get_current_pseudo_position()

        # pygame.draw.circle(self.screen, ORANGE,
        #                 (avatar_pos[0] + avatar_size // 2, avatar_pos[1] + avatar_size // 2),
        #                avatar_size // 2 + 4 + (8 * self.anim_progress))

        # Afficher l'avatar avec masque circulaire
        temp_avatar = pygame.transform.scale(
            self.avatar, (avatar_size, avatar_size))
        apply_circular_mask(temp_avatar)
        self.screen.blit(temp_avatar, avatar_pos)

        # Bordure d'avatar
        self.screen.blit(
            self.avatar_bordure,
            (avatar_pos[0] -
             avatar_size *
             0.045,
             avatar_pos[1] -
             avatar_size *
             0.045))

        # Afficher le pseudo
        pseudo_surf = SMALL_FONT.render(
            self.input_text +
            "|" if self.pseudo_editable else PLAYER_DATA["pseudo"],
            True,
            (255, 102, 102))
        self.screen.blit(pseudo_surf, pseudo_pos)

        # Afficher les boutons et contrôles d'édition si activés
        if self.show_buttons:
            # Palette de couleurs
            for i, rect in enumerate(self.color_rects):
                pygame.draw.rect(
                    self.screen,
                    self.colors[i],
                    rect,
                    border_radius=8)

            # Aperçu de la taille du pinceau
            pygame.draw.circle(
                self.screen,
                self.brush_color,
                (self.avatar_target_pos[0] +
                 self.avatar_target_size +
                 5,
                 self.avatar_start_pos[1] +
                 50 +
                 60),
                self.brush_size +
                5,
                width=5)

            # Boutons de taille du pinceau
            mouse_x, mouse_y = pygame.mouse.get_pos()

            for rect, label in [
                    (self.increase_button_rect, "+"), (self.decrease_button_rect, "-")]:
                hover = rect.collidepoint(mouse_x, mouse_y)
                self.size_button(rect, label, hover)

            # Boutons valider/annuler
            pygame.draw.rect(
                self.screen,
                GREEN,
                self.validate_button_rect,
                border_radius=10)
            pygame.draw.rect(
                self.screen,
                RED,
                self.cancel_button_rect,
                border_radius=10)

            validate_text = SMALL_FONT.render("✔ Valider", True, WHITE)
            cancel_text = SMALL_FONT.render("✕ Annuler", True, WHITE)

            self.screen.blit(
                validate_text,
                (self.validate_button_rect.x + 20,
                 self.validate_button_rect.y + 10))
            self.screen.blit(
                cancel_text,
                (self.cancel_button_rect.x + 20,
                 self.cancel_button_rect.y + 10))
