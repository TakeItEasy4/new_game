import pygame
import socket
import json
import sys

# Connect to server
SERVER_IP = "192.168.106.215"  # 👈 host machine IP
PORT = 5000
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1)

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LAN Multiplayer UDP Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
PLAYER_COLORS = {
    1: (50, 100, 255),   # Player 1 = Blue
    2: (200, 50, 50),    # Player 2 = Red
    3: (50, 200, 50)     # Player 3 = Green
}

font = pygame.font.SysFont(None, 32)

# Local state
my_id = None
local_pos = pygame.Rect(0, 0, 50, 50)
latest_state = {"players": {}, "point": {"x": 400, "y": 300}}

def get_key_input():
    keys = pygame.key.get_pressed()
    return {
        "left": keys[pygame.K_LEFT],
        "right": keys[pygame.K_RIGHT],
        "up": keys[pygame.K_UP],
        "down": keys[pygame.K_DOWN]
    }

def apply_local_prediction(rect, keys):
    if keys["left"]:  rect.x -= 5
    if keys["right"]: rect.x += 5
    if keys["up"]:    rect.y -= 5
    if keys["down"]:  rect.y += 5

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = get_key_input()
    # Send inputs
    client.sendto(json.dumps(keys).encode(), (SERVER_IP, PORT))

    # Predict my own movement immediately
    if my_id is not None:
        apply_local_prediction(local_pos, keys)

    # Receive state
    try:
        data, _ = client.recvfrom(4096)
        latest_state = json.loads(data.decode())

        # Set my ID the first time
        if my_id is None:
            # Find which player is closest to my local pos
            # (better: server should send ID separately, but this works for 3 players)
            my_id = max(latest_state["players"].keys())

        # Correct local position with server state
        if str(my_id) in latest_state["players"]:
            pl = latest_state["players"][str(my_id)]
            local_pos.x, local_pos.y = pl["x"], pl["y"]

    except socket.timeout:
        pass

    # Draw everything
    screen.fill(BLACK)

    # Draw players
    for pid, pl in latest_state["players"].items():
        color = PLAYER_COLORS.get(int(pid), (255, 255, 255))
        pygame.draw.rect(screen, color, (pl["x"], pl["y"], 50, 50))
        score_text = font.render(f"P{pid} Score: {pl['score']}", True, WHITE)
        screen.blit(score_text, (10, 10 + 30 * (int(pid)-1)))

    # Draw point
    pygame.draw.circle(screen, GOLD, (latest_state["point"]["x"], latest_state["point"]["y"]), 7)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.close()
sys.exit()
