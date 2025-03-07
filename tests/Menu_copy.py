import pygame

pygame.init()

# --- Config Fenêtre ---
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Charger l'image de profil ---
AVATAR_PATH = "tests/avatar.bmp"
avatar_original = pygame.image.load(AVATAR_PATH)  # Mets ton image ici
avatar_original = pygame.transform.scale(avatar_original, (100, 100))  # Taille initiale
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
avatar_target_pos = ((WIDTH - avatar_target_size) // 2, (HEIGHT - avatar_target_size) // 2 - 50)
pseudo_target_pos = (WIDTH // 2 - 50, avatar_target_pos[1] + avatar_target_size + 10)

# État de transition
anim_progress = 0  # 0 → 1
is_expanding = False
is_retracting = False
pseudo_editable = False
show_buttons = False  # Affiche les boutons après l'animation

# --- Palette de couleurs ---
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 255, 255), (0, 0, 0)]
color_rects = [pygame.Rect(avatar_target_pos[0] + i * 40, avatar_target_pos[1]-50, 30, 30) for i in range(len(colors))]
brush_color = colors[0]  # Rouge par défaut

# --- Boutons ---
button_width, button_height = 120, 40
validate_button_rect = pygame.Rect(WIDTH // 2 - 130, pseudo_target_pos[1] + 50, button_width, button_height)
cancel_button_rect = pygame.Rect(WIDTH // 2 + 10, pseudo_target_pos[1] + 50, button_width, button_height)

button_width = 60
button_height = 60
button_padding = 20
add_button_rect = pygame.Rect(WIDTH // 2 - button_width - button_padding, HEIGHT // 2 - button_height // 2, button_width, button_height)
subtract_button_rect = pygame.Rect(WIDTH // 2 + button_padding, HEIGHT // 2 - button_height // 2, button_width, button_height)


# --- Couleurs ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

# --- Masque circulaire ---
def apply_circular_mask(image):
    mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (image.get_width() // 2, image.get_height() // 2), image.get_width() // 2)
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# --- Sauvegarde état ---
def save_state():
    history.append(avatar.copy())
    if len(history) > 20:  # Limite historique
        history.pop(0)
    redo_stack.clear()  # Reset redo

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
                    is_expanding = True
                    pseudo_editable = True
            if add_button_rect.collidepoint(event.pos):  # Clique sur "+"
                if brush_size < 5:
                    brush_size += 1
            elif subtract_button_rect.collidepoint(event.pos):  # Clique sur "-"
                if brush_size > 1:
                    brush_size -= 1
            else:
                if validate_button_rect.collidepoint(mouse_x, mouse_y):  # ✔ Valider
                    pygame.image.save(avatar, "tests/avatar.bmp")  # Enregistrer en .bmp
                    show_buttons = False  # Cacher les boutons
                    pseudo_editable = False
                    is_retracting = True

                if cancel_button_rect.collidepoint(mouse_x, mouse_y):  # ❌ Annuler
                    avatar = avatar_original.copy()  # Reset image
                    is_retracting = True
                    show_buttons = False

            for i, rect in enumerate(color_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    print("Couleur choisie:", colors[i])
                    brush_color = colors[i]
                    erasing = (brush_color == (255, 255, 255))  # Activer gomme si blanc


        if event.type == pygame.KEYDOWN and pseudo_editable:
            if event.key == pygame.K_RETURN and pseudo_editable:  # Valider avec ENTER
                pygame.image.save(avatar, AVATAR_PATH)
                show_buttons = False
                pseudo_editable = False
            elif event.key == pygame.K_ESCAPE and pseudo_editable:  # Annuler avec ESC
                avatar = history[0].copy()
                is_retracting = True
                show_buttons = False
            elif event.key == pygame.K_UP:  # Augmenter la taille du pinceau
                brush_size += 1
            elif event.key == pygame.K_DOWN and brush_size > 1:  # Diminuer la taille
                brush_size -= 1
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z (Undo)
                if len(history) > 1:
                    redo_stack.append(history.pop())  # Sauvegarder état pour redo
                    avatar = history[-1].copy()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y (Redo)
                if redo_stack:
                    avatar = redo_stack.pop()
                    history.append(avatar.copy())

    # --- Dessin sur l'image (seulement si agrandie) ---
    if show_buttons and mouse_pressed[0]:  # Si on clique gauche
        rel_x = (mouse_x - avatar_pos[0]) / avatar_size
        rel_y = (mouse_y - avatar_pos[1]) / avatar_size
        if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:  # Vérifie si on est bien sur l'image
            px = int(rel_x * avatar.get_width())
            py = int(rel_y * avatar.get_height())
            pygame.draw.circle(avatar, brush_color, (px, py), brush_size)
            save_state() 

    # --- Interpolation Positions/Tailles ---
    avatar_size = int(100 + (avatar_target_size - 50) * anim_progress)
    avatar_pos = (
        int(avatar_start_pos[0] + (avatar_target_pos[0] - avatar_start_pos[0]) * anim_progress),
        int(avatar_start_pos[1] + (avatar_target_pos[1] - avatar_start_pos[1]) * anim_progress)
    )

    # --- Animation Expansion ---
    if is_expanding:
        anim_progress += 0.1  # Vitesse de transition
        if anim_progress >= 1:
            anim_progress = 1
            is_expanding = False
            show_buttons = True  # Afficher les boutons une fois centré

    # --- Animation Retrait ---
    if is_retracting:
        anim_progress -= 0.1  # Retour plus rapide
        if anim_progress <= 0:
            anim_progress = 0
            is_retracting = False
            pseudo_editable = False

    # --- Interpolation Positions/Tailles ---
    avatar_size = int(100 + (avatar_target_size - 50) * anim_progress)
    avatar_pos = (
        int(avatar_start_pos[0] + (avatar_target_pos[0] - avatar_start_pos[0]) * anim_progress),
        int(avatar_start_pos[1] + (avatar_target_pos[1] - avatar_start_pos[1]) * anim_progress)
    )
    pseudo_pos = (
        int(pseudo_start_pos[0] + (pseudo_target_pos[0] - pseudo_start_pos[0]) * anim_progress),
        int(pseudo_start_pos[1] + (pseudo_target_pos[1] - pseudo_start_pos[1]) * anim_progress)
    )

    # --- Dessin de l'avatar ---
    temp_avatar = pygame.transform.scale(avatar, (avatar_size, avatar_size))
    apply_circular_mask(temp_avatar)
    screen.blit(temp_avatar, avatar_pos)

    # --- Dessin du pseudo ---
    pseudo_surf = font.render(input_text + "|" if pseudo_editable else pseudo, True, WHITE)
    screen.blit(pseudo_surf, pseudo_pos)

    if show_buttons:
        # --- Palette de couleurs ---
        for i, rect in enumerate(color_rects):
            pygame.draw.rect(screen, colors[i], rect)
        # size
        # Fond du compteur
        pygame.draw.rect(screen, (100,100,230), (WIDTH // 2 - 180, HEIGHT // 2 - 60, 360, 120))
        pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 180, HEIGHT // 2 - 60, 360, 120), 5)  # Bordure noire

        # Texte de la valeur actuelle
        value_text = font.render(str(brush_size), True, WHITE)
        screen.blit(value_text, (WIDTH // 2 - value_text.get_width() // 2, HEIGHT // 2 - value_text.get_height() // 2))

        pygame.draw.rect(screen, GRAY, add_button_rect)
        pygame.draw.rect(screen, BLACK, add_button_rect, 5)
        add_text = font.render("+", True, BLACK)
        screen.blit(add_text, (add_button_rect.x + add_button_rect.width // 2 - add_text.get_width() // 2, add_button_rect.y + add_button_rect.height // 2 - add_text.get_height() // 2))

        # Bouton Soustraire (-)
        pygame.draw.rect(screen, GRAY, subtract_button_rect)
        pygame.draw.rect(screen, BLACK, subtract_button_rect, 5)
        subtract_text = font.render("-", True, BLACK)
        screen.blit(subtract_text, (subtract_button_rect.x + subtract_button_rect.width // 2 - subtract_text.get_width() // 2, subtract_button_rect.y + subtract_button_rect.height // 2 - subtract_text.get_height() // 2))


        # --- Dessin des boutons (si activés) ---
        pygame.draw.rect(screen, GREEN, validate_button_rect)
        pygame.draw.rect(screen, RED, cancel_button_rect)

        validate_text = font.render("✔ Valider", True, WHITE)
        cancel_text = font.render("❌ Annuler", True, WHITE)

        screen.blit(validate_text, (validate_button_rect.x + 10, validate_button_rect.y + 10))
        screen.blit(cancel_text, (cancel_button_rect.x + 10, cancel_button_rect.y + 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
