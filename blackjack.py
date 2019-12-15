# blackjack.py

import random, os, sys, csv, math, statistics, time


filename = 'blackjack_outcomes.csv'
file_exists = os.path.isfile(filename)
fieldnames = ['games played',
              'player wins',
              'player blackjacks',
              'house wins',
              'house blackjacks',
              'draws']

games = 0
plwns = 0
hswns = 0
draws = 0
plbjk = 0
hsbjk = 0

thisSession = 0

# if not file_exists:
#     with open(filename, 'w') as f:
#         if not file_exists:
#             csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
#             csv_writer.writeheader()

if file_exists:
    with open(filename, 'r') as f:
        csv_reader = csv.DictReader(f)
        csv_data = list(csv_reader)

    for line in csv_data:
        games = int(line['games played'])
        plwns = int(line['player wins'])
        hswns = int(line['house wins'])
        draws = int(line['draws'])
        plbjk = int(line['player blackjacks'])
        hsbjk = int(line['house blackjacks'])


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
numshuffles = 5


def shuffledeck(numshuffles, deck, ranks, suits):
    global shuffleNeeded
    for sets in range(numDecks):
        for rank in ranks:
            for suit in suits:
                deck.append(Card(rank, suit, sets))

    if numshuffles == 1:
        for shuffle in range(numshuffles - 1 , -1, -1):
            print('Shuffling %s deck one time. Total of %s cards' % (numDecks, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]
    else:
        for shuffle in range(numshuffles - 1, -1, -1):
            print('Shuffling %s decks %s more times. Total of %s cards' % (numDecks, shuffle, len(deck)))
            for i in range(len(deck) - 1, 0, -1):
                j = random.randint(0, i)
                deck[i], deck[j] = deck[j], deck[i]

    offsetbound = round(len(deck) * .1)
    shuffleoffset = random.randint(-offsetbound, offsetbound)
    shufflespot = round(len(deck) * 0.85) + shuffleoffset
    deck.insert(shufflespot - 5, Card(0, 'shuffle', 'shuffle'))

    shuffleNeeded = False
    return deck


def playerwins():
    print('Player Wins. House pays 2:1\n\n')
    global plwns
    plwns += 1
    return plwns
    # double chips


def playerblackjack():
    print('Player Wins. Black Jack pays 3:2\n\n')
    global plbjk
    plbjk += 1
    return plbjk
    # 3/2 chips


def housewins():
    print('House Wins. House takes bet.\n\n')
    global hswns
    hswns += 1
    return hswns
    # keep chips


def houseblackjack():
    print('Dealer has blackjack. House takes bet.\n\n')
    global hsbjk
    hsbjk += 1
    return hsbjk
    # keep chips


def push():
    print('Push. Player keeps bet.')
    global draws
    draws += 1
    return draws
    # add chips


deck = shuffledeck(numshuffles, deck, ranks, suits)
continuePlay = True
playerTurn = True
preTurn = True
dealerTurn = False


def dealcard(who):
    global shuffleNeeded
    if deck[0].rank == 'shuffle':
        print('_,.-.,__,.-.,_ The shuffle card has been reached _,.-.,__,.-.,_')
        shuffleNeeded = True
        deck.pop(0)
    who.append(deck.pop(0))
    print('Card was dealt and now there are %s cards left in deck' % len(deck))


while continuePlay:
    playerHand = []
    houseHand = []
    playerValue = 0
    houseValue = 0

    playerBust = False
    houseBust = False
    playerBlackjack = False
    dealerBlackjack = False

    print('Player: %s   House: %s   Draws: %s' % (plwns + plbjk, hswns + hsbjk, draws))
    games += 1
    thisSession += 1 # debug thing to run a lot of games, remove later
    dealcard(playerHand)
    dealcard(houseHand)
    dealcard(playerHand)
    dealcard(houseHand)
    for card in range(len(houseHand)):
        houseValue += houseHand[card].value
    for card in range(len(playerHand)):
        playerValue += playerHand[card].value

    print('Player\'s hand:')
    for card in range(len(playerHand)):
        print(playerHand[card])
    print('Player hand value is %s' % playerValue)
    print('Dealer is showing a %s' % houseHand[0])
    print('Dealer is hiding a %s' % houseHand[1])
    print('Dealer hand value is %s' % houseValue)

    if playerValue == 21:
        print('Player has a blackjack')
        playerBlackjack = True

    if houseValue == 21:
        print('Dealer has a blackjack')
        dealerBlackjack = True

    if playerBlackjack and dealerBlackjack:
        print('Push')
        playerTurn = False
        dealerTurn = False

    if playerBlackjack and not dealerBlackjack:
        playerblackjack()
        playerTurn = False
        dealerTurn = False

    if dealerBlackjack and not playerBlackjack:
        houseblackjack()
        playerTurn = False
        dealerTurn = False

    while playerTurn:

        if playerValue > 21:
            housewins()
            playerBust = True
            playerTurn = False
            break

        else:
            # play = input('Would you like to (h)it, (s)tay, (d)ouble, or (s)plit?').lower()
            play = 's'
            if 'h' in play:
                dealcard(playerHand)
            elif 's' in play:
                playerTurn = False
                dealerTurn = True

    while dealerTurn:

        if houseValue < 17:
            print('Dealer must hit')
            dealcard(houseHand)
            houseValue += houseHand[-1].value
            print('Dealers\'s hand:')
            for card in range(len(houseHand)):
                print(houseHand[card])
            print('Dealer hand value is %s' % houseValue)

        if houseValue > 21:
            houseBust = True
            print('Dealer bust')
            playerwins()
            break

        if houseValue >= 17:
            print('Dealer must stay')
            break

    if playerValue > houseValue and not playerBlackjack:
        print('Player\'s final hand value is %s' % playerValue)
        print('Dealer\'s final hand value is %s' % houseValue)
        playerwins()
        # player chips increase

    if playerValue < houseValue and not houseBust and not dealerBlackjack:
        print('Player\'s final hand value is %s' % playerValue)
        print('Dealer\'s final hand value is %s' % houseValue)
        housewins()
        # player chips stay constant

    if playerValue == houseValue:
        print('Player\'s final hand value is %s' % playerValue)
        print('Dealer\'s final hand value is %s' % houseValue)
        push()
        # player chips stay constant

    line = {'games played':                games,
            'player wins':          plwns,
            'player blackjacks':    plbjk,
            'house wins':           hswns,
            'house blackjacks':     hsbjk,
            'draws':                draws,
            }

    with open(filename, 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerow(line)

    if thisSession < 1000:
        continuePlay = True
        playerTurn = True
        dealerTurn = False
        preTurn = True
        if shuffleNeeded:
            deck = shuffledeck(numshuffles, [], ranks, suits)
    else:
        continuePlay = False


    # Player responds to a new game prompt

    # response = input('Deal Again? (d)eal (b)et (q)uit').lower()
    # if response in 'd':
    #     continuePlay = True
    #     playerTurn = True
    #     dealerTurn = False
    #     preTurn = True
    #     if shuffleNeeded:
    #         deck = shuffledeck(numshuffles, [], ranks, suits)
    # elif response in 'q':
    #     continuePlay = False
    # elif response not in ['d', 'q']:
    #     print('You\'re dumb, I quit.')
    #     continuePlay = False
