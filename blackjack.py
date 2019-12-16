# blackjack.py
# I made this because I'm convinced that blackjack apps which have a monetization
# scheme will play unfairly in order to get players to put USD into the game.

import random, os, sys, csv, math, statistics, time

auto_play = False
auto_play_games = 1000
auto_wager = 5

filename = 'blackjack_outcomes.csv'
file_exists = os.path.isfile(filename)
fieldnames = ['games played',
              'player wins',
              'player blackjacks',
              'house wins',
              'house blackjacks',
              'draws count',
              'player chips']

num_games = 0
player_wins_count = 0
house_wins_count = 0
draws_count = 0
player_blackjack_count = 0
house_blackjack_count = 0
this_session_games = 0
player_chips = 0


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
        player_chips = int(line['player chips'])


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
current_wager = 0

continue_play = True
player_turn = True
dealer_turn = False
shuffle_needed = True
first_game = True
end_game = False


def shuffle_deck(num_shuffles, deck, ranks, suits):
    global shuffle_needed
    for sets in range(numDecks):
        for rank in ranks:
            for suit in suits:
                deck.append(Card(rank, suit, sets))

    if num_shuffles == 1:
        for shuffle in range(num_shuffles - 1, -1, -1):
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
    global player_chips
    player_wins_count += 1
    player_chips += current_wager
    print('Player wins %s chips' % current_wager)
    return player_wins_count


def player_blackjack():
    print('Player Wins. Black Jack pays 3:2\n\n')
    global player_blackjack_count
    global player_chips
    player_blackjack_count += 1
    player_chips += int(3/2 * current_wager)
    print('Player wins %s chips' % (int(math.ceil(3/2 * current_wager))))
    return player_blackjack_count


def dealer_wins():
    print('House Wins. House takes bet.\n\n')
    global house_wins_count
    global player_chips
    house_wins_count += 1
    player_chips -= current_wager
    print('Player lost %s chips' % current_wager)
    return house_wins_count


def dealer_blackjack():
    print('Dealer has blackjack. House takes bet.\n\n')
    global house_blackjack_count
    global player_chips
    house_blackjack_count += 1
    player_chips -= current_wager
    return house_blackjack_count


def push():
    print('Push. Player keeps bet.\n\n')
    global draws_count
    draws_count += 1
    return draws_count


def blackjack_push():
    print('Push with BlackJack?!? Terrible luck...\n\n')
    global draws_count
    draws_count += 1
    return draws_count


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
    ace_count = 0
    for card in range(len(hand)):
        this_hand_value += hand[card].value
    for card in range(len(hand)):
        if hand[card].value == 11:
            ace_count += 1
    while this_hand_value > 21 and ace_count > 0:
        print('reducing ace')
        ace_count -= 1
        this_hand_value -= 10
    return this_hand_value


def show_hand(hand):
    if hand is dealer_hand:
        print('Dealers\'s hand:')
    if hand is player_hand:
        print('Player\'s hand:')
    for card in range(len(hand)):
        print(hand[card])


def set_wager(wager_amount):
    global player_chips
    global current_wager
    try:
        number = int(wager_amount)
    except ValueError:
        print('Wager amount must be a whole number of chips, not %s' % wager_amount)
        print('I\'ll make your wager the minimum of 2 chips')
        wager_amount = 2
        player_chips += current_wager
        player_chips -= wager_amount
        current_wager = wager_amount
        print('Current wager: %s' % current_wager)
        return current_wager
    else:
        wager_amount = int(wager_amount)
        if wager_amount < 2:
            print('Minimum wager is 2 chips')
            wager_amount = 2
            player_chips += current_wager
            player_chips -= wager_amount
            current_wager = wager_amount
        else:
            player_chips += current_wager
            player_chips -= wager_amount
            current_wager = wager_amount
        print('Current wager: %s' % current_wager)
        return current_wager


while continue_play:
    if shuffle_needed:
        deck = shuffle_deck(num_shuffles, deck, ranks, suits)
    player_hand = []
    dealer_hand = []
    player_value = 0
    dealer_value = 0

    player_bust = False
    dealer_bust = False
    player_has_blackjack = False
    dealer_has_blackjack = False
    blackjack_is_push = False

    split_hand = False
    double_down = False

    print('\n\nTotal Player Wins: %s   Total House Wins: %s   Total Draws: %s'
          % (player_wins_count + player_blackjack_count,
             house_wins_count + house_blackjack_count,
             draws_count))

# set wager here

    while first_game:
        if auto_play:
            print('Player Chips: %s' % player_chips)
            wager_amount = auto_wager
            current_wager = set_wager(wager_amount)
            print('Player Chips: %s' % player_chips)
            first_game = False
        else:
            print('Player Chips: %s' % player_chips)
            wager_amount = input('Wager amount:  ')
            current_wager = set_wager(wager_amount)
            print('Player Chips: %s' % player_chips)
            first_game = False

    this_session_games += 1 # debug thing to run a lot of num_games, remove later
    deal_card(player_hand)
    deal_card(dealer_hand)
    deal_card(player_hand)
    deal_card(dealer_hand)
    dealer_value = hand_value(dealer_hand)
    player_value = hand_value(player_hand)

    if player_value == 21:
        print('Player has a blackjack')
        player_has_blackjack = True

    if dealer_value == 21:
        print('Dealer has a blackjack')
        dealer_has_blackjack = True

    if player_has_blackjack and dealer_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand)
        blackjack_push()
        player_turn = False
        dealer_turn = False
        blackjack_is_push = True

    if player_has_blackjack and not dealer_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand)
        player_blackjack()
        player_turn = False
        dealer_turn = False

    if dealer_has_blackjack and not player_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand)
        dealer_blackjack()
        player_turn = False
        dealer_turn = False

    while player_turn:

        print('\n\nDealer is showing a %s' % dealer_hand[0])
        # print('Dealer is hiding a %s' % dealer_hand[1])
        # print('Dealer hand value is %s' % dealer_value)
        print('Player\'s hand:')
        for card in range(len(player_hand)):
            print(player_hand[card])
        print('Player hand value is %s' % player_value)

        if player_value > 21:
            print('Player bust')
            dealer_wins()
            player_bust = True
            player_turn = False
            break

        elif not auto_play:
            play = input('Would you like to (h)it, (s)tay   ').lower()
                             #', (d)ouble, or (s)plit?').lower()
            if 'h' in play:
                deal_card(player_hand)
                player_value = hand_value(player_hand)
            elif 's' in play:
                print('\n\n ')
                player_turn = False
                dealer_turn = True

        else:
            if player_value < 17:
                play = 'h'
                print('Player decided to hit')
            else:
                play = 's'
                print('Player decided to stay')
            if 'h' in play:
                deal_card(player_hand)
                player_value = hand_value(player_hand)
            elif 's' in play:
                print('\n\n ')
                player_turn = False
                dealer_turn = True

    while dealer_turn:

        if dealer_value < 17:
            show_hand(dealer_hand)
            print('Dealer hand value is %s' % dealer_value)
            print('Dealer must hit')
            deal_card(dealer_hand)
            dealer_value = hand_value(dealer_hand)

        if dealer_value > 21:
            show_hand(dealer_hand)
            print('Dealer hand value is %s' % dealer_value)
            dealer_bust = True
            print('Dealer bust')
            player_wins()
            break

        if dealer_value >= 17:
            show_hand(dealer_hand)
            print('Dealer hand value is %s' % dealer_value)
            print('Dealer must stay')
            break

    num_games += 1

    if player_value > dealer_value and not player_bust and not player_has_blackjack:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        player_wins()

    if player_value < dealer_value and not dealer_bust and not dealer_has_blackjack:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        dealer_wins()

    if player_value == dealer_value and not blackjack_is_push:
        print('Player\'s final hand value is %s' % player_value)
        print('Dealer\'s final hand value is %s' % dealer_value)
        push()

    end_game = True

    line = {'games played':         num_games,
            'player wins':          player_wins_count,
            'player blackjacks':    player_blackjack_count,
            'house wins':           house_wins_count,
            'house blackjacks':     house_blackjack_count,
            'draws count':          draws_count,
            'player chips':         player_chips
            }

    with open(filename, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerow(line)

# Run this_session_games number of games, then quit

    if auto_play and end_game:
        print('Current Wager: %s    Player Chips: %s' % (current_wager, player_chips))
        if this_session_games < auto_play_games:
            continue_play = True
            player_turn = True
            dealer_turn = False
            if shuffle_needed:
                deck = shuffle_deck(num_shuffles, [], ranks, suits)
            end_game = False
        else:
            continue_play = False
            end_game = False


# Player responds to a new game prompt
    while end_game:
        if not auto_play:
            print('Current Wager: %s    Player Chips: %s' % (current_wager, player_chips))
            response = input('Deal Again? (d)eal (b)et (q)uit:   ').lower()
            if response in 'd':
                continue_play = True
                player_turn = True
                dealer_turn = False
                end_game = False
                if shuffle_needed:
                    deck = shuffle_deck(num_shuffles, [], ranks, suits)
            elif response in 'q':
                continue_play = False
                end_game = False
            elif response in 'b':
                wager_amount = input('Wager amount:   ')
                current_wager = set_wager(wager_amount)
                pass
            elif response in ['']:
                pass
            else:
                print('You\'re dumb, I quit.')
                continue_play = False
                end_game = False

