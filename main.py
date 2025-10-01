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

    def enter(self):
        self.visited = True
        print(f"\nYou enter the {self.get_display_name()}.")
        print(self.description)
        # Special hint in the starting room
        if self.actual_name == "Starting Room":
            print('You hear a voice over the speakers, “You have been selected to play my game you are granted 50 steps to find me if you WIN you are set FREE! LOSE and you DIE!”')
            print('\nIf stuck, scream for "help".')
            print('To move type GO followed by a direction. forward, back, left or right.\n')
        if self.items:
            print("You see:", ", ".join(self.items))
   # Always show exits dynamically
        print(self.describe_exits())


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
        self.balloon_pop_count = 0
        self.secret_room_opened = False
        self.dagger_unlocked = False


# -----------------------------
# Ambient & Scare Events
# -----------------------------
def ambient_event():
    events = [
        "You hear faint circus music drifting from nowhere...",
        "A child’s laughter echoes, then cuts off abruptly.",
        "The lights flicker, and for a moment the shadows seem to move.",
        "You feel a cold hand brush against your arm, but nothing is there.",
        "Somewhere in the distance, a balloon pops on its own.",
        "The smell of popcorn fills the air, then vanishes instantly.",
        "A whisper calls your name, but the room is empty."
    ]
    if random.randint(1, 100) <= 20:  # 20% chance
        print(random.choice(events))


def major_scare_event(player):
    events = [
        "💥 A statue crashes to the ground behind you with a deafening bang!",
        "⚡ The lights explode overhead, showering sparks around you!",
        "🔪 A knife whizzes past your head and embeds itself in the wall!",
        "🎭 A clown mannequin topples forward, almost pinning you beneath it!"
    ]
    if random.randint(1, 100) <= 5:  # 5% chance
        event = random.choice(events)
        print(event)
        print("The shock rattles you... you stumble and lose 1 step.")
        player.steps -= 1


# -----------------------------
# Puzzle Functions
# -----------------------------
def pop_balloon(game_state, player):
    game_state.balloon_pop_count += 1
    chance = game_state.balloon_pop_count * 5
    if not game_state.blue_button_found and random.randint(1, 100) <= chance:
        game_state.blue_button_found = True
        game_state.balloon_room.items.append('blue button')
        print("🎉 A blue button drops from a popped balloon!")
    else:
        print("You pop a balloon... nothing happens.")

    if game_state.balloon_pop_count >= 20 and not game_state.secret_room_opened:
        game_state.secret_room_opened = True
        print("🎊 All balloons popped! A secret room opens.")
        player.steps += 2
        player.inventory.append("graveyard hint note")


def color_room_puzzle(game_state, player):
    if "blue button" not in player.inventory:
        print("You need the blue button to activate the panel.")
        return

    guess = input("Enter the color sequence (e.g. red green blue yellow): ").lower().split()
    if guess == game_state.color_code:
        print("✅ Correct! The door opens.")
    else:
        print("❌ Incorrect! You lose 5 steps.")
        player.steps -= 5


def graveyard_puzzle(game_state, player):
    print("You see three graves: Oldest, Middle, Youngest.")
    order = []
    for i in range(3):
        choice = input(f"Choose grave #{i+1} to activate: ").lower()
        order.append(choice)

    if order == game_state.grave_order:
        print("💀 A clown skeleton rises and hands you a wheel handle.")
        player.inventory.append("wheel handle")
    else:
        print("⚠️ Wrong order! You lose 5 steps.")
        player.steps -= 5


def portrait_room_puzzle(game_state, player):
    if "lever" in player.inventory and not game_state.dagger_unlocked:
        print("You place the lever into the painting and pull it. A vault opens, revealing a ceremonial dagger!")
        game_state.dagger_unlocked = True
    elif game_state.dagger_unlocked:
        print("The vault is already open.")
    else:
        print("There is a slot for something... maybe a lever?")


def final_room(player):
    if "dagger" in player.inventory and player.steps >= 0:
        print("🎉 You stab the evil clown and escape the mansion!")
    else:
        print("☠️ You failed to reach the end in time...")


# -----------------------------
# Setup Game
# -----------------------------
def setup_game():
        game_state = GameState()

        # --- Core rooms ---
        starting_room = Room("White Door", "Starting Room", "You awaken in darkness. Circus music echoes.")
        main_hall = Room("Green Door", "Main Hall", "A grand hallway with two branching paths.")
        storage = Room("Red Door", "Storage Room", "Dusty shelves and a locked cabinet.", items=["crowbar"])
        mirror = Room("Blue Door", "Mirror Room", "Distorted reflections surround you.")
        trippy_hallway = Room("Purple Door", "Trippy Hallway",
                              "The hallway feels smaller the further you go. A dusty bench sits halfway down.",
                              items=["lever"])
        dining = Room("Orange Door", "Dining Hall",
                      "Lift a cloche to find a clown head with a note: 'pop pop pop them all'")

        # --- Dining Hall branches ---
        hallway_to_balloon = Room("Tan Door", "Hallway to Balloon Room", "A narrow corridor with faded posters.")
        balloon_room = Room("Pink Door", "Balloon Room", "20 balloons float eerily.", items=[])
        secret_room = Room("Hidden Door", "Secret Room", "A hidden chamber with a graveyard hint note.",
                           items=["graveyard hint note"])

        stairway_to_portrait = Room("Brown Door", "Stairway to Portrait Room",
                                    "A spiraling stairway with creaky steps.")
        portrait_room = Room("Gray Door", "Portrait Room", "A painting has a slot for a lever.", items=[])
        hallway_to_clown_gallery = Room("Dark Gray Door", "Hallway to Clown Gallery",
                                        "Statues line the walls, watching silently.")
        clown_gallery = Room("White Door", "Clown Gallery", "Statues stare silently. One has a red nose.",
                             items=["clown nose", "color code note"])

        # --- Puzzle path ---
        color_room = Room("Yellow Door", "Color Puzzle Room", "A panel awaits a color sequence.")
        hallway_to_graveyard = Room("Dark Door", "Hallway to Graveyard", "Cold air flows through this dim passage.")
        graveyard = Room("Black Door", "Graveyard", "Three graves stand in silence.",items=[])
        circus = Room("Gold Door", "Circus Room", "Trapeze artists swing above. A door awaits a wheel handle.")
        final_hallway = Room("Silver Door", "Final Hallway", "The last stretch...")
        final_room = Room("Crimson Door", "Ringmaster’s Chamber", "The evil clown awaits.")

        # --- Connections ---
        starting_room.connections = {"forward": main_hall}
        main_hall.connections = {"left": storage, "right": mirror}
        storage.connections = {"back": main_hall}
        mirror.connections = {"back": main_hall}  # exit revealed later with crowbar
        trippy_hallway.connections = {"back": mirror, "forward": dining}

        dining.connections = {
            "back": trippy_hallway,
            "left": hallway_to_balloon,
            "right": stairway_to_portrait,
            "forward": color_room
        }
        hallway_to_balloon.connections = {"back":dining,"forward": balloon_room}
        balloon_room.connections = {"back":hallway_to_balloon,"forward": secret_room}
        secret_room.connections = {"back": balloon_room}

        stairway_to_portrait.connections = {"back":dining,"forward": portrait_room}
        portrait_room.connections = {"back":stairway_to_portrait,"right": hallway_to_clown_gallery}
        hallway_to_clown_gallery.connections = {"back":portrait_room,"left": clown_gallery}
        clown_gallery.connections = {"back": hallway_to_clown_gallery}

        color_room.connections = {"back":dining,"forward": hallway_to_graveyard}
        hallway_to_graveyard.connections = {"back":color_room,"forward": graveyard}
        graveyard.connections = {"back":hallway_to_graveyard,"forward": circus}
        circus.connections = {"back": graveyard}  # exit revealed later with wheel handle
        final_hallway.connections = {"back":circus,"forward": final_room}

        # --- Save special rooms into game_state ---
        game_state.trippy_hallway = trippy_hallway
        game_state.balloon_room = balloon_room
        game_state.graveyard = graveyard
        game_state.portrait_room = portrait_room
        game_state.final_hallway = final_hallway

        player = Player(starting_room)
        return player, game_state
# -----------------------------
# Game Loop
# -----------------------------
def game_loop(player, game_state):
    player.location.enter()
    while player.steps > 0:
        print(f"\nSteps remaining: {player.steps}")
        print('------------------------------------')
        command = input("> ").lower()

        if command.startswith("go "):
            direction = command.split("go ")[1]
            if direction in player.location.connections:
                player.steps -= 1
                player.location = player.location.connections[direction]
                player.location.enter()
                ambient_event()
                major_scare_event(player)
            else:
                print("You can't go that way.")
        elif command.startswith("use "):
            item = command.split("use ")[1]

            if item not in player.inventory:
                print("You don't have that item.")
                continue

            # --- Notes (reminders) ---
            if item == "graveyard hint note":
                print("The note reads: 'The order of the graves is not what it seems...'")
            elif item == "color code note":
                print("The note shows a sequence of colors scribbled in crayon.")

            # --- Crowbar in Mirror Room ---
            elif item == "crowbar":
                if player.location.actual_name == "Mirror Room":
                    print("You smash the mirrors with the crowbar. Shards scatter everywhere, revealing a hidden exit!")
                    print("Sadly the crowbar broke on impact.")
                    # Add the exit to Trippy Hallway
                    player.location.connections["forward"] = game_state.trippy_hallway
                    player.inventory.remove("crowbar")
                else:
                    print("You swing the crowbar around, but nothing useful happens.")

            # --- Lever in Portrait Room ---
            elif item == "lever":
                if player.location.actual_name == "Portrait Room":
                    portrait_room_puzzle(game_state, player)
                    player.inventory.remove("lever")
                    game_state.portrait_room.items.append('dagger')
                else:
                    print("There's nowhere to use the lever here.")

            # --- Blue Button in Color Room ---
            elif item == "blue button":
                if player.location.actual_name == "Color Puzzle Room":
                    print("You press the blue button into the panel. The puzzle activates!")
                    color_room_puzzle(game_state, player)
                    player.inventory.remove("blue button")
                else:
                    print("The button does nothing here.")

            # --- Wheel Handle in Circus Room ---
            elif item == "wheel handle":
                if player.location.actual_name == "Circus Room":
                    print("You attach the wheel handle to the mechanism. The door creaks open!")
                    # Ensure the Circus connects forward to Final Hallway
                    player.location.connections["forward"] = game_state.final_hallway
                    player.inventory.remove("wheel handle")
                else:
                    print("The wheel handle doesn't fit anywhere here.")

            else:
                print("You can't use that here.")

        elif command.startswith("take "):
            item = command.split("take ")[1]
            if item in player.location.items:
                player.inventory.append(item)
                player.location.items.remove(item)
                print(f"You took the {item}.")
                if item == "lever":
                    print("The lever feels unnaturally heavy, as if it resists being carried.")
                elif item == "crowbar":
                    print("The crowbar is rusted, but sturdy enough to smash through glass or wood.")
                    print('Type INVENTORY to see the inventory. ')
                    print('Type USE followed by item name to use ITEM')
                elif item == "clown nose":
                    print("You slip the clown nose on. It squeaks. You feel ridiculous.")
                elif item == "dagger":
                    print("The ceremonial dagger hums faintly, as though eager for blood.")
            else:
                print("That item isn't here.")

        elif command == "inventory":
            print("Inventory:", ", ".join(player.inventory) if player.inventory else "Empty")

        elif command == "look":
            print(player.location.description)
            if player.location.items:
                print("You see:", ", ".join(player.location.items))
            else:
                print("Nothing of interest catches your eye... though the shadows seem to shift.")
            ambient_event()
            major_scare_event(player)

        elif command == "pop balloon":
            if player.location.actual_name == "Balloon Room":
                pop_balloon(game_state, player)
            else:
                print("You can't do that here.")

        elif command == "solve color":
            if player.location.actual_name == "Color Puzzle Room":
                color_room_puzzle(game_state, player)
            else:
                print("You can't do that here.")

        elif command == "solve graveyard":
            if player.location.actual_name == "Graveyard":
                graveyard_puzzle(game_state, player)
            else:
                print("You can't do that here.")

        elif command == "use lever":
            if player.location.actual_name == "Portrait Room":
                portrait_room_puzzle(game_state, player)
            else:
                print("You can't do that here.")

        elif command == "final":
            if player.location.actual_name == "Ringmaster’s Chamber":
                final_room(player)
                break
            else:
                print("You are not in the final room.")

        elif command == "help":
            print("\nAvailable commands:")
            print("  go [direction]   - Move to another room (forward, left, right, back)")
            print("  look             - Look around the room for details")
            print("  take [item]      - Pick up an item in the room")
            print("  inventory        - Check what you're carrying")
            print("  use [item]       - Use an item (notes remind you, tools solve puzzles)")
            print("  pop balloon      - Pop a balloon (Balloon Room only)")
            print("  solve color      - Attempt the color puzzle (Color Room only)")
            print("  solve graveyard  - Attempt the graveyard puzzle (Graveyard only)")
            print("  use lever        - Place lever in Portrait Room painting")
            print("  final            - Confront the clown in the final chamber")
            print("  quit             - End the game")
            print("\nTip: Not everything is useful... but everything adds to the story.")

        elif command == "quit":
            print("The circus music fades as you abandon the mansion...")
            break

        else:
            print("Unknown command. Type 'help' for a list of actions.")

    if player.steps <= 0:
        print("\nThe last echo of circus music fades... you collapse as the mansion claims another victim.")


# -----------------------------
# Run the Game
# -----------------------------
if __name__ == "__main__":
    player, game_state = setup_game()
    game_loop(player, game_state)