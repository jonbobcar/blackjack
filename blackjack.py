# blackjack.py
# I made this because I'm convinced that blackjack apps which have a monetization
# scheme will play unfairly in order to get players to put USD into the game.

import random
import os
import math
import time
import json

auto_play = False
auto_play_games = 50
auto_wager = 2

fieldnames = ['games played',
              'player wins',
              'player blackjacks',
              'house wins',
              'house blackjacks',
              'draws count',
              'player chips']

filename = 'blackjack_data.json'
file_exists = os.path.isfile(filename)

if not file_exists:
    num_games = 0
    player_wins_count = 0
    house_wins_count = 0
    draws_count = 0
    player_blackjack_count = 0
    house_blackjack_count = 0
    player_stack = 100

this_session_games = 0


# Open database containing play statistics and persistent player stack
if file_exists:
    with open(filename, 'r') as f:
        json_data = json.load(f)

    num_games = json_data['games played']
    player_wins_count = json_data['player wins']
    house_wins_count = json_data['house wins']
    draws_count = json_data['draws count']
    player_blackjack_count = json_data['player blackjacks']
    house_blackjack_count = json_data['house blackjacks']
    player_stack = json_data['player chips']


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


class Hand:
    def __init__(self, player, hand_number):
        self.player = player
        self.cards = []
        self.value = 0
        self.ace_count = 0
        self.soft_hand = False
        self.hand_number = hand_number
        self.split_aces = False
        self.wager = 0
        self.additional_wager = 0
        self.bust = False

    def hand_value(self):
        self.value = 0
        self.ace_count = 0
        for card in self.cards:
            self.value += card.value
        for card in self.cards:
            if card.value == 11:
                self.ace_count += 1
                self.soft_hand = True
        while self.value > 21 and self.ace_count > 0:
            self.ace_count -= 1
            self.value -= 10
            self.soft_hand = False
        return self.value

    def __str__(self):
        print('%s\'s hand:' % self.player)
        for card in self.cards:
            print(card)


suits = ["Clubs", "Spades", "Hearts", "Diamonds"]
ranks = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

deck = []
num_decks = 8
num_shuffles = 3
current_wager = 0
num_hands = 1

continue_play = True
player_turn = True
dealer_turn = False
shuffle_needed = True
first_game = True
end_turn = False
split_aces = False


def shuffle_deck():
    # Each time shuffle_deck() is called, the current deck is overwritten by num_decks new 52
    # card decks and then shuffled num_shuffles times.
    new_deck = []
    global shuffle_needed
    for sets in range(num_decks):
        for rank in ranks:
            for suit in suits:
                new_deck.append(Card(rank, suit, sets))

    if num_shuffles == 1:
        for shuffle in range(num_shuffles - 1, -1, -1):
            print('Shuffling %s deck one time. Total of %s cards' % (num_decks, len(new_deck)))
            for i in range(len(new_deck) - 1, 0, -1):
                j = random.randint(0, i)
                new_deck[i], new_deck[j] = new_deck[j], new_deck[i]
    else:
        for shuffle in range(num_shuffles - 1, -1, -1):
            print('Shuffling %s decks %s more times. Total of %s cards' % (num_decks, shuffle, len(new_deck)))
            for i in range(len(new_deck) - 1, 0, -1):
                j = random.randint(0, i)
                new_deck[i], new_deck[j] = new_deck[j], new_deck[i]

    offset_bound = round(len(new_deck) * .1)
    shuffle_offset = random.randint(-offset_bound, offset_bound)
    shuffle_spot = round(len(new_deck) * 0.85) + shuffle_offset
    new_deck.insert(shuffle_spot - 5, Card(0, 'shuffle', 'shuffle'))

    shuffle_needed = False
    return new_deck


def set_wager(new_wager, old_wager, stack):
    # set_wager() takes the current chips on the table, adds then to the player stack
    # then removes wager_amount chips from the player stack and puts them on the table.
    global current_wager
    global continue_play
    if stack + old_wager < 2:
        print('You don\'t have enough chips to play')
        continue_play = False
        return old_wager, stack
    try:
        _ = int(new_wager)
    except ValueError:
        print('Wager amount must be a whole number of chips, not \"%s\"' % new_wager)
        print('I\'ll make your wager the minimum of 2 chips')
        new_wager = 2
        stack += old_wager
        stack -= new_wager
        # old_wager = new_wager
        print('Current wager: %s' % new_wager)
        return new_wager, stack
    else:
        new_wager = int(new_wager)
        if new_wager < 2:
            print('Minimum wager is 2 chips, I\'ll set your wager to 2 chips.')
            new_wager = 2
            stack += old_wager
            stack -= new_wager
            print('Current wager: %s' % new_wager)
            return new_wager, stack
        else:
            stack += old_wager
            if new_wager > stack:
                print('You only have %s chips.' % stack)
                new_wager = stack
                stack -= new_wager
            else:
                stack -= new_wager
            print('Current wager: %s' % new_wager)
            return new_wager, stack


def player_wins():
    print('\n\nPlayer Wins. House pays 2:1\n\n')
    global player_wins_count
    global player_stack
    player_wins_count += 1
    player_stack += current_wager
    print('Player wins %s chips' % current_wager)
    if double_down:
        player_stack += current_wager // 2
    return player_wins_count


def player_blackjack():
    print('\n\nPlayer Wins. Black Jack pays 3:2\n\n')
    global player_blackjack_count
    global player_stack
    player_blackjack_count += 1
    player_stack += math.ceil(player_hand[0].wager * 3 // 2) + player_hand[0].wager
    print('Player wins %s chips' % (int(math.ceil(3/2 * current_wager))))
    return player_blackjack_count


def dealer_wins():
    print('\n\nHouse Wins. House takes bet.\n\n')
    global house_wins_count
    global player_stack
    house_wins_count += 1
    if double_down:
        player_stack -= current_wager // 2
    else:
        player_stack -= current_wager
    print('Player lost %s chips' % current_wager)
    return house_wins_count


def dealer_blackjack():
    print('\n\nDealer has blackjack. House takes bet.\n\n')
    global house_blackjack_count
    global player_stack
    house_blackjack_count += 1
    return house_blackjack_count


def push():
    print('\n\nPush. Player keeps bet.\n\n')
    global draws_count
    draws_count += 1
    return draws_count


def blackjack_push():
    print('\n\nPush with BlackJack?!? Terrible luck...\n\n')
    global draws_count
    draws_count += 1
    return draws_count


def deal_card(where):
    # deal_card() looks for the shuffle card, then pops the first card out of the deck
    # and appends it to the where hand.
    global shuffle_needed
    if deck[0].rank == 'shuffle':
        print('_,.-.,__,.-.,_ The shuffle card has been reached _,.-.,__,.-.,_')
        shuffle_needed = True
        deck.pop(0)
    where.cards.append(deck.pop(0))
    where.hand_value()
    print('A card was dealt and now there are %s cards left in the deck\n' % len(deck))
    time.sleep(0.5)


def show_hand(hand):
    # show_hand() prints hand using the __str__ method in Card
    print('%s %s\'s hand:' % (hand.player, hand.hand_number))
    for card in hand.cards:
        print(card)


def show_chips():
    print('Player\'s Stack: %s' % player_stack)


def down_doubler(hand, stack):
    print('Player doubled down and %s chips added to wager' % hand.wager)
    stack -= hand.wager
    hand.additional_wager = hand.wager
    deal_card(hand)
    show_hand(hand)
    store_results()
    return hand, stack


def hand_splitter():
    # hand_splitter() removes one card from the current hand and puts it into a new hand.
    global num_hands
    global player_stack
    split_player_hand = Hand(player_hand[0].player, num_hands)
    split_player_hand.cards.append(player_hand[num_hands - 1].cards.pop(0))
    if player_hand[num_hands - 1].cards[0].value == 11:
        player_hand[num_hands - 1].split_aces = True
        split_player_hand.split_aces = True
    deal_card(player_hand[num_hands - 1])
    split_player_hand.wager = current_wager
    player_stack -= current_wager
    player_hand.append(split_player_hand)
    num_hands += 1
    print('Current hand split into two hands with wager of %s chips each' % current_wager)
    show_chips()


def store_results():
    results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                    'Hand Value': player_hand[current_hand_count].value,
                    'Wager': player_hand[current_hand_count].wager + player_hand[current_hand_count].additional_wager
                    })


def write_out(file_name):
    # Writes the game statistics and persistent player stack out to database.
    json_data = {
        'games played':       num_games,
        'player wins':        player_wins_count,
        'player blackjacks':  player_blackjack_count,
        'house wins':         house_wins_count,
        'house blackjacks':   house_blackjack_count,
        'draws count':        draws_count,
        'player chips':       player_stack
                  }

    with open(filename, 'w') as write_file:
        json.dump(json_data, write_file, indent=6)


while continue_play:
    this_session_games += 1  # auto_play variable

    player_hand = []
    dealer_hand = []
    results = []
    current_hand_count = 0
    total_hands = 1

    player_bust = False
    dealer_bust = False
    player_has_blackjack = False
    dealer_has_blackjack = False
    blackjack_is_push = False

    first_turn = True
    splittable_hand = False
    double_down = False

    print('\n\nTotal Player Wins: %s   Total House Wins: %s   Total Draws: %s'
          % (player_wins_count + player_blackjack_count,
             house_wins_count + house_blackjack_count,
             draws_count))

    while first_game:
        if auto_play:
            print('Player\'s Stack: %s' % player_stack)
            wager_amount = auto_wager
            current_wager, player_stack = set_wager(wager_amount, current_wager, player_stack)
            print('Player\'s Stack: %s' % player_stack)
            first_game = False
        if not auto_play:
            print('Dealer Must Hit on Soft 17')
            print('Player\'s Stack: %s' % player_stack)
            time.sleep(0.5)
            wager_amount = input('Wager amount:   ')
            print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
            current_wager, player_stack = set_wager(wager_amount, current_wager, player_stack)
            print('Player\'s Stack: %s' % player_stack)
            first_game = False

    if not continue_play:
        break

    if shuffle_needed:
        deck = shuffle_deck()
    player_hand.append(Hand('Player', 0))
    player_hand[0].wager = current_wager
    dealer_hand = Hand('Dealer', 0)
    deal_card(player_hand[0])
    deal_card(dealer_hand)
    deal_card(player_hand[0])
    deal_card(dealer_hand)

    if player_hand[0].value == 21:
        print('Player has a blackjack')
        player_has_blackjack = True

    if dealer_hand.value == 21:
        print('Dealer has a blackjack')
        dealer_has_blackjack = True

    if player_has_blackjack and dealer_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand[0])
        blackjack_push()
        player_turn = False
        dealer_turn = False
        blackjack_is_push = True
    elif player_has_blackjack and not dealer_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand[0])
        player_blackjack()
        player_turn = False
        dealer_turn = False
    elif dealer_has_blackjack and not player_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand[0])
        dealer_blackjack()
        player_turn = False
        dealer_turn = False

    while player_turn:
        while current_hand_count < total_hands:
            if len(player_hand[current_hand_count].cards) == 1:
                deal_card(player_hand[current_hand_count])
            playing_hand = True
            first_hand = True
            while playing_hand:
                if player_hand[current_hand_count].cards[0].value == player_hand[current_hand_count].cards[1].value:
                    splittable_hand = True
                print('\n\nDealer is showing a %s' % dealer_hand.cards[0])
                # print('Dealer is hiding a %s' % dealer_hand[1])
                # print('Dealer hand value is %s\n' % dealer_hand.value)
                show_hand(player_hand[current_hand_count])
                print('Player hand value is %s\n' % player_hand[current_hand_count].value)

                if player_hand[current_hand_count].split_aces:
                    print('Player hand value is %s\n' % player_hand[current_hand_count].value)
                    playing_hand = False
                    store_results()

                elif player_hand[current_hand_count].value == 21:
                    print('Player stands on 21')
                    playing_hand = False
                    store_results()

                elif first_turn and splittable_hand:
                    time.sleep(0.5)
                    play = input('Would you like to (h)it, (s)tay, (d)ouble down, s(p)lit   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 'd' in play:
                        double_down = True
                        player_hand[current_hand_count], player_stack = \
                            down_doubler(player_hand[current_hand_count], player_stack)
                        playing_hand = False
                    elif 'p' in play:
                        hand_splitter()
                        did_split = True
                        splittable_hand = False
                        first_hand = True
                        total_hands += 1

                    elif 's' in play:
                        playing_hand = False
                        store_results()

                elif first_turn and not splittable_hand:
                    time.sleep(0.5)
                    play = input('Would you like to (h)it, (s)tay, (d)ouble down   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 'd' in play:
                        double_down = True
                        player_hand[current_hand_count], player_stack = \
                            down_doubler(player_hand[current_hand_count], player_stack)
                        playing_hand = False

                    elif 's' in play:
                        playing_hand = False
                        store_results()

                else:
                    time.sleep(0.5)
                    play = input('Would you like to (h)it, (s)tay   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 's' in play:
                        playing_hand = False
                        store_results()

                if player_hand[current_hand_count].value > 21:
                    print('Player hand value is %s\n' % player_hand[current_hand_count].value)
                    print('Player bust')
                    player_hand[current_hand_count].bust = True
                    playing_hand = False
                    store_results()

            current_hand_count += 1
            print(results)
        player_turn = False
        dealer_turn = True

# Autoplayer here

        # else:
        #     if first_turn and this_hand.value in [11] and auto_play:
        #         play = 'd'
        #         print('Player decided to DOUBLE DOWN')
        #         double_down = True
        #         print('Wager was doubled for the remainder of this hand')
        #         set_wager(current_wager * 2)
        #         show_chips()
        #         deal_card(this_hand)
        #         show_hand(this_hand)
        #         print('Player hand value is %s\n' % player_hand[0].value)
        #         if player_hand[0].value > 21:
        #             print('Player bust')
        #             dealer_wins()
        #             player_bust = True
        #             player_turn = False
        #             break
        #         player_turn = False
        #         dealer_turn = True
        #         first_turn = False
        #     elif this_hand.value == 17 and player_hand[0].soft_hand:
        #         play = 'h'
        #         print('Player decided to hit on soft 17')
        #         first_turn = False
        #     elif this_hand.value < 17:
        #         play = 'h'
        #         print('Player decided to hit')
        #         first_turn = False
        #     else:
        #         play = 's'
        #         print('Player decided to stay')
        #     if 'h' in play:
        #         deal_card(this_hand)
        #     elif 's' in play:
        #         print('\n\n ')
        #         player_turn = False
        #         dealer_turn = True

    if all(hand.bust is True for hand in player_hand):
        dealer_turn = False

    while dealer_turn:

        if dealer_hand.value == 17 and dealer_hand.soft_hand:
            show_hand(dealer_hand)
            print('Dealer must hit on soft 17')
            deal_card(dealer_hand)

        elif dealer_hand.value < 17:
            show_hand(dealer_hand)
            print('Dealer hand value is %s\n' % dealer_hand.value)
            time.sleep(1)
            print('Dealer must hit')
            deal_card(dealer_hand)

        elif dealer_hand.value > 21:
            show_hand(dealer_hand)
            print('Dealer hand value is %s\n' % dealer_hand.value)
            time.sleep(1)
            dealer_bust = True
            # print('Dealer bust')
            dealer_turn = False

        else:
            show_hand(dealer_hand)
            print('Dealer hand value is %s' % dealer_hand.value)
            time.sleep(1)
            print('Dealer must stay on hard 17+')
            dealer_turn = False

    num_games += 1

# Check results of each player hand against dealer's hand
#     for result in results:
#         if result.get('Hand Value') > 21 and not dealer_bust:
#             print('Hand %s was a bust' % result.get('Hand Number'))
#         elif result.get('Hand Value') in range(dealer_hand.value + 1, 22) and not dealer_bust:
#             print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
#             print('Dealer hand value: %s' % dealer_hand.value)
#             print('Hand %s is a winner' % result.get('Hand Number'))
#         elif result.get('Hand Value') < dealer_hand.value and not dealer_bust:
#             print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
#             print('Dealer hand value: %s' % dealer_hand.value)
#             print('Hand %s is a loser' % result.get('Hand Number'))
#         elif result.get('Hand Value') == dealer_hand.value:
#             print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
#             print('Dealer hand value: %s' % dealer_hand.value)
#             print('Hand %s is a push' % result.get('Hand Number'))
#         elif result.get('Hand Value') < 22 and dealer_bust:
#             print('Dealer\'s hand was a bust')
#             print('Hand %s is a winner' % result.get('Hand Number'))

    current_wager = 0
    for hand in player_hand:
        if not player_has_blackjack and not dealer_has_blackjack:
            print('\n\nDealer hand value: %s' % dealer_hand.value)
            if hand.value > 21 and not dealer_bust:
                show_hand(dealer_hand)
                print('Player\'s hand %s was a bust' % hand.hand_number)
            elif hand.value < 22 and dealer_bust:
                print('Dealer\'s hand was a bust')
                print('Hand %s is a winner' % hand.hand_number)
                print('Payout of %s chips' % (hand.wager + hand.additional_wager))
                player_stack += (hand.wager + hand.additional_wager) * 2
            elif hand.value in range(dealer_hand.value + 1, 22):
                print('Hand %s value: %s' % (hand.hand_number, hand.value))
                print('Hand %s is a winner' % hand.hand_number)
                print('Payout of %s chips' % (hand.wager + hand.additional_wager))
                player_stack += (hand.wager + hand.additional_wager) * 2
            elif hand.value < dealer_hand.value:
                print('Hand %s value: %s' % (hand.hand_number, hand.value))
                print('Hand %s is a loser' % hand.hand_number)
            elif hand.value == dealer_hand.value:
                print('Hand %s value: %s' % (hand.hand_number, hand.value))
                print('Hand %s is a push' % hand.hand_number)
                player_stack += hand.wager + hand.additional_wager

    end_turn = True
    num_hands = 1

    # Player responds to a new game prompt
    while end_turn:
        if not auto_play:
            print('\n')
            if current_wager == 0:
                current_wager, player_stack = set_wager(wager_amount, current_wager, player_stack)
            print('Player\'s Stack: %s' % player_stack)
            time.sleep(0.5)
            if not continue_play:
                break
            # current_wager, player_stack = set_wager(wager_amount, current_wager, player_stack)
            response = input('Deal Again? (d)eal, change (b)et, (q)uit:   ').lower()
            print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
            if response in 'd':
                if player_stack + current_wager < 2:
                    continue_play = False
                    print('You don\'t have enough chips to play')
                    player_stack += current_wager
                else:
                    continue_play = True
                    player_turn = True
                    dealer_turn = False
                    end_turn = False
                    if shuffle_needed:
                        deck = shuffle_deck()
            elif response in 'q':
                player_stack += current_wager
                continue_play = False
                end_turn = False
            elif response in 'b':
                print('Total player chips: %s' % (player_stack + current_wager))
                time.sleep(0.5)
                wager_amount = input('Wager amount:   ')
                print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
                current_wager, player_stack = set_wager(wager_amount, current_wager, player_stack)

    # Run this_session_games number of games, then quit

    # if auto_play and end_turn:
    #     if double_down:
    #         current_wager //= 2
    #         double_down = False
    #     print('Current Wager: %s    Player\'s Stack: %s' % (current_wager, player_stack))
    #     if this_session_games < auto_play_games:
    #         continue_play = True
    #         player_turn = True
    #         dealer_turn = False
    #         if shuffle_needed:
    #             deck = shuffle_deck()
    #         end_turn = False
    #     else:
    #         continue_play = False
    #         end_turn = False

if not continue_play:
    print('Saving %s\'s %s chips for next time!' % (player_hand[0].player, player_stack))
    write_out(filename)
