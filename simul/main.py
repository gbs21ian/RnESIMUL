import pygame
import sys
import threading
from simulation import Simulation
from utils import save_csv
from stats_popup import StatsPopup

MAIN_WIDTH, MAIN_HEIGHT = 640, 640
BG_COLOR = (230, 230, 240)

def run_stats_popup(sim):
    popup = StatsPopup(sim)
    popup.run()

def main():
    pygame.init()
    screen = pygame.display.set_mode((MAIN_WIDTH, MAIN_HEIGHT))
    pygame.display.set_caption("Korean Road Simulation (Braess Paradox)")
    sim = Simulation(screen)
    clock = pygame.time.Clock()
    running = True

    stats_thread = threading.Thread(target=run_stats_popup, args=(sim,), daemon=True)
    stats_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sim.stop()
                    save_csv("results.csv", sim.get_results_csv())

        screen.fill(BG_COLOR)
        sim.draw_grid_background()
        sim.update()
        sim.render()
        pygame.display.flip()
        clock.tick(25)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()