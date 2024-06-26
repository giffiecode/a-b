import getpass
import random

# solidify version of a/b 

class Player:
    def __init__(self, name):
        self.name = name
        self.money = 300
        self.points = 0
        self.defended_points = 0
        self.current_points = 0  
        self.yes_vote = 0 
        self.no_vote = 0 
        self.defending = False  
        self.side = 'yes'
        self.update_stealable()

    def get_stealable(self):
        return self.points - self.defended_points
    
    def update_stealable(self):
        self.stealable = self.get_stealable()


    def add_points(self, points):
        self.points += points
        self.update_stealable()

    def deduct_points(self, points):
        self.points -= points
        self.update_stealable()

    def add_defended_points(self, points):
        self.defended_points += points
        self.update_stealable()

    def remove_expired_defenses(self):
        self.defended_points = 0
        self.defending = False
        self.update_stealable()

class Game:
    def __init__(self, player_names, day_period_length=60):
        self.players = [Player(name) for name in player_names] 
        # game param to set (static)  
        self.total_point = 100 
        self.round_estimate = 5  
        # game mode: spliting during a/b voting and solidifying points 
        self.no_split = False

        # for this branch self.solid = True. For false, please refer to the master branch 
        self.solid = True 
        # increase alpha to increase price increase speed
        self.alpha = 2
        # game param to set (dynamic)
        self.god_points = 100
        self.god_pot = 0
        self.points_eliminated = 0
        self.dev_team_pot = 0
        self.round = 1
        self.day_period_length = day_period_length  
        # game param to set (buy steal per round limit equation)  
        self.max = self.total_point / (len(player_names) * self.round_estimate)

    @property
    def point_price(self):
        return 1 if self.round == 1 else (self.god_points * self.alpha) / (self.god_points - self.points_eliminated)
    
    def print_prices(self):
        self.buy_price = self.point_price
        self.steal_price = self.point_price * 0.9 
        self.defend_price = self.point_price * 0.05 
        print(f"Round {self.round} price chart") 
        print()
        print(f"Buy price: {self.buy_price:.2f}")
        print(f"Steal price: {self.steal_price:.2f}")
        print(f"Defend price: {self.defend_price:.2f}") 

    def buy_points(self, player, points):
        cost = points * self.point_price
        if player.money >= cost and points <= self.max:
            player.money -= cost
            player.add_points(points)
            player.defended_points += points
            player.update_stealable() 
            player.current_points += points
            self.god_points -= points
            self.god_pot += cost
            print(f"{player.name} bought {points} points for ${cost:.2f}.")

    def steal_points(self, player, target, points):
        if target.points - target.defended_points >= points and points <= self.max:
            steal_price = 0.9 * self.point_price
            victim_compensation = 0.8 * self.point_price
            dev_team_cut = 0.1 * self.point_price

            steal_cost = points * steal_price
            compensation = points * victim_compensation
            dev_team_fee = points * dev_team_cut

            player.money -= steal_cost
            target.money += compensation
            player.defended_points += points
            target.points -= points
            player.points += points
            self.dev_team_pot += dev_team_fee
            target.update_stealable() 
            print(f"{player.name} stole {points} points from {target.name} for ${steal_cost:.2f}.")

    def defend_points(self, player, points):
        defense_price = 0.05 * self.point_price
        defense_cost = points * defense_price
        if player.money >= defense_cost and points <= player.points:
            player.money -= defense_cost
            player.add_defended_points(points)
            self.dev_team_pot += defense_cost
            player.update_stealable()
            print(f"{player.name} defended {points} points for ${defense_cost:.2f}.")

    def night_phase(self):
        total_votes_yes = 0
        total_votes_no = 0
        # with solidifying 
        if self.solid: 
            for player in self.players:
                if not self.no_split:
                    if player.current_points > 0: 
                        print(f"\n{player.name}'s turn:")
                        print(f"You have {player.current_points} points.")
                        player.yes_vote = self.get_votes(player, 'yes')
                        player.no_vote = player.current_points - player.yes_vote
                        total_votes_yes += player.yes_vote
                        total_votes_no += player.no_vote
                else:
                    if player.current_points > 0:
                        print(f"\n{player.name}'s turn:")
                        print(f"You have {player.current_points} points.")
                        player.side = self.get_votes_no_split(player)
                        if player.side == 'yes':
                            player.yes_vote = player.current_points
                        else:
                            player.no_vote = player.current_points
                        total_votes_yes += player.yes_vote
                        total_votes_no += player.no_vote
        # without solidifying
        if not self.solid: 
            for player in self.players: 
                # allow splitting, use get_votes function 
                if not self.no_split:
                    if player.points > 0:
                        print(f"\n{player.name}'s turn:")
                        print(f"You have {player.points} points.")
                        player.yes_vote = self.get_votes(player, 'yes')
                        player.no_vote = player.points - player.yes_vote
                        total_votes_yes += player.yes_vote
                        total_votes_no += player.no_vote
                else: # not allowing splitting, use get_vote_no_split
                    if player.points > 0:
                        print(f"\n{player.name}'s turn:")
                        print(f"You have {player.points} points.")
                        player.side = self.get_votes_no_split(player)
                        if player.side == 'yes':
                            player.yes_vote = player.points
                        else:
                            player.no_vote = player.points
                        total_votes_yes += player.yes_vote
                        total_votes_no += player.no_vote
        # determine majority side and total eliminated votes 
        if total_votes_yes > total_votes_no:
            majority_side = 'yes'
            eliminated_points = total_votes_yes
        elif total_votes_yes == total_votes_no:
            choices = ['yes', 'no']
            majority_side = random.choice(choices)
        else:
            majority_side = 'no'
            eliminated_points = total_votes_no

        if majority_side == 'yes':
            eliminated_points = total_votes_yes
        else:
            eliminated_points = total_votes_no

        # update total points eliminated 
        self.points_eliminated += eliminated_points

	    # a/b elimination process
        for player in self.players:
            if majority_side == 'yes':  
                # a/b eliminates stealable points first, so updating stealble and defended_points 
                if player.stealable <= player.yes_vote:
                    # a/b eliminates the rest as defended points  
                    player.defended_points -= (player.yes_vote - player.stealable)
                    player.points -= player.yes_vote 
                else: 
                    player.points -= player.yes_vote
                player.update_stealable()
            else:
                # a/b eliminates stealable points first, so updating stealble and defended_points 
                if player.stealable <= player.no_vote:
                    # a/b eliminates the rest as defended points 
                    player.defended_points -= (player.no_vote - player.stealable)
                    player.points -= player.no_vote 
                else: 
                    player.points -= player.no_vote
                player.update_stealable() 
        # reset current_points back to 0. nexr buy will add current points 
        for player in self.players: 
            player.current_points = 0 
        
    def distribute_god_pot(self):
        total_points = sum(player.points for player in self.players)
        for player in self.players:
            if total_points > 0:
                share = (player.points / total_points) * self.god_pot
                player.money += share
                print(f"{player.name} received ${share:.2f} from God's pot.")

    def get_action(self, player):
        while True:
            action = input(f"\n{player.name}'s turn: Choose your action (buy/steal/defend): ").strip().lower()
            if action in ['buy', 'steal', 'defend']:
                return action
            else:
                print("Invalid action. Please choose 'buy', 'steal', or 'defend'.")

    def get_steal_target(self, player):
        while True:
            target_name = input(f"\n{player.name}'s turn: Choose a player to steal from: ").strip()
            target = next((p for p in self.players if p.name == target_name), None)
            if target and target != player and target.points > 0:
                return target
            else:
                print("Invalid target. Please choose a valid player to steal from.")
    
    def get_action_points(self, player, action, target=None):
        while True:
            try:
                if action == 'steal':
                    points = int(input(f"\n{player.name}'s turn: Enter the number of points to {action}: (max: {min(target.points - target.defended_points, self.max)})").strip())
                    if points > self.max:
                        print(f"The input amount exceeds the maximum of {self.max}. Please enter a valid number.")
                    elif target.points - target.defended_points < points:
                        print(f"{target.name} has insufficient undefended points. Please enter a valid number.")
                    else:
                        return points
                elif action == "buy":
                    points = int(input(f"\n{player.name}'s turn: Enter the number of points to {action} (max: {self.max}): ").strip())
                    if 1 <= points <= self.max:
                        return points
                    else:
                        print("Invalid number of points. Please enter a number between 1 and {self.max}.") 
                elif action == "defend":
                    points = int(input(f"\n{player.name}'s turn: Enter the number of points to {action} (max: {player.points}): ").strip()) 
                    if points <= player.points and points * self.defend_price <= player.money:
                        return points
                    else:
                        print("Invalid number of points to defend. Please enter again.")

            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def get_defend_points(self, player):
        while True:
            try:
                points = int(input(f"\n{player.name}'s turn: Enter the number of points to defend: ").strip())
                if 1 <= points <= player.points - player.defended_points:
                    return points
                else:
                    print("Invalid number of points. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_votes_no_split(self, player):     
        while True: 
            try:
                vote = input(f"\n{player.name}'s turn: Do you want to vote 'yes' or 'no' (max {player.current_points} points)? ").strip().lower()
                if vote in ['yes', 'no']:
                    return vote
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
            except ValueError:
                print("Invalid input. Please enter 'yes' or 'no'.")

    def get_votes(self, player, vote_type):
        while True:
            try:
                votes = int(getpass.getpass(f"\n{player.name}'s turn: Enter the number of points to vote '{vote_type}' (max {player.current_points}): ").strip())
                if 0 <= votes <= player.current_points:
                    return votes
                else:
                    print(f"Invalid number of points. Please enter a number between 0 and {player.current_points}.")
            except ValueError:
                print(f"Invalid input. Please enter a number between 0 and {player.current_points}.")

    
    def ask_defense(self, player):
        if player.defended_points > 0:
            choice = input(f"{player.name}, do you want to keep defending your points? (yes/no): ").strip().lower()
            if choice == 'yes':
                while True:
                    try:
                        points = int(input(f"{player.name}, enter the number of points to defend: ").strip())
                        if points <= player.points and points > 0:
                            defense_cost = points * self.defend_price
                            if player.money >= defense_cost:
                                player.money -= defense_cost
                                player.defended_points = points
                                self.dev_team_pot += defense_cost
                                player.update_stealable()
                                player.defending = True
                                print(f"{player.name} defended {points} points for ${defense_cost:.2f}.")
                                break
                            else:
                                print("Not enough money to defend that many points.")
                        else:
                            print("Invalid number of points.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            else:
                player.remove_expired_defenses()
    

    def play_round(self):
        self.print_prices() 

        # ask people with defense whether they want to continue, and reset
        for player in self.players:
            self.print_balance()
            self.ask_defense(player) 

        # reset the vote and clear the defenses
        for player in self.players:
            player.yes_vote = 0
            player.no_vote = 0

        for player in self.players:
            if player.defending:
                continue 
            self.print_balance()
            action = self.get_action(player)
            if action == 'buy':
                points = self.get_action_points(player, 'buy')
                self.buy_points(player, points)
            elif action == 'steal':
                target = self.get_steal_target(player)
                points = self.get_action_points(player, 'steal', target)
                self.steal_points(player, target, points)
            elif action == 'defend':
                points = self.get_defend_points(player)
                self.defend_points(player, points)

        self.night_phase()
        self.round += 1 

    def print_balance(self):
            print(f"\n--- Round {self.round} ---")
            for player in self.players:
                print(f"\n{player.name}: ${player.money:.2f}, {player.points} points, {player.defended_points} defended points, {player.stealable} stealable points") 
            print(f"\n") 

    def start_game(self):
        while self.god_points > 0: 
            self.play_round()

        self.distribute_god_pot()
        print("\nGame over!")
        for player in self.players:
            print(f"{player.name}: ${player.money:.2f}, {player.points} points")

# Example Usage
player_names = ["Alice", "Bob", "Charlie", "Diana"]
game = Game(player_names)
game.start_game()
