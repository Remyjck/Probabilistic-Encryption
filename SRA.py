import gmpy2
import random

# a big prime number
PRIME = 4294967291
state = gmpy2.random_state()

def generate_keys(prime = PRIME):
    while True:
        e = gmpy2.mpz_random(state, prime-2)
        if gmpy2.gcd(e, prime-1) == 1 and e > 2:
            break
    d = gmpy2.invert(e, prime-1)
    return e,d

def crypt(card_num, key, prime = PRIME):
	return int(gmpy2.powmod(card_num, key, prime))

def encrypt_deck(deck, key, prime = PRIME):
    return [crypt(card, key, prime) for card in deck]

if __name__ == "__main__":
    cards = list(range(1, 26))
    random.shuffle(cards)

    print(cards)
    print()

    e1, d1 = generate_keys()
    cards = encrypt_deck(cards, e1)

    print(cards)
    print()

    e2, d2 = generate_keys()
    cards = encrypt_deck(cards, e2)

    print(cards)
    print()

    cards = encrypt_deck(cards, d1)

    print(cards)
    print()

    cards = encrypt_deck(cards, d2)

    print(cards)
    print()