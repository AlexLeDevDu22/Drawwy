from re import S
import threading
from shared.ui.elements import ColorPicker, Button
from shared.utils.data_manager import *
from shared.utils.common_utils import *
from shared.tools import *
from SoloGame.ui.result_popup import PopupAnimation
from SoloGame.utils.comparaison import compare_images
import pygame

class SoloPlay:
    def __init__(self, screen, cursor, model_path, achievements_manager):
        self.last_mouse_pos = None
        self.screen = screen
        self.W, self.H = get_screen_size()
        
        # Paramètres du pinceau
        self.pen_color = BLACK
        self.pen_radius = 6
        
        # État de la souris
        self.mouse_down = False
        self.mouse_pos = (0, 0)
        
        # On définit les valeurs des rectangles d'interface
        self.define_layout(model_path)
        
        self.color_picker = ColorPicker(
            self.colors_rect.x,
            self.colors_rect.y,
            self.colors_rect.width,
            self.colors_rect.height)
        
        # Canvas persistant (Surface)
        self.canvas_surf = pygame.Surface(
            (self.canvas_rect.width, self.canvas_rect.height))
        self.canvas_surf.fill(WHITE)
        
        self.achievements_manager = achievements_manager
        self.cursor = cursor

        self.popup_result = PopupAnimation(self.screen, self.W, self.H)

        self.similarity_score = None
        self.similiraty_score_ready = False

        self.can_draw = True

        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(CONFIG["fps"])
            self.events = pygame.event.get()
            
            # Mise à jour de la taille si on redimensionne
            self.W, self.H = get_screen_size()
            
            # Gestion des événements
            for event in self.events:
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
            
            if self.mouse_down:
                color = self.color_picker.get_color_at(pygame.mouse.get_pos())
                if color:
                    self.pen_color = color
            
            # Dessin de l'arrière-plan
            self.screen.fill(BEIGE)
            
            # Dessin du canvas au centre
            self.draw_canvas()
            
            # Dessin de la palette en haut à droite
            self.color_picker.draw(self.screen)
            
            # Dessin du slider en dessous
            self.draw_slider()
            
            # Dessin du bouton "Valider" en bas à droite
            self.draw_validate_button()
            
            self.quit_button.draw(self.screen, self.mouse_pos)
            
            # Dessin du modèle
            pygame.draw.rect(self.screen, BLACK, self.model_rect, 2)
            self.screen.blit(self.model, self.model_rect)
            
            self.achievements_manager.draw_popup_if_active(self.screen)

            self.popup_result.update()
            self.popup_result.draw()
            
            if self.mouse_down and self.validate_button_rect.collidepoint(self.mouse_pos) and self.can_draw: # Validation du dessin
                
                self.can_draw = False

                PLAYER_DATA["solo_game_played"] += 1
                PLAYER_DATA["num_draws_total"] += 1
                if PLAYER_DATA["num_draws_total"] == 10:
                    self.achievements_manager.new_achievement(1)
                elif PLAYER_DATA["num_draws_total"] == 50:
                    self.achievements_manager.new_achievement(2)

                threading.Thread(target = compare_images, args=(self, model_path, self.canvas_surf,)).start()

            elif self.mouse_down and self.quit_button.hover:
                return
            
            if self.similiraty_score_ready and self.similiraty_score!=-1:
                self.similiraty_score_ready = False
               # end game
                for i in range(len(SOLO_THEMES)):
                    for j in range(len(SOLO_THEMES[i]["images"])):
                        if SOLO_THEMES[i]["images"][j]["path"] == model_path.split("/")[-1]:
                            SOLO_THEMES[i]["images"][j]["num_try"] += 1
                            if self.similarity_score >= 70:
                                SOLO_THEMES[i]["images"][j]["stars"] = max(SOLO_THEMES[i]["images"][j]["stars"], 3)
                                if self.similarity_score>=90:
                                    self.achievements_manager.new_achievement(4)
                            elif self.similarity_score >= 50:
                                SOLO_THEMES[i]["images"][j]["stars"] = max(SOLO_THEMES[i]["images"][j]["stars"], 2)
                            elif self.similarity_score >= 30:
                                SOLO_THEMES[i]["images"][j]["stars"] = max(SOLO_THEMES[i]["images"][j]["stars"], 1)
                            break
                save_data("PLAYER_DATA", "SOLO_THEMES")

                pygame.image.save(self.canvas_surf, "assets/your_best_draws/" + str(PLAYER_DATA["solo_game_played"]) + ".png")
                
                self.popup_result.start(self.similarity_score, model_path, self.canvas_surf)
            elif self.similarity_score == -1:
                
                draw_text("Comparaison en cours...",surface=self.screen, x=self.W // 2, y=self.H // 2, color=BLACK, font=MEDIUM_FONT, shadow=True)
            
            self.cursor.show(self.screen, self.mouse_pos, self.mouse_down)
            pygame.display.flip()

    def define_layout(self, model_path):

        # Canvas
        self.canvas_rect = pygame.Rect(
            int(0.05 * self.W),    # marge à gauche
            int(0.05 * self.H),    # marge en haut
            int(0.90 * self.H),    # 70% de la largeur
            int(0.90 * self.H)     # 90% de la hauteur
        )

        # Palette
        palette_width = int(0.25 * self.W)
        palette_height = int(0.30 * self.H)
        self.colors_rect = pygame.Rect(
            self.canvas_rect.right + 40,
            int(0.05 * self.H),
            palette_width - 20,
            palette_height
        )

        # Le truc qui permet de changer la taille
        slider_width = palette_width - 20
        slider_height = int(0.10 * self.H)
        self.slider_rect = pygame.Rect(
            self.canvas_rect.right + 40,
            self.colors_rect.bottom + 10,
            slider_width,
            slider_height
        )

        # Valider
        validate_button_w = 300
        validate_button_h = 50
        self.validate_button_rect = pygame.Rect(
            self.slider_rect.left + self.slider_rect.width - 80 - validate_button_w,
            self.slider_rect.bottom + 15,
            validate_button_w,
            validate_button_h
        )

        # quit button
        self.quit_button = Button(self.slider_rect.left + self.slider_rect.width - 72, self.slider_rect.bottom + 10, 60, 60, None, 25, image="assets/quit.svg")

        model_size = self.H - self.validate_button_rect.top - 120
        model = pygame.image.load(model_path)
        self.model = pygame.transform.scale(model, (model_size, model_size))

        self.model_rect = pygame.Rect(self.canvas_rect.right +
                                      40, self.validate_button_rect.top +
                                      70, model_size, model_size)

    def draw_canvas(self):
    # Cadre du canvas
        pygame.draw.rect(self.screen, BLACK, self.canvas_rect, 2)

        # On blit la Surface du canvas
        self.screen.blit(self.canvas_surf, (self.canvas_rect.x, self.canvas_rect.y))

        if self.can_draw:
            # Si la souris est enfoncée dans la zone du canvas, on dessine
            if self.mouse_down and self.canvas_rect.collidepoint(self.mouse_pos):
                local_x = self.mouse_pos[0] - self.canvas_rect.x
                local_y = self.mouse_pos[1] - self.canvas_rect.y

                if self.last_canvas_pos:  # Vérifie qu'on a une position précédente
                    last_x, last_y = self.last_canvas_pos

                    # Dessine une ligne entre la dernière position et la nouvelle
                    pygame.draw.line(self.canvas_surf, self.pen_color, (last_x, last_y), (local_x, local_y), self.pen_radius * 2)
                    pygame.draw.circle(self.canvas_surf, self.pen_color, (local_x, local_y), self.pen_radius)

                # Met à jour la dernière position
                self.last_canvas_pos = (local_x, local_y)
            
                # Achievement
                self.achievements_manager.new_achievement(0)

        # Réinitialiser la dernière position quand la souris est relevée
        if not self.mouse_down:
            self.last_canvas_pos = None  # On reset pour éviter des traits indésirables


    def draw_slider(self):
        """Dessine un slider simple sous la palette pour régler la taille du pinceau."""
        pygame.draw.rect(self.screen, (220, 220, 220), self.slider_rect)
        pygame.draw.rect(self.screen, BLACK, self.slider_rect, 2)

        # Barre du slider
        margin = 15
        line_y = self.slider_rect.centery
        line_start = (self.slider_rect.x + margin, line_y)
        line_end = (self.slider_rect.right - margin, line_y)
        pygame.draw.line(self.screen, BLACK, line_start, line_end, 3)

        # Calcul de la position du bouton sur la barre
        max_radius = 50  # Rayon maximum pour le pinceau
        total_width = line_end[0] - line_start[0]
        ratio = self.pen_radius / max_radius
        knob_x = int(line_start[0] + ratio * total_width)
        knob_y = line_y

        # Ici, le knob est directement proportionnel à la taille du pinceau
        knob_size = self.pen_radius  # Taille proportionnelle
        pygame.draw.circle(self.screen, RED, (knob_x, knob_y), knob_size)

        # Gestion du clic pour modifier la taille du pinceau
        if self.mouse_down:
            mx, my = self.mouse_pos
            if self.slider_rect.collidepoint(mx, my):
                # On borne la position entre line_start et line_end
                knob_x = max(line_start[0], min(mx, line_end[0]))
                self.pen_radius = int(
                    ((knob_x - line_start[0]) / total_width) * max_radius)
                if self.pen_radius < 1:
                    self.pen_radius = 1

    def draw_validate_button(self):
        # Fond du bouton
        pygame.draw.rect(self.screen, (0, 255, 0), self.validate_button_rect)
        # Bordure noire
        pygame.draw.rect(self.screen, BLACK, self.validate_button_rect, 2)

        # Texte du bouton
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render("Valider", True, BLACK)
        text_rect = text_surface.get_rect(
            center=self.validate_button_rect.center)
        self.screen.blit(text_surface, text_rect)


if __name__ == '__main__':
    W, H = get_screen_size()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    SoloPlay(screen)
