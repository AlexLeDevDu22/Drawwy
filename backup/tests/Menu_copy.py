import pygame

pygame.init()

# --- Config Fenêtre ---
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Charger l'image de profil ---
AVATAR_PATH = "tests/assets/avatar.bmp"
avatar_original = pygame.image.load(
    AVATAR_PATH).convert_alpha()  # Mets ton image ici
avatar_original = pygame.transform.scale(
    avatar_original, (100, 100))  # Taille initiale
avatar = avatar_original.copy()  # Copie pour modifications

# --- Variables ---
avatar_size = 100
pseudo = "Pseudo123"
input_text = pseudo
drawing = False  # Mode dessin activé ?
brush_size = 5  # Taille du pinceau

history = [avatar.copy()]
redo_stack = []

# Positions Initiales
avatar_start_pos = (WIDTH - avatar_size - 25, 20)  # En haut à droite
pseudo_start_pos = (WIDTH - avatar_size - 35, avatar_size + 30)

# Positions Finales (Centré)
avatar_target_size = int(0.7 * HEIGHT)
avatar_target_pos = (
    (WIDTH - avatar_target_size) // 2,
    (HEIGHT - avatar_target_size) // 2 - 80)
pseudo_target_pos = (
    WIDTH //
    2 -
    50,
    avatar_target_pos[1] +
    avatar_target_size +
    70)

# État de transition
anim_progress = 0  # 0 → 1
is_expanding = False
is_retracting = False
pseudo_editable = False
show_buttons = False  # Affiche les boutons après l'animation

# --- Palette de couleurs ---
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
          (255, 165, 0), (255, 255, 255), (0, 0, 0)]
color_rects = [
    pygame.Rect(
        avatar_target_pos[0] +
        i *
        60,
        avatar_target_pos[1] -
        60,
        50,
        50) for i in range(
            len(colors))]
brush_color = colors[0]  # Rouge par défaut

# --- Boutons ---
button_width, button_height = 140, 50
cancel_button_rect = pygame.Rect(
    WIDTH // 2 - 140,
    pseudo_target_pos[1] + 45,
    button_width,
    button_height)
validate_button_rect = pygame.Rect(
    WIDTH // 2 + 20,
    pseudo_target_pos[1] + 45,
    button_width,
    button_height)

size_min = 1
size_max = 5
size_button_width = 60
size_button_height = 50
decrease_button_rect = pygame.Rect(
    avatar_target_pos[0] +
    avatar_target_size -
    size_button_width,
    avatar_start_pos[1] +
    size_button_height //
    2 -
    10,
    size_button_width,
    size_button_height)
increase_button_rect = pygame.Rect(
    avatar_target_pos[0] +
    avatar_target_size -
    size_button_width +
    70,
    avatar_start_pos[1] +
    size_button_height //
    2 -
    10,
    size_button_width,
    size_button_height)

# --- Couleurs ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
DARK_BEIGE = (222, 184, 135)
# --- Masque circulaire ---


def apply_circular_mask(image):
    mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(
        mask,
        (255,
         255,
         255,
         255),
        (image.get_width() //
         2,
         image.get_height() //
         2),
        image.get_width() //
        2)
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# --- Sauvegarde état ---


def save_state():
    history.append(avatar.copy())
    if len(history) > 20:  # Limite historique
        history.pop(0)
    redo_stack.clear()  # Reset redo


def size_button(rect, text, hover):
    # Ombre
    offset = 3
    pygame.draw.rect(
        screen,
        DARK_BEIGE if not hover else GRAY,
        (rect.x + offset,
         rect.y + offset,
         rect.width,
         rect.height),
        border_radius=30)

    # Bouton principal
    button_color = ORANGE if not hover else SOFT_ORANGE
    pygame.draw.rect(screen, button_color, rect, border_radius=30)

    # Texte du bouton
    text_surface = font.render(text, True, BLACK)
    text_x = rect.x + (rect.width - text_surface.get_width()) // 2
    text_y = rect.y + (rect.height - text_surface.get_height()
                       ) // 2 - (2 if hover else 0)
    screen.blit(text_surface, (text_x, text_y))


running = True
while running:
    screen.fill((30, 30, 30))  # Fond sombre
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    # --- Gestion du clic ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not show_buttons:  # Si pas déjà en mode édition
                if avatar_start_pos[0] < mouse_x < avatar_start_pos[0] + avatar_size and \
                   avatar_start_pos[1] < mouse_y < avatar_start_pos[1] + avatar_size:
                    input_text = pseudo
                    is_expanding = True
                    pseudo_editable = True
            else:
                if decrease_button_rect.collidepoint(mouse_x, mouse_y):
                    brush_size = max(size_min, brush_size - 1)

                elif increase_button_rect.collidepoint(mouse_x, mouse_y):
                    brush_size = min(size_max, brush_size + 1)

                # ✔ Valider
                elif validate_button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.image.save(
                        avatar, "tests/assets/avatar.bmp")  # Enregistrer en .bmp
                    pseudo = input_text
                    show_buttons = False  # Cacher les boutons
                    pseudo_editable = False
                    is_retracting = True

                # ❌ Annuler
                elif cancel_button_rect.collidepoint(mouse_x, mouse_y):
                    avatar = avatar_original.copy()  # Reset image
                    is_retracting = True
                    show_buttons = False

            for i, rect in enumerate(color_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    brush_color = colors[i]
                    # Activer gomme si blanc
                    erasing = (brush_color == (255, 255, 255))
        elif event.type == pygame.MOUSEBUTTONUP:
            save_state()

        elif event.type == pygame.KEYDOWN and pseudo_editable:
            if event.key == pygame.K_RETURN:  # Valider avec ENTER
                pygame.image.save(
                    avatar, "tests/assets/avatar.bmp")  # Enregistrer en .bmp
                pseudo = input_text
                show_buttons = False  # Cacher les boutons
                pseudo_editable = False
                is_retracting = True
            elif event.key == pygame.K_ESCAPE:  # Annuler avec ESC
                avatar = avatar_original.copy()  # Reset image
                is_retracting = True
                show_buttons = False
            elif event.key == pygame.K_UP and brush_size < size_max:  # Augmenter la taille du pinceau
                brush_size += 1
            elif event.key == pygame.K_DOWN and brush_size > size_min:  # Diminuer la taille
                brush_size -= 1
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z (Undo)
                if len(history) > 1:
                    # Sauvegarder état pour redo
                    redo_stack.append(history.pop())
                    avatar = history[-1].copy()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y (Redo)
                if redo_stack:
                    avatar = redo_stack.pop()
                    history.append(avatar.copy())

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    # --- Dessin sur l'image (seulement si agrandie) ---
    if show_buttons and True in mouse_pressed:
        rel_x = (mouse_x - avatar_pos[0]) / avatar_size
        rel_y = (mouse_y - avatar_pos[1]) / avatar_size
        if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:  # Vérifie si on est bien sur l'image
            px = int(rel_x * avatar.get_width())
            py = int(rel_y * avatar.get_height())
            pygame.draw.circle(avatar, brush_color, (px, py), brush_size)

    # --- Interpolation Positions/Tailles ---
    avatar_size = int(100 + (avatar_target_size - 50) * anim_progress)
    avatar_pos = (int(avatar_start_pos[0] +
                      (avatar_target_pos[0] -
                       avatar_start_pos[0]) *
                      anim_progress), int(avatar_start_pos[1] +
                                          (avatar_target_pos[1] -
                                           avatar_start_pos[1]) *
                                          anim_progress))

    # --- Animation Expansion ---
    if is_expanding:
        anim_progress += 0.1  # Vitesse de transition
        if anim_progress >= 1:
            anim_progress = 1
            is_expanding = False
            show_buttons = True  # Afficher les boutons une fois centré
            pseudo_editable = True

    # --- Animation Retrait ---
    if is_retracting:
        anim_progress -= 0.1  # Retour plus rapide
        if anim_progress <= 0:
            anim_progress = 0
            is_retracting = False
            pseudo_editable = False

    # --- Interpolation Positions/Tailles ---
    avatar_size = int(100 + (avatar_target_size - 50) * anim_progress)
    avatar_pos = (int(avatar_start_pos[0] +
                      (avatar_target_pos[0] -
                       avatar_start_pos[0]) *
                      anim_progress), int(avatar_start_pos[1] +
                                          (avatar_target_pos[1] -
                                           avatar_start_pos[1]) *
                                          anim_progress))
    pseudo_pos = (int(pseudo_start_pos[0] +
                      (pseudo_target_pos[0] -
                       pseudo_start_pos[0]) *
                      anim_progress), int(pseudo_start_pos[1] +
                                          (pseudo_target_pos[1] -
                                           pseudo_start_pos[1]) *
                                          anim_progress))

    # --- Dessin de l'avatar ---
    pygame.draw.circle(screen,
                       ORANGE,
                       (avatar_pos[0] + avatar_size // 2,
                        avatar_pos[1] + avatar_size // 2),
                       avatar_size // 2 + 4 + (8 * anim_progress))
    temp_avatar = pygame.transform.scale(avatar, (avatar_size, avatar_size))
    apply_circular_mask(temp_avatar)
    screen.blit(temp_avatar, avatar_pos)

    # --- Dessin du pseudo ---
    pseudo_surf = font.render(
        input_text +
        "|" if pseudo_editable else pseudo,
        True,
        WHITE)
    screen.blit(pseudo_surf, pseudo_pos)

    if show_buttons:
        # --- Palette de couleurs ---
        for i, rect in enumerate(color_rects):
            pygame.draw.rect(screen, colors[i], rect, border_radius=8)
        # size
        pygame.draw.circle(
            screen,
            brush_color,
            (avatar_target_pos[0] +
             avatar_target_size +
             5,
             avatar_start_pos[1] +
             size_button_height +
             60),
            brush_size**2 +
            5,
            width=5)

        for rect, label, action in [(increase_button_rect, "+", lambda: min(size_max, brush_size + 1)),
                                    (decrease_button_rect, "-", lambda: max(size_min, brush_size - 1))]:
            hover = rect.collidepoint(mouse_x, mouse_y)

            size_button(rect, label, hover)

        # --- Dessin des boutons (si activés) ---
        pygame.draw.rect(screen, GREEN, validate_button_rect, border_radius=10)
        pygame.draw.rect(screen, RED, cancel_button_rect, border_radius=10)

        validate_text = font.render("✔ Valider", True, WHITE)
        cancel_text = font.render("❌ Annuler", True, WHITE)

        screen.blit(
            validate_text,
            (validate_button_rect.x + 20,
             validate_button_rect.y + 15))
        screen.blit(
            cancel_text,
            (cancel_button_rect.x + 20,
             cancel_button_rect.y + 15))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
