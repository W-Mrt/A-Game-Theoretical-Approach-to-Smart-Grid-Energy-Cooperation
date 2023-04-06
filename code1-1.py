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

    return new_price


class Player():


    def __init__(self,name,
                renewable_boundaries=(0.1,1),
                mean_consumption=0.7,
                battery_capacity = 1. ,  #max energy that can be stored
                energy_threshold = .30, #min energy needed to work
                
            ):
        
        self.name = name
        self.battery_status = 0.5
        self.mean_consumption = mean_consumption # mean energy needed
        self.energy_consumption = np.random.normal(self.mean_consumption, scale=0.05) # energy consumption is normal distributed
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
        self.utility = 0
    
    def buy_energy(self, energy_to_buy, energy_transfer, price):
        self.utility=0
        self.battery_status += energy_to_buy
        if energy_transfer > 0:
            if energy_to_buy >= energy_transfer:
                self.utility = -price*(b*energy_transfer + (energy_to_buy - energy_transfer))
            else:
                self.utility = -price*b*energy_to_buy

        elif energy_transfer < 0:
            self.utility = -price*energy_to_buy
        else:
            self.utility = -price*energy_to_buy
            
    def sell_energy(self, energy_to_sell, energy_transfer, price):
        self.utility = 0
        self.battery_status -= energy_to_sell
        if energy_transfer > 0:
            if energy_to_sell >= energy_transfer:
                self.utility = price* (s*energy_transfer + (energy_to_sell - energy_transfer))
            else:
                self.utility = price*s*energy_to_sell
        elif energy_transfer < 0:
            self.utility = price*energy_to_sell
        else:
            self.utility = price*energy_to_sell


def static_game(players = [], days=100, start_price=1, price_elasticity=1, grid_sell=1.5, grid_buy=1.5):
    
    global s
    s = grid_sell
    global b
    b = grid_buy


    num_players = len(players) # number of players
    utility = np.zeros(shape=(num_players, days)) # utility of every player on every day
    game_state = np.zeros(shape=(num_players, days)) # battery of every player on every day
    price_series = np.zeros(shape=(1, days)) # price of every day
    temp1 = 0
    temp2 = 0

    price = get_price(start_price, price_elasticity, 0, 0)

    for w in range(days):

        utility[:,w] = [x.utility for x in players]
        game_state[:,w] = [x.battery_status for x in players]
        price_series[0, w] = price
        seller = np.array([]) # list of players that want to sell today
        buyer = np.array([]) # list of players that want to buy today
        idle = np.array([]) # list of players that want to stay idle

        for i in players:
            if (i.delta + i.battery_status) <= i.battery_min and i.delta < 0 : 
                i.want_buy = True
                buyer = np.append(buyer, i)
        
            elif (i.delta + i.battery_status) > i.battery_min and i.delta < 0 : 
                seller = np.append(seller, i)

            elif (i.delta + i.battery_status) < i.battery_capacity and i.delta >= 0 : 
                
                if np.random.randint(2) == True:
                    i.want_sell = True
                    seller = np.append(seller, i)

                else:
                    idle = np.append(idle, i)     

            elif (i.delta + i.battery_status) >= i.battery_capacity and i.delta >= 0 : 
                i.want_sell = True
                seller = np.append(seller, i)

            else:
                idle = np.append(idle, i)

        buyer = sorted(buyer, key=operator.attrgetter('battery_status')) # the buyer with the highest need buys first
       
        energy_transfer_a = 0
        energy_transfer_b = 0

        for i in idle:
            i.do_nothing
            
        for i in buyer:    
            for j in seller:
                energy_transfer_a = j.delta + j.battery_status - j.battery_min
                i.buy_energy(i.battery_capacity - i.battery_status -i.delta, energy_transfer_a, price)
                
        for i in seller:
            for j in buyer:
                energy_transfer_b = -j.delta - j.battery_status + j.battery_capacity
                i.sell_energy(j.delta + j.battery_status - j.battery_min, energy_transfer_b, price)
        
        temp2 = temp1
        temp1 = energy_transfer_a + energy_transfer_b

        price = get_price(prev_price=price,
                price__elasticity=price_elasticity,
                energy_transferred_t_1=temp1,
                energy_transferred_t_2=temp2
                )

        for x in players: # start a new day -> new random variables for consumption and renewable energy
            x.new_day()
            x.energy_supply()


    return utility, game_state, price_series
