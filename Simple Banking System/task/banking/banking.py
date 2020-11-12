import sqlite3
import random
from functools import reduce


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()


cur.execute('CREATE TABLE IF NOT EXISTS card('
            'id INTEGER PRIMARY KEY,'
            'number TEXT,'
            'pin TEXT,'
            'balance INTEGER DEFAULT 0'
            ');')
conn.commit()


def show_main_menu():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    user_choice = input()
    if user_choice == '1':
        card_generate()
        show_main_menu()
    elif user_choice == '2':
        chek_account()
    elif user_choice == '0':
        print('Bye!')


def card_generate():
    card = luhn_number_generator()
    pin = str(random.randint(1000, 9999))
    cur.execute('INSERT INTO card (number, pin) VALUES ({}, {})'.format(card, pin))
    conn.commit()
    print('Your card has been created')
    print('Your card number:')
    print(card)
    print('Your card PIN:')
    print(pin)


def luhn_number_generator():
    card = str(random.randint(0, 999999999))
    if len(card) < 9:
        card = '0' * (9 - len(card)) + card
    card = '400000' + card
    temp_number = []
    for i in range(len(card)):
        if i % 2 == 0:
            temp_number.append(int(card[i]) * 2)
        elif i % 2 == 1:
            temp_number.append(int(card[i]))
    for i in range(len(temp_number)):
        if temp_number[i] > 9:
            temp_number[i] -= 9
    check_summ = 10 - sum(temp_number) % 10
    if check_summ == 10:
        check_summ = 0
    card += str(check_summ)
    return card


def card_is_luhn(card):
    LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
    code = reduce(str.__add__, filter(str.isdigit, card))
    evens = sum(int(i) for i in code[-1::-2])
    odds = sum(LOOKUP[int(i)] for i in code[-2::-2])
    return ((evens + odds) % 10 == 0)


def chek_account():
    card = input('Enter your card number:')
    pin = input('Enter your PIN:')
    try:
        cur.execute('''
        SELECT
            number,
            pin
        FROM
            card
        WHERE
            number = {}
            '''.format(card))
        result = cur.fetchone()
    except:
        print('Bad card number')
        show_main_menu()
    print(result)
    if result:
        if result[1] != pin:
            print('Wrong card number or PIN!')
            show_main_menu()
        else:
            show_account_menu_first_time(card)
    else:
        print('Wrong card number or PIN!')
        show_main_menu()


def card_exist(card):
    cur.execute('''
            SELECT
                id
            FROM
                card
            WHERE
                number = {}
                '''.format(card))
    result = cur.fetchone()
    if result is not None:
        return True
    else:
        return False


def del_acc(card):
    cur.execute('''DELETE FROM 
                          card 
                   WHERE
                          number = {};'''.format(card))
    conn.commit()


def show_account_menu_first_time(card):
    print('You have successfully logged in!')
    print('')
    show_account_menu(card)


def get_balance(card):
    cur.execute('''

            SELECT
                balance
            FROM
                card
            WHERE
            number = {}

            '''.format(card))
    return cur.fetchall()[0][0]


def set_balance(card, value):
    cur.execute('''UPDATE 
                        card 
                    SET 
                        balance = {} WHERE number = {};'''.format(value, card))
    conn.commit()


def show_account_menu(card):
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')
    user_choice = input()
    if user_choice == '1':  # balance
        print('Balance: {}'.format(get_balance(card)))
        show_account_menu(card)
    elif user_choice == '2':  # add income
        print('Enter income:')
        income = int(input())
        set_balance(card, get_balance(card) + income)
        show_account_menu(card)
    elif user_choice == '3':  # do transfer
        print('Enter card number:')
        card_reciever = input()
        if not card_is_luhn(card_reciever):
            print('Probably you made a mistake in the card number. Please try again!')
            show_account_menu(card)
        elif not card_exist(card_reciever):
            print('Such a card does not exist.')
            show_account_menu(card)
        else:
            print('Enter how much money you want to transfer:')
            sum_to_transfer = int(input())
            if sum_to_transfer > get_balance(card):
                print('Not enough money!')
                show_account_menu(card)
            set_balance(card_reciever, get_balance(card_reciever) + sum_to_transfer)
            set_balance(card, get_balance(card) - sum_to_transfer)
            print('Success!')
            show_account_menu(card)

    elif user_choice == '4':  # close account
        del_acc(card)
        print('The account has been closed!')
        show_main_menu()
    elif user_choice == '5':  # log out
        print('You have successfully logged out!')
        show_main_menu()
    elif user_choice == '0':  # exit
        print('Bye!')
        quit()

show_main_menu()
