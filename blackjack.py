# blackjack.py
# I made this because I'm convinced that blackjack apps which have a monetization
# scheme will play unfairly in order to get players to put USD into the game.

import random, os, sys, csv, math, statistics, time

auto_play = False
auto_play_games = 50
auto_wager = 2

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
player_stack = 100


# Open database containing play statistics and persistent player stack
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
        player_stack = int(line['player chips'])


######
player_stack = 100
######

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
            print('reducing ace')
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
    deck = []
    global shuffle_needed
    for sets in range(num_decks):
        for rank in ranks:
            for suit in suits:
                deck.append(Card(rank, suit, sets))

    if num_shuffles == 1:
        for shuffle in range(num_shuffles - 1, -1, -1):
            print('Shuffling %s deck one time. Total of %s cards' % (num_decks, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]
    else:
        for shuffle in range(num_shuffles - 1, -1, -1):
            print('Shuffling %s decks %s more times. Total of %s cards' % (num_decks, shuffle, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]

    offsetbound = round(len(deck) * .1)
    shuffleoffset = random.randint(-offsetbound, offsetbound)
    shufflespot = round(len(deck) * 0.85) + shuffleoffset
    deck.insert(shufflespot - 5, Card(0, 'shuffle', 'shuffle'))

    shuffle_needed = False
    return deck


def set_wager(wager_amount):
    # set_wager() takes the current chips on the table, adds then to the player stack
    # then removes wager_amount chips from the player stack and puts them on the table.
    global player_stack
    global current_wager
    try:
        number = int(wager_amount)
    except ValueError:
        print('Wager amount must be a whole number of chips, not %s' % wager_amount)
        print('I\'ll make your wager the minimum of 2 chips')
        wager_amount = 2
        player_stack += current_wager
        player_stack -= wager_amount
        current_wager = wager_amount
        print('Current wager: %s' % current_wager)
        return current_wager
    else:
        wager_amount = int(wager_amount)
        if wager_amount < 2:
            print('Minimum wager is 2 chips, I\'ll set your wager to 2 chips.')
            wager_amount = 2
            player_stack += current_wager
            player_stack -= wager_amount
            current_wager = wager_amount
        else:
            player_stack += current_wager
            player_stack -= wager_amount
            current_wager = wager_amount
        print('Current wager: %s' % current_wager)
        return current_wager


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
    player_stack += int(3/2 * current_wager)
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
    player_stack -= current_wager
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


def show_hand(hand):
    # show_hand() prints hand using the __str__ method in Card
    print('%s %s\'s hand:' % (hand.player, hand.hand_number))
    for card in hand.cards:
        print(card)


def show_chips():
    print('Player\'s Stack: %s' % player_stack)


def hand_splitter():
    # hand_splitter() removes one card from the current hand and puts it into a new hand.
    global num_hands
    global player_stack
    # global current_wager
    split_player_hand = Hand(player_hand[0].player, num_hands)
    split_player_hand.cards.append(player_hand[num_hands - 1].cards.pop(0))
    if player_hand[num_hands - 1].cards[0].value == 11:
      player_hand[num_hands - 1].split_aces = True
      split_player_hand.split_aces = True
    # deal_card(player_hand[num_hands - 1])
    player_hand[num_hands - 1].cards.append(Card(3, 'Card from hand_splitter', 0))

    player_hand.append(split_player_hand)
    num_hands += 1
    player_stack -= current_wager
    print('Current hand split. Two hands with wager %s' % current_wager)
    show_chips()


def write_out():
    # Writes the game statistics and persistant player stack out to database.
    line = {'games played': num_games,
            'player wins': player_wins_count,
            'player blackjacks': player_blackjack_count,
            'house wins': house_wins_count,
            'house blackjacks': house_blackjack_count,
            'draws count': draws_count,
            'player chips': player_stack
            }

    with open(filename, 'a') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            csv_writer.writeheader()
        csv_writer.writerow(line)


while continue_play:
    this_session_games += 1 # auto_play variable

    if shuffle_needed:
        deck = shuffle_deck()
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
            current_wager = set_wager(wager_amount)
            print('Player\'s Stack: %s' % player_stack)
            first_game = False
        if not auto_play:
            print('Dealer Must Hit on Soft 17.')
            print('Player\'s Stack: %s' % player_stack)
            wager_amount = input('Wager amount:   ')
            print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
            current_wager = set_wager(wager_amount)
            print('Player\'s Stack: %s' % player_stack)
            first_game = False

    player_hand.append(Hand('Player', 0))
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

    if player_has_blackjack and not dealer_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand[0])
        player_blackjack()
        player_turn = False
        dealer_turn = False

    if dealer_has_blackjack and not player_has_blackjack:
        show_hand(dealer_hand)
        show_hand(player_hand[0])
        dealer_blackjack()
        player_turn = False
        dealer_turn = False

    #######
    player_hand[0] = Hand('Player', 0)
    player_hand[0].cards.append(Card(3, 'First Deal', 0))
    player_hand[0].cards.append(Card(3, 'First Deal', 0))
    player_hand[0].hand_value()
    #######

    while player_turn:
        while current_hand_count < total_hands:
            if len(player_hand[current_hand_count].cards) == 1:
                deal_card(player_hand[current_hand_count])
            playing_hand = True
            first_hand = True
            while playing_hand:
                if player_hand[current_hand_count].split_aces = True:
                    break
                if player_hand[current_hand_count].cards[0].value == player_hand[current_hand_count].cards[1].value:
                    splittable_hand = True
                print('\n\nDealer is showing a %s' % dealer_hand.cards[0])
                #     # print('Dealer is hiding a %s' % dealer_hand[1])
                #     # print('Dealer hand value is %s\n' % dealer_hand.value)
                show_hand(player_hand[current_hand_count])
                print('Player hand value is %s\n' % player_hand[current_hand_count].value)

                if player_hand[current_hand_count].value > 21:
                    print('Player bust')
                    playing_hand = False
                    # results.append([player_hand[current_hand_count].hand_number,
                    #                 player_hand[current_hand_count].value,
                    #                 current_wager])
                    results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                    'Hand Value': player_hand[current_hand_count].value,
                                    'Wager': current_wager})

                elif player_hand[current_hand_count].value == 21:
                    print('Player stands on 21')
                    playing_hand = False
                    # results.append([player_hand[current_hand_count].hand_number,
                    #                 player_hand[current_hand_count].value,
                    #                 current_wager])
                    results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                    'Hand Value': player_hand[current_hand_count].value,
                                    'Wager': current_wager})

                elif first_turn and splittable_hand:
                    play = input('Would you like to (h)it, (s)tay, (d)ouble down, s(p)lit   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 'd' in play:
                        double_down = True
                        print('Wager was doubled for the remainder of this hand')
                        set_wager(current_wager * 2)
                        show_chips()
                        deal_card(player_hand[current_hand_count])
                        show_hand(player_hand[current_hand_count])
                        print('Player hand value is %s\n' % player_hand[current_hand_count].value)
                        if player_hand[current_hand_count].value > 21:
                            print('Player bust')
                        playing_hand = False
                        # results.append([player_hand[current_hand_count].hand_number,
                        #                 player_hand[current_hand_count].value,
                        #                 current_wager])
                        results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                        'Hand Value': player_hand[current_hand_count].value,
                                        'Wager': current_wager})
                        set_wager(current_wager // 2)

                    elif 'p' in play:
                        hand_splitter()
                        did_split = True
                        splittable_hand = False
                        first_hand = True
                        total_hands += 1

                    elif 's' in play:
                        playing_hand = False
                        # results.append([player_hand[current_hand_count].hand_number,
                        #                 player_hand[current_hand_count].value,
                        #                 current_wager])
                        results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                        'Hand Value': player_hand[current_hand_count].value,
                                        'Wager': current_wager})

                elif first_turn and not splittable_hand:
                    play = input('Would you like to (h)it, (s)tay, (d)ouble down   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 'd' in play:
                        double_down = True
                        print('Wager was doubled for the remainder of this hand')
                        set_wager(current_wager * 2)
                        show_chips()
                        deal_card(player_hand[current_hand_count])
                        show_hand(player_hand[current_hand_count])
                        print('Player hand value is %s\n' % player_hand[current_hand_count].value)
                        if player_hand[current_hand_count].value > 21:
                            print('Player bust')
                        playing_hand = False
                        # results.append([player_hand[current_hand_count].hand_number,
                        #                 player_hand[current_hand_count].value,
                        #                 current_wager])
                        results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                        'Hand Value': player_hand[current_hand_count].value,
                                        'Wager': current_wager})
                        set_wager(current_wager // 2)

                    elif 's' in play:
                        playing_hand = False
                        # results.append([player_hand[current_hand_count].hand_number,
                        #                 player_hand[current_hand_count].value,
                        #                 current_wager])
                        results.append({'Hand Number':   player_hand[current_hand_count].hand_number,
                                       'Hand Value':    player_hand[current_hand_count].value,
                                       'Wager':         current_wager})

                else:
                    play = input('Would you like to (h)it, (s)tay   ').lower()
                    print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')

                    if 'h' in play:
                        deal_card(player_hand[current_hand_count])
                        first_turn = False

                    elif 's' in play:
                        playing_hand = False
                        # results.append([player_hand[current_hand_count].hand_number,
                        #                 player_hand[current_hand_count].value,
                        #                 current_wager])
                        results.append({'Hand Number': player_hand[current_hand_count].hand_number,
                                        'Hand Value': player_hand[current_hand_count].value,
                                        'Wager': current_wager})

            current_hand_count += 1
            print(results)
        player_turn = False
        dealer_turn = True

######## Autoplayer here

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

    while dealer_turn:

        if dealer_hand.value == 17 and dealer_hand.soft_hand:
            show_hand(dealer_hand)
            print('Dealer must hit on soft 17')
            deal_card(dealer_hand)

        elif dealer_hand.value < 17:
            show_hand(dealer_hand)
            print('Dealer hand value is %s\n' % dealer_hand.value)
            print('Dealer must hit')
            deal_card(dealer_hand)

        elif dealer_hand.value > 21:
            show_hand(dealer_hand)
            print('Dealer hand value is %s\n' % dealer_hand.value)
            dealer_bust = True
            print('Dealer bust')
            # player_wins()
            dealer_turn = False

        else:
            show_hand(dealer_hand)
            print('Dealer hand value is %s\n' % dealer_hand.value)
            print('Dealer must stay on hard 17')
            dealer_turn = False

    num_games += 1

# Check results of each player hand against dealer's hand
    for result in results:
        if result.get('Hand Value') > 21 and not dealer_bust:
            print('Hand %s was a bust' % result.get('Hand Number'))
        elif result.get('Hand Value') in range(dealer_hand.value + 1, 22) and not dealer_bust:
            print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
            print('Dealer hand value: %s' % dealer_hand.value)
            print('Hand %s is a winner' % result.get('Hand Number'))
        elif result.get('Hand Value') < dealer_hand.value and not dealer_bust:
            print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
            print('Dealer hand value: %s' % dealer_hand.value)
            print('Hand %s is a loser' % result.get('Hand Number'))
        elif result.get('Hand Value') == dealer_hand.value:
            print('Hand %s value: %s' % (result.get('Hand Number'), result.get('Hand Value')))
            print('Dealer hand value: %s' % dealer_hand.value)
            print('Hand %s is a push' % result.get('Hand Number'))
        elif result.get('Hand Value') < 22 and dealer_bust:
            print('Dealer\'s hand was a bust')
            print('Hand %s is a winner' % result.get('Hand Number'))

    end_turn = True
    num_hands = 1

    # Player responds to a new game prompt
    while end_turn:
        if double_down:
            current_wager //= 2
            double_down = False
        if not auto_play:
            print('Current Wager: %s    Player\'s Stack: %s' % (current_wager, player_stack))
            response = input('Deal Again? (d)eal, change (b)et, (q)uit:   ').lower()
            print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
            if response in 'd':
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
                wager_amount = input('Wager amount:   ')
                print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
                current_wager = set_wager(wager_amount)

    # Run this_session_games number of games, then quit

    if auto_play and end_turn:
        if double_down:
            current_wager //= 2
            double_down = False
        print('Current Wager: %s    Player\'s Stack: %s' % (current_wager, player_stack))
        if this_session_games < auto_play_games:
            continue_play = True
            player_turn = True
            dealer_turn = False
            if shuffle_needed:
                deck = shuffle_deck()
            end_turn = False
        else:
            continue_play = False
            end_turn = False

if not continue_play:
    write_out()
