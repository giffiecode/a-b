# todo  
# 12 if someone said yes to continue defend, no further action can be conducted and stop asking them 

 
# done 
# 1 not eliminating points / not displaying correctly 
# 7 how to implement the on-chain defense system? ask people with defense first 
# 4 printing the buy / steal / defense price at the beginning of each round   
# 2 auto-defense for bought / steal points 
# 6 display who's available for stealing 
# 10 target: if steal exceeds undefended points, let enter again  
# 11 defend get action point
# 8 ask people with any defense first - continue defensing? 
    # yes - how many defense? set. 
    # no - clear defense point.    

# later 
# 5 vim variable_prompt? 
# 6 push code from vs code  

import getpass
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.money = 1000
        self.points = 0
        self.defended_points = 0 
        self.yes_vote = 0 
        self.no_vote = 0 
        self.defending = False

    def add_points(self, points):
        self.points += points

    def deduct_points(self, points):
        self.points -= points

    def add_defended_points(self, points):
        self.defended_points += points

    def remove_expired_defenses(self):
        self.defended_points = 0

class Game:
    def __init__(self, player_names, day_period_length=60):
        self.players = [Player(name) for name in player_names]
        self.god_points = 1000
        self.god_pot = 0
        self.points_eliminated = 0
        self.dev_team_pot = 0
        self.round = 1
        self.day_period_length = day_period_length 

    @property
    def point_price(self):
        return 1 if self.round == 1 else 1000 / (1000 - self.points_eliminated)
    
    def print_prices(self):
        self.buy_price = self.point_price
        self.steal_price = self.point_price * 0.9 
        self.defend_price = self.point_price * 0.05 
        print(f"Round {self.round} price chart") 
        print()
        print(f"Buy price: {self.buy_price:.2f}")
        print(f"Steal price: {self.steal_price:.2f}")
        print(f"Defend price: {self.defend_price:.2f}") 
        self.get_stealable()  # Call it here
    
    def buy_points(self, player, points):
        cost = points * self.point_price
        if player.money >= cost and points <= 25:
            player.money -= cost
            player.add_points(points)
            player.defended_points += points
            self.god_points -= points
            self.god_pot += cost
            print(f"{player.name} bought {points} points for ${cost:.2f}.")

    def steal_points(self, player, target, points):
        if target.points - target.defended_points >= points and points <= 25:
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
            print(f"{player.name} stole {points} points from {target.name} for ${steal_cost:.2f}.")

    def defend_points(self, player, points):
        defense_price = 0.05 * self.point_price
        defense_cost = points * defense_price
        if player.money >= defense_cost and points <= player.points:
            player.money -= defense_cost
            player.add_defended_points(points)
            self.dev_team_pot += defense_cost
            print(f"{player.name} defended {points} points for ${defense_cost:.2f}.")

    def night_phase(self):
        total_votes_yes = 0
        total_votes_no = 0
        for player in self.players:
            if player.points > 0:
                print(f"\n{player.name}'s turn:")
                print(f"You have {player.points} points.")
                player.yes_vote = self.get_votes(player, 'yes')
                player.no_vote = player.points - player.yes_vote

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
                player.points -= player.yes_vote
            else:
                player.points -= player.no_vote
        
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
                    points = int(input(f"\n{player.name}'s turn: Enter the number of points to {action}: (max: {min(target.points - target.defended_points, 25)})").strip())
                    if points > 25:
                        print("The input amount exceeds the maximum of 25. Please enter a valid number.")
                    elif target.points - target.defended_points < points:
                        print(f"{target.name} has insufficient undefended points. Please enter a valid number.")
                    else:
                        return points
                elif action == "buy":
                    points = int(input(f"\n{player.name}'s turn: Enter the number of points to {action} (max: 25): ").strip())
                    if 1 <= points <= 25:
                        return points
                    else:
                        print("Invalid number of points. Please enter a number between 1 and 25.") 
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

    def get_votes(self, player, vote_type):
        while True:
            try:
                votes = int(getpass.getpass(f"\n{player.name}'s turn: Enter the number of points to vote '{vote_type}' (max {player.points}): ").strip())
                if 0 <= votes <= player.points:
                    return votes
                else:
                    print(f"Invalid number of points. Please enter a number between 0 and {player.points}.")
            except ValueError:
                print(f"Invalid input. Please enter a number between 0 and {player.points}.")
    
    def get_stealable(self): 
        print()
        print("Stealable points in round", self.round, ":") 
        print()
        for player in self.players:
            if player.defended_points < player.points:
                stealable_points = player.points - player.defended_points
                print(f"{player.name}: {stealable_points} stealable points.")

    
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
            self.ask_defense(player) 

        # reset the vote and clear the defenses
        for player in self.players:
            player.yes_vote = 0
            player.no_vote = 0

        for player in self.players:
            if player.defending:
                continue
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

    def start_game(self):
        while self.god_points > 0:
            print(f"\n--- Round {self.round} ---")
            for player in self.players:
                print(f"\n{player.name}: ${player.money:.2f}, {player.points} points") 
            print(f"\n")    
            self.play_round()

        self.distribute_god_pot()
        print("\nGame over!")
        for player in self.players:
            print(f"{player.name}: ${player.money:.2f}, {player.points} points")

# Example Usage
player_names = ["Alice", "Bob", "Charlie", "Diana"]
game = Game(player_names)
game.start_game()