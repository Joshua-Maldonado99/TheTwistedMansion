#Joshua Maldonado

import random

# -----------------------------
# Room Class
# -----------------------------
class Room:
    def __init__(self, color_name, actual_name, description, connections=None, items=None, puzzle=None):
        self.color_name = color_name
        self.actual_name = actual_name
        self.description = description
        self.connections = connections or {}
        self.items = items or []
        self.puzzle = puzzle
        self.visited = False

    def get_display_name(self):
        # Show actual name if visited, otherwise show color name
        return self.actual_name if self.visited else self.color_name

    def describe_exits(self):
        if not self.connections:
            return "There are no visible exits."
        lines = []
        for direction, room in self.connections.items():
            target_name = room.get_display_name()
            if direction == "forward":
                lines.append(f"Ahead is the {target_name}.")
            elif direction == "back":
                lines.append(f"Behind is the {target_name}.")
            else:
                lines.append(f"To the {direction} is the {target_name}.")
        return " ".join(lines)

    def enter(self, player, game_state):
        self.visited = True
        print(f"\nYou enter the {self.get_display_name()}.")

        #special events in special rooms
        if self.actual_name == "Ringmaster’s Chamber":
            final_room(player,game_state)
            return

        if self.actual_name == 'Secret Room':
            player.steps += 2

        if self.actual_name == 'Hallway to Clown Gallery':
            trap_event(player,game_state)
            return

        # Special hint in the starting room and main hall
        if self.actual_name == "Starting Room":
            print(f'\n{self.description}')
            print('\nYou hear a voice over the speakers, “You have been selected to play my game, you are granted 50 steps to find me if you WIN you are set FREE! LOSE and you DIE!”')
            print('\nIf stuck, scream for "help".')
            print('\nType go followed by a direction. forward, back, left or right. To Move. ')
        elif self.actual_name == "Main Hall":
            print('\nThe speaker voice is heard again. "Do not get lost or confused "look" for clues"')
   # Always show exits dynamically
        print(f'\n{self.describe_exits()}')


# -----------------------------
# Player Class
# -----------------------------
class Player:
    def __init__(self, starting_room):
        self.location = starting_room
        self.inventory = []
        self.steps = 50


# -----------------------------
# Game State
# -----------------------------
class GameState:
    def __init__(self):
        self.color_code = random.sample(["red", "green", "blue", "yellow"], 4)
        self.grave_order = random.sample(["oldest", "middle", "youngest"], 3)
        self.blue_button_found = False
        self.color_puzzle_unlocked = False
        self.balloon_pop_count = 0
        self.secret_room_opened = False
        self.dagger_unlocked = False
        self.balloon_count = 10
        self.lifted = False
        self.color_solved = False
        self.grave_solved = False
        self.end = False

        #Tracking Used Scare Events
        self.ambient_pool = []
        self.major_scare_pool = []



# -----------------------------
# Ambient & Scare Events
# -----------------------------
def ambient_event(game_state):
    all_events = [
        "You hear faint circus music drifting from nowhere...",
        "A child’s laughter echoes, then cuts off abruptly.",
        "The lights flicker, and for a moment the shadows seem to move.",
        "You feel a cold hand brush against your arm, but nothing is there.",
        "Somewhere in the distance, a balloon pops on its own.",
        "The smell of popcorn fills the air, then vanishes instantly.",
        "A whisper calls your name, but the room is empty."
    ]
    if not game_state.ambient_pool:
        game_state.ambient_pool = random.sample(all_events, len(all_events))
    if random.randint(1, 100) <= 10:  # 10% chance
        event = game_state.ambient_pool.pop()
        print(f'\n{event}')


def major_scare_event(player,game_state):
    all_events = [
        "💥 A statue crashes to the ground behind you with a deafening bang!",
        "⚡ The lights explode overhead, showering sparks around you!",
        "🔪 A knife whizzes past your head and embeds itself in the wall!",
        "🎭 A clown mannequin topples forward, almost pinning you beneath it!"
    ]
    if not game_state.major_scare_pool:
        game_state.major_scare_pool = random.sample(all_events, len(all_events))

    if random.randint(1, 100) <= 5:  # 5% chance
        event = game_state.major_scare_pool.pop()
        print(f'\n{event}')
        print("\nThe fear rattles you... you stumble and lose 1 step.")
        player.steps -= 1

def trap_event(player,game_state):
    if player.location.actual_name == 'Hallway to Clown Gallery':
        if "clown nose" in player.inventory:
            print("\nThe Clowns Come Alive And Chase Your Red Nose Into The Next Room You Shut The Door Behind You but Lose That Path!")
            player.location = game_state.portrait_room
            del player.location.connections['right']
            player.location.enter(player, game_state)


# -----------------------------
# Puzzle Functions
# -----------------------------
def pop_balloon(game_state, player):
    if game_state.secret_room_opened:
        print('\nNo More Balloons To POP!')
        print(f'\n{player.location.describe_exits()}')
    else:
        game_state.balloon_pop_count += 1
        game_state.balloon_count -= 1
        player.location.description = f"{game_state.balloon_count} red balloons float eerily, maybe you will float too... If only you had something to pop them."
        chance = game_state.balloon_pop_count * 5
        if not game_state.blue_button_found and random.randint(1, 100) <= chance:
            game_state.blue_button_found = True
            game_state.balloon_room.items.append('blue button')
            print("\n🎉 A blue button drops from a popped balloon!")
        else:
            print("\nYou pop a balloon... nothing happens.")

        if game_state.balloon_pop_count >= 10 and not game_state.secret_room_opened:
            game_state.secret_room_opened = True
            print("\n🎊 All balloons popped! A secret room opens.")
            player.location.connections["left"] = game_state.secret_room
            player.location.description = "Pieces of balloons scattered all over the floor. A secret entrance is now visible."
            if not game_state.blue_button_found:
                game_state.blue_button_found = True
                game_state.balloon_room.items.append('blue button')
                print("\n🎉 A blue button drops from a popped balloon!")

        print(f'\n{player.location.describe_exits()}')


def color_room_puzzle(game_state, player):
    if not game_state.color_puzzle_unlocked:
        if "blue button" not in player.inventory:
            print("\nYou need the blue button to activate the panel.")
            return
        elif "blue button" in player.inventory:
            print("\nThe panel is missing a button.")
            return


    print("Enter your color guess as four colors separated by spaces (e.g., red green blue yellow) or type back to stop: ")
    guess = input("> ").lower().strip().split()

    # Check if player typed 'back' or didn't enter 4 colors
    if "back" in guess or len(guess) != 4:
        print("You step away from the panel or entered an invalid guess.")
        return


    # Define allowed colors
    allowed_colors = ["red", "green", "blue", "yellow"]

    # Check if all guessed colors are valid
    for color in guess:
        if color not in allowed_colors:
            print("Invalid input. Use only red, green, blue, or yellow.")
            return
    if guess == game_state.color_code:
        game_state.color_solved = True
        print("\n✅ Correct! The door opens.")
        player.location.connections["forward"] = game_state.grave_hallway
        print(f'\n{player.location.describe_exits()}')
        player.location.description = "Room of colored light behind where the panel was is now an open door."
    else:
        print("\n❌ Incorrect! You lose 5 steps.")
        player.steps -= 5
        print(f'\n{player.location.describe_exits()}')


def graveyard_puzzle(game_state, player):
    print("\nYou see three graves with levers behind them: Oldest, Middle, Youngest.")
    order = []
    for i in range(3):
        choice = input(f"\nChoose grave #{i+1} to activate or type back to leave it for later: ").lower()
        order.append(choice)
        if choice == 'back':
            return

        if choice not in ["oldest", "middle", "youngest"]:
            print("\nThat’s not a valid grave. choose between Oldest, Middle, Youngest.")
            return

    if order == game_state.grave_order:
        game_state.grave_solved = True
        player.location.description = f"A clown skeleton is risen from the {order[2]} grave."
        print("\n💀 A clown skeleton rises holding a wheel handle.")
        player.location.items.append("wheel handle")
        print(f'\n{player.location.describe_exits()}')
    else:
        print("\n⚠️ Wrong order! You lose 5 steps.")
        player.steps -= 5
        print(f'\n{player.location.describe_exits()}')


def portrait_room_puzzle(game_state, player):
    if "lever" in player.inventory and not game_state.dagger_unlocked:
        print("You place the lever into the painting and pull it. A vault opens, revealing a ceremonial dagger!")
        game_state.dagger_unlocked = True
        player.location.description = "This room is surrounded by paintings of a family of clowns. Now with an open vault"
    elif game_state.dagger_unlocked:
        print("The vault is already open.")
    else:
        print("There is a slot for something... maybe a lever?")


def final_room(player,game_state):
    if "dagger" in player.inventory and player.steps >= 1:
        print("\n🎉 You stab the evil clown and escape the mansion!")
        game_state.end = True
        return
    else:
        print("\n☠️ You made it but you are out of steps you die while the clown laughs...")
        game_state.end = True
        return


# -----------------------------
# Setup Game
# -----------------------------
def setup_game():
        game_state = GameState()

        # --- Core rooms ---
        starting_room = Room("White Door", "Starting Room", "You awaken in darkness. Circus music echoes.")
        main_hall = Room("Green Door", "Main Hall", "A grand hallway with two branching paths.")
        storage = Room("Red Door", "Storage Room", "Dusty shelves and a locked cabinet.", items=["crowbar"])
        mirror = Room("Blue Door", "Mirror Room", "Distorted reflections surround you. If only you had a way to break free...")
        trippy_hallway = Room("Purple Door", "Trippy Hallway",
                              "The hallway feels smaller the further you go. A dusty bench sits halfway down.",
                              items=["lever"])
        dining = Room("Orange Door", "Dining Hall",
                      "You see a fancy dinner table with a giant covered platter. Are you curious enough to lift it?")

        # --- Dining Hall branches ---
        hallway_to_balloon = Room("Tan Door", "Hallway to Balloon Room", "A narrow corridor with faded posters for an old circus.")
        balloon_room = Room("Pink Door", "Balloon Room", f"{game_state.balloon_count} red balloons float eerily, maybe you will float too... If only you had something to pop them.", )
        secret_room = Room("Hidden Door", "Secret Room", "A hidden chamber with a freshly inked note. You strangely feel refreshed.",
                           items=["graveyard note"])

        stairway_to_portrait = Room("Brown Door", "Stairway to Portrait Room",
                                    "A spiraling stairway with creaky steps.")
        portrait_room = Room("Gray Door", "Portrait Room", "This room is surrounded by paintings of a family of clowns. You notice one has a slot maybe something could fit into it.",)
        hallway_to_clown_gallery = Room("Dark Gray Door", "Hallway to Clown Gallery",
                                        "Statues line the walls, watching menacingly you feel like they might move when you're not watching.")
        clown_gallery = Room("White Door", "Clown Gallery", "Statues stare silently. One has a red nose, you barely notice a small piece of paper stuck under it.",
                             items=["color note"])

        # --- Puzzle path ---
        color_room = Room("Yellow Door", "Color Puzzle Room", "A room with lights flashing different colors across is a panel missing a button. Current only red, green, and yellow are on the panel")
        hallway_to_graveyard = Room("Dark Door", "Hallway to Graveyard", "Cold air flows through this dim passage.")
        graveyard = Room("Black Door", "Graveyard", "The graves of three brothers stand in silence only the year of death is seen 1857, 1889, and 1905. There is a lever on the back of each grave.")
        circus = Room("Gold Door", "Circus Room", "Trapeze artists swing above. To your left you can see a door missing it's handle.")
        final_hallway = Room("Silver Door", "Final Hallway", "The last stretch...")
        final_room = Room("Crimson Door", "Ringmaster’s Chamber", "The evil clown awaits.")

        # --- Connections ---
        starting_room.connections = {"forward": main_hall}
        main_hall.connections = {"left": storage, "right": mirror}
        storage.connections = {"back": main_hall}
        mirror.connections = {"back": main_hall}  # an exit revealed later with crowbar
        trippy_hallway.connections = {"back": mirror, "forward": dining}

        dining.connections = {
            "back": trippy_hallway,
            "left": hallway_to_balloon,
            "right": stairway_to_portrait,
            "forward": color_room
        }
        hallway_to_balloon.connections = {"back":dining,"right": balloon_room}
        balloon_room.connections = {"back":hallway_to_balloon} #exit opens with puzzle solve
        secret_room.connections = {"back": balloon_room}

        stairway_to_portrait.connections = {"back":dining,"forward": portrait_room}
        portrait_room.connections = {"back":stairway_to_portrait,"right": hallway_to_clown_gallery}
        hallway_to_clown_gallery.connections = {"back":portrait_room,"left": clown_gallery}
        clown_gallery.connections = {"back": hallway_to_clown_gallery}

        color_room.connections = {"back":dining} #exit opens with puzzle solve
        hallway_to_graveyard.connections = {"back":color_room,"forward": graveyard}
        graveyard.connections = {"back":hallway_to_graveyard,"right": circus}
        circus.connections = {"back": graveyard}  # an exit opens later with wheel handle
        final_hallway.connections = {"back":circus,"forward": final_room}

        # --- Save special rooms into game_state ---
        game_state.trippy_hallway = trippy_hallway
        game_state.balloon_room = balloon_room
        game_state.secret_room = secret_room
        game_state.grave_hallway = hallway_to_graveyard
        game_state.graveyard = graveyard
        game_state.portrait_room = portrait_room
        game_state.final_hallway = final_hallway

        player = Player(starting_room)
        return player, game_state
# -----------------------------
# Game Loop
# -----------------------------
def game_loop(player, game_state):
    player.location.enter(player, game_state)
    while player.steps > 0:
        print(f"\nSteps remaining: {player.steps}")
        print('---------------------------------------------------------')
        command = input("Enter Your Action: ").lower()

        if command.startswith("go "):
            direction = command.split("go ")[1]
            if direction in player.location.connections:
                player.steps -= 1
                player.location = player.location.connections[direction]
                player.location.enter(player, game_state)

            else:
                print("\nYou can't go that way.")
                print(f'\n{player.location.describe_exits()}')

        elif command == "lift":
            if player.location.actual_name == "Dining Hall" and game_state.lifted == False:
                game_state.lifted = True
                print("\nA clown head lies on the dining hall table, with a note in its mouth reading: 'Pop pop pop all the balloons!'")
                player.location.description = "A clown head lies on the dining hall table, with a note in its mouth reading: 'Pop pop pop all the balloons!'"
                print(f'\n{player.location.describe_exits()}')
            else:
                print(f'\n{player.location.describe_exits()}')
                continue

        elif command.startswith("use "):
            item = command.split("use ")[1]

            if item not in player.inventory:
                print("\nYou don't have that item.")
                print(f'\n{player.location.describe_exits()}')
                continue

            # --- Notes (reminders) ---
            if item == "graveyard note":
                print(f"\nThe note reads: The order of the graves is {', '.join(map(lambda x: x.capitalize(), game_state.grave_order))}.")
                print(f'\n{player.location.describe_exits()}')
            elif item == "color note":
                print(f"\nThe note shows a sequence of colors scribbled in crayon. {" ".join(map(str,game_state.color_code))}")
                print(f'\n{player.location.describe_exits()}')
            # --- Crowbar in Mirror Room ---
            elif item == "crowbar":
                if player.location.actual_name == "Mirror Room":
                    print("\nYou smash the mirrors with the crowbar. Shards scatter everywhere, revealing a hidden exit!")
                    print("\nSadly the crowbar broke on impact.")
                    # Add the exit to Trippy Hallway
                    player.location.connections["forward"] = game_state.trippy_hallway
                    player.inventory.remove("crowbar")
                    player.location.description = 'Shattered glass covers the floor with a door now visible across the room.'
                    print(f'\n{player.location.describe_exits()}')
                else:
                    print("\nYou swing the crowbar around, but nothing useful happens.")
                    print(f'\n{player.location.describe_exits()}')

            # --- Lever in Portrait Room ---
            elif item == "lever":
                if player.location.actual_name == "Portrait Room":
                    portrait_room_puzzle(game_state, player)
                    player.inventory.remove("lever")
                    game_state.portrait_room.items.append('dagger')
                    print(f'\n{player.location.describe_exits()}')
                else:
                    print("\nThere's nowhere to use the lever here.")
                    print(f'\n{player.location.describe_exits()}')

            # --- Dagger in Balloon Room ---
            elif item == "dagger":
                if player.location.actual_name == "Balloon Room":
                    pop_balloon(game_state, player)

            # --- Blue Button in Color Room ---
            elif item == "blue button":
                if player.location.actual_name == "Color Puzzle Room":
                    print("\nYou press the blue button into the panel. The puzzle activates!")
                    game_state.color_puzzle_unlocked = True
                    player.location.description = "A room with lights flashing different colors across is a panel awaiting the correct code."
                    color_room_puzzle(game_state, player)
                    player.inventory.remove("blue button")
                else:
                    print("\nThe button does nothing here.")
                    print(f'\n{player.location.describe_exits()}')

            # --- Wheel Handle in Circus Room ---
            elif item == "wheel handle":
                if player.location.actual_name == "Circus Room":
                    print("\nYou attach the wheel handle to the mechanism and turn it. The door creaks open!")
                    # Ensure the Circus connects to Final Hallway
                    player.location.connections["left"] = game_state.final_hallway
                    player.inventory.remove("wheel handle")
                    player.location.description = 'Trapeze artists swing above. The door now remains open.'
                    print(f'\n{player.location.describe_exits()}')
                else:
                    print("\nThe wheel handle doesn't fit anywhere here.")
                    print(f'\n{player.location.describe_exits()}')

            else:
                print("\nYou can't use that here.")
                print(f'\n{player.location.describe_exits()}')

        elif command.startswith("take "):
            item = command.split("take ")[1]
            if item in player.location.items:
                player.inventory.append(item)
                player.location.items.remove(item)
                print(f"\nYou took the {item}.")
                if item == "lever":
                    print("\nThe lever feels unnaturally heavy, as if it resists being carried.")

                elif item == "crowbar":
                    print("\nThe crowbar is rusted, but sturdy enough to smash through glass or wood.")
                    print('\nType INVENTORY to see the inventory. ')
                    print('\nType USE followed by item name to use ITEM')
                elif item == "color note":
                    print("\nThe clow statue lunges towards you and breaks on the floor. In the rubble lays the 'clown nose'")
                    player.location.items.append('clown nose')
                    player.location.description = 'Clown statues now all facing the rubble of their red nose leader.'
                elif item == "clown nose":
                    print("\nYou slip the clown nose on. It squeaks. You feel ridiculous.")
                elif item == "dagger":
                    print("\nThe ceremonial dagger hums faintly, as though eager for blood.")
                print(f'\n{player.location.describe_exits()}')
            else:
                print("\nThat item isn't here.")
                print(f'\n{player.location.describe_exits()}')

        elif command == "inventory":
            print("\nInventory:", ", ".join(player.inventory) if player.inventory else "Empty")
            print(f'\n{player.location.describe_exits()}')

        elif command == "look":
            print(f'\n{player.location.description}')
            if player.location.items:
                print("\nYou see:", ", ".join(player.location.items))
                print(f'\n{player.location.describe_exits()}')
            else:
                print(f'\n{player.location.describe_exits()}')
            ambient_event(game_state)
            major_scare_event(player,game_state)

        elif command == "solve":
            if player.location.actual_name == "Graveyard":
                if not game_state.grave_solved:
                    graveyard_puzzle(game_state, player)
                else:
                    print("\nThe graveyard is already solved.")
            elif player.location.actual_name == "Color Puzzle Room":
                if not game_state.color_solved:
                    color_room_puzzle(game_state, player)
                else:
                    print("\nThe color room is already solved.")
            else:
                print("\nYou can't do that here.")
                print(f'\n{player.location.describe_exits()}')

        elif command == "help":
            print("\nAvailable commands:")
            print("  go [direction]   - Move to another room (forward, left, right, back)")
            print("  take [item]      - Pick up an item in the room")
            print("  use [item]       - Use an item (notes remind you, tools solve puzzles)")
            print("  look             - Look around the room for details")
            print("  inventory        - Check what you're carrying")
            print("  solve            - Attempt the puzzles (Color Room and Graveyard only)")
            print("  quit             - End the game")
            print("\nTip: Not everything is useful... but everything adds to the story.")
            print(f'\n{player.location.describe_exits()}')

        elif command == "quit":
            print("\nThe circus music fades as you take the easy way out...")
            break

        else:
            print("\nUnknown command. Type 'help' for a list of actions.")
            print(f'\n{player.location.describe_exits()}')

        if game_state.end:
            break
    if player.steps <= 0 and player.location.actual_name != "Ringmaster’s Chamber":
        print("\nThe last echo of circus music fades... you collapse as the mansion claims another victim.")
        return


# -----------------------------
# Run the Game
# -----------------------------
if __name__ == "__main__":
    while True:
        player, game_state = setup_game()
        game_loop(player, game_state)
    # After game ends, ask to restart
        choice = input("\nWould you like to restart the game? (yes/no): ").lower()
        print('---------------------------------------------------------')
        if choice != "yes":
            print("Thanks for playing. The circus fades into memory...")
            break