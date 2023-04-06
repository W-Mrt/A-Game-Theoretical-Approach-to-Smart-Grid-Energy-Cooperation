import numpy as np
import operator
import seaborn as sns
import matplotlib.pyplot as plt


def get_price(prev_price=0,
            price__elasticity=1,
            energy_transferred_t_1=0,
            energy_transferred_t_2=0
            ):

    new_price = prev_price + price__elasticity*(energy_transferred_t_1- energy_transferred_t_2)
    if new_price < 0:
        new_price = prev_price
        print('New price too low, old price stays')

    return new_price



class Player():



    def __init__(self,name,
                renewable_boundaries=(0.1,1),
                mean_consumption=0.7,
                battery_capacity = 1. ,  #max energy that can be stored
                energy_threshold = .30, #min energy needed to work
                damage = 1000  

            ):
        self.name = name
        self.damage = damage
        self.battery_status = 0.5
        self.mean_consumption = mean_consumption # mean energy needed
        self.energy_consumption = np.random.normal(self.mean_consumption, scale=0.1) # energy consumption is normal distributed
        self.battery_capacity = battery_capacity
        self.battery_min = energy_threshold
        self.uniform_boundaries = renewable_boundaries # boundaries for uniform probability for of renewable energy
        self.renewable_energy = np.random.uniform(*self.uniform_boundaries)
        self.utility = 0
        self.delta = self.renewable_energy - self.energy_consumption
        

    def energy_supply(self):
            energy_supply = self.renewable_energy - self.energy_consumption
            self.battery_status += energy_supply 
            return self.battery_status

    def new_day(self):
        self.energy_consumption = np.random.normal(self.mean_consumption, scale=0.05)
        self.renewable_energy = np.random.uniform(*self.uniform_boundaries)
        
    
    def do_nothing(self):
        
        utility = 0

        if self.battery_status < self.battery_min:
            utility -= self.damage

        return utility
    
    def buy_energy(self, energy_to_buy, energy_transfer, price):
        
        utility=0

        if energy_to_buy > 0:
            utility -= self.damage

        utility = utility -price*np.abs(energy_to_buy)
        
        return utility
        
            
    def sell_energy(self, energy_to_sell, energy_transfer, price):
        
        utility = 0

        if energy_to_sell < 0:
            utility -= self.damage
    
        utility = utility + price*np.abs(energy_to_sell)
            
        return utility

    def make_a_play(self, action, energy_to_buy, energy_to_sell):

        if action == 1:
            self.battery_status += np.abs(energy_to_buy)

        if action == 2:
            self.battery_status -= np.abs(energy_to_sell)

        #if self.battery_status > self.battery_capacity:
        #    self.battery_status = self.battery_capacity

def static_game(players = [], days=100, start_price=1, price_elasticity=1, grid_sell=1.0, grid_buy=1.2):
    
    global s
    s = grid_sell
    global b
    b = grid_buy


    num_players = len(players) # number of players
    utility = np.zeros(shape=(num_players, days))
    daily_utility = np.zeros(shape=(num_players, 3)) # utility of every player on every day
    game_state = np.zeros(shape=(num_players, days)) # battery of every player on every day
    price_series = np.zeros(shape=(1, days)) # price of every day
    temp1 = 0
    temp2 = 0

    price = get_price(start_price, price_elasticity, 0, 0)

    for w in range(days):

        utility[:,w] = [x.utility for x in players]
        game_state[:,w] = [x.battery_status for x in players]
        price_series[0, w] = price

       
        energy_transfer_sell = 0
        energy_transfer_buy = 0

        temp3 = 0

        for i in range(num_players):

            energy_transfer_sell = players[i].delta + players[i].battery_status - players[i].battery_min #left over energy
            energy_transfer_buy = energy_transfer_sell

            daily_utility[i] = [players[i].do_nothing(),
            players[i].buy_energy(energy_transfer_buy, 0, price),
            players[i].sell_energy(energy_transfer_sell, 0, price)]

            action = np.argmax(daily_utility[i])
            actions = ['nothing', 'buy', 'sell']
            print('Player : ', i, ' is ', actions[action])
            players[i].make_a_play(action, energy_transfer_buy, energy_transfer_sell)
            players[i].utility = daily_utility[i, action]
            temp3 += energy_transfer_sell

        temp2 = temp1
        temp1 = temp3

        price = get_price(prev_price=price,
                price__elasticity=price_elasticity,
                energy_transferred_t_1=temp1,
                energy_transferred_t_2=temp2
                )

        for x in players: # start a new day -> new random variables for consumption and renewable energy
            x.new_day()
            x.energy_supply()


    return utility, game_state, price_series
