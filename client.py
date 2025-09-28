import pygame
import socket
import json
import sys

# Connect to server
SERVER_IP = "192.168.106.215"  # 👈 change to your host machine’s LAN IP
PORT = 5000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LAN Multiplayer Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# Player colors (extendable)
PLAYER_COLORS = {
    1: (50, 100, 255),   # Blue
    2: (200, 50, 50),    # Red
    3: (50, 200, 50),    # Green
    4: (200, 200, 50),   # Yellow
    5: (200, 50, 200),   # Purple
}

font = pygame.font.SysFont(None, 32)

def get_key_input():
    keys = pygame.key.get_pressed()
    return {
        "left": keys[pygame.K_LEFT],
        "right": keys[pygame.K_RIGHT],
        "up": keys[pygame.K_UP],
        "down": keys[pygame.K_DOWN]
    }

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Send input to server
    key_data = json.dumps(get_key_input()).encode()
    client.sendall(key_data)

    # Receive updated game state
    try:
        data = client.recv(4096).decode()
        if not data:
            break
        state = json.loads(data)
    except:
        print("Lost connection to server.")
        break

    # Draw everything
    screen.fill(BLACK)

    # Draw players dynamically
    for pid, pl in state["players"].items():
        color = PLAYER_COLORS.get(int(pid), (255, 255, 255))  # default white if not in dict
        pygame.draw.rect(screen, color, (pl["x"], pl["y"], 50, 50))
        score_text = font.render(f"P{pid} Score: {pl['score']}", True, WHITE)
        screen.blit(score_text, (10, 10 + 30 * (int(pid)-1)))

    # Draw point
    pygame.draw.circle(screen, GOLD, (state["point"]["x"], state["point"]["y"]), 7)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.close()
sys.exit()
