# blackjack.py

import random, os, sys, csv, math, statistics, time


filename = 'blackjack_outcomes.csv'
file_exists = os.path.isfile(filename)
fieldnames = ['games played',
              'player wins',
              'player blackjacks',
              'house wins',
              'house blackjacks',
              'draws count']

num_games = 0
player_wins_count = 0
house_wins_count = 0
draws_count = 0
player_blackjack_count = 0
house_blackjack_count = 0
this_session_games = 0


if file_exists:
    with open(filename, 'r') as f:
        csv_reader = csv.DictReader(f)
        csv_data = list(csv_reader)

    for line in csv_data:
        num_games = int(line['games played'])
        player_wins_count = int(line['player wins'])
        house_wins_count = int(line['house wins'])
        draws_count = int(line['draws count'])
        player_blackjack_count = int(line['player blackjacks'])
        house_blackjack_count = int(line['house blackjacks'])


class Card:
    def __init__(self, rank, suit, sets):
        self.rank = rank
        self.suit = suit
        self.sets = sets
        if rank in range(1, 14):
            self.value = rank
        if rank in ['J', 'Q', 'K']:
            self.value = 10
        if rank == 'A':
            self.value = 11

        # This is the "shuffle card" which when drawn indicates that the end of the
        # deck is coming up and a new deck is needed.
        if rank == 0:
            self.rank = suit
            self.suit = suit
            self.value = suit

    def __str__(self):
        return '%s of %s' % (self.rank, self.suit)


suits = ["Clubs", "Spades", "Hearts", "Diamonds"]
ranks = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

deck = []
numDecks = 6
num_shuffles = 5


def shuffle_deck(num_shuffles, deck, ranks, suits):
    global shuffle_needed
    for sets in range(numDecks):
        for rank in ranks:
            for suit in suits:
                deck.append(Card(rank, suit, sets))

    if num_shuffles == 1:
        for shuffle in range(num_shuffles - 1 , -1, -1):
            print('Shuffling %s deck one time. Total of %s cards' % (numDecks, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]
    else:
        for shuffle in range(num_shuffles - 1, -1, -1):
            print('Shuffling %s decks %s more times. Total of %s cards' % (numDecks, shuffle, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]

    offsetbound = round(len(deck) * .1)
    shuffleoffset = random.randint(-offsetbound, offsetbound)
    shufflespot = round(len(deck) * 0.85) + shuffleoffset
    deck.insert(shufflespot - 5, Card(0, 'shuffle', 'shuffle'))

    shuffle_needed = False
    return deck


def player_wins():
    print('Player Wins. House pays 2:1\n\n')
    global player_wins_count
    player_wins_count += 1
    return player_wins_count
    # double chips


def player_blackjack():
    print('Player Wins. Black Jack pays 3:2\n\n')
    global player_blackjack_count
    player_blackjack_count += 1
    return player_blackjack_count
    # 3/2 chips


def dealer_wins():
    print('House Wins. House takes bet.\n\n')
    global house_wins_count
    house_wins_count += 1
    return house_wins_count
    # keep chips


def dealer_blackjack():
    print('Dealer has blackjack. House takes bet.\n\n')
    global house_blackjack_count
    house_blackjack_count += 1
    return house_blackjack_count
    # keep chips


def push():
    print('Push. Player keeps bet.')
    global draws_count
    draws_count += 1
    return draws_count
    # add chips


deck = shuffle_deck(num_shuffles, deck, ranks, suits)
continue_play = True
player_turn = True
preTurn = True
dealer_turn = False


def deal_card(who):
    global shuffle_needed
    if deck[0].rank == 'shuffle':
        print('_,.-.,__,.-.,_ The shuffle card has been reached _,.-.,__,.-.,_')
        shuffle_needed = True
        deck.pop(0)
    who.append(deck.pop(0))
    print('Card was dealt and now there are %s cards left in deck' % len(deck))


def hand_value(hand):
    this_hand_value = 0
    for card in range(len(hand)):
        this_hand_value += hand[card].value
    return this_hand_value


while continue_play:
    player_hand = []
    dealer_hand = []
    player_value = 0
    dealer_value = 0

    player_bust = False
    dealer_bust = False
    player_has_blackjack = False
    dealer_has_blackjack = False

    print('Player: %s   House: %s   draws_count: %s'
          % (player_wins_count + player_blackjack_count,
             house_wins_count + house_blackjack_count,
             draws_count))
    num_games += 1
    this_session_games += 1 # debug thing to run a lot of num_games, remove later
    deal_card(player_hand)
    deal_card(dealer_hand)
    deal_card(player_hand)
    deal_card(dealer_hand)
    dealer_value = hand_value(dealer_hand)
    player_value = hand_value(player_hand)

    print('Player\'s hand:')
    for card in range(len(player_hand)):
        print(player_hand[card])
    print('Player hand value is %s' % player_value)
    print('Dealer is showing a %s' % dealer_hand[0])
    print('Dealer is hiding a %s' % dealer_hand[1])
    print('Dealer hand value is %s' % dealer_value)

    if player_value == 21:
        print('Player has a blackjack')
        player_has_blackjack = True

    if dealer_value == 21:
        print('Dealer has a blackjack')
        dealer_has_blackjack = True

    if player_has_blackjack and dealer_has_blackjack:
        print('Push')
        player_turn = False
        dealer_turn = False

    if player_has_blackjack and not dealer_has_blackjack:
        player_blackjack()
        player_turn = False
        dealer_turn = False

    if dealer_has_blackjack and not player_has_blackjack:
        dealer_blackjack()
        player_turn = False
        dealer_turn = False

    while player_turn:

        if player_value > 21:
            dealer_wins()
            player_bust = True
            player_turn = False
            break

        else:
            # play = input('Would you like to (h)it, (s)tay, (d)ouble, or (s)plit?').lower()
            play = 's'
            if 'h' in play:
                deal_card(player_hand)
            elif 's' in play:
                player_turn = False
                dealer_turn = True

    while dealer_turn:

        if dealer_value < 17:
            print('Dealer must hit')
            deal_card(dealer_hand)
            dealer_value += dealer_hand[-1].value
            print('Dealers\'s hand:')
            for card in range(len(dealer_hand)):
                print(dealer_hand[card])
            print('Dealer hand value is %s' % dealer_value)

        if dealer_value > 21:
            dealer_bust = True
            print('Dealer bust')
            player_wins()
            break

        if dealer_value >= 17:
            print('Dealer must stay')
            break

    if player_value > dealer_value and not player_has_blackjack:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        player_wins()
        # player chips increase

    if player_value < dealer_value and not dealer_bust and not dealer_has_blackjack:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        dealer_wins()
        # player chips stay constant

    if player_value == dealer_value:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        push()
        # player chips stay constant

    line = {'games played':         num_games,
            'player wins':          player_wins_count,
            'player blackjacks':    player_blackjack_count,
            'house wins':           house_wins_count,
            'house blackjacks':     house_blackjack_count,
            'draws count':          draws_count,
            }

    with open(filename, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerow(line)

    if this_session_games < 1000:
        continue_play = True
        player_turn = True
        dealer_turn = False
        preTurn = True
        if shuffle_needed:
            deck = shuffle_deck(num_shuffles, [], ranks, suits)
    else:
        continue_play = False


    # Player responds to a new game prompt

    # response = input('Deal Again? (d)eal (b)et (q)uit').lower()
    # if response in 'd':
    #     continue_play = True
    #     player_turn = True
    #     dealer_turn = False
    #     preTurn = True
    #     if shuffle_needed:
    #         deck = shuffle_deck(num_shuffles, [], ranks, suits)
    # elif response in 'q':
    #     continue_play = False
    # elif response not in ['d', 'q']:
    #     print('You\'re dumb, I quit.')
    #     continue_play = False
