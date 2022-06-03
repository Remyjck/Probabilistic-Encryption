from asyncore import write
from tokenize import Number
from manim import *
from manim_presentation import Slide
import numpy as np

from SRA import generate_keys, crypt

class DoubleCard(VGroup):
    def __init__(self, number, color = GREEN_E, **kwargs):
        VGroup.__init__(self, **kwargs)
        base = RoundedRectangle(
            color=color, width=1.0, height=1.5, corner_radius=0.05, fill_opacity=1, stroke_color=BLACK, stroke_width=1,
        )
        num_1 = Integer(number=number).scale(0.8).align_to(base, UR).shift(0.08*DL)
        num_2 = Integer(number=number).scale(0.8).align_to(base, DL).shift(0.08*UR).rotate(PI)
        self.add(
            VGroup(base, num_1, num_2).scale(0.9)
        )

class Card(VGroup):
    def __init__(self, number, color = GREEN_E, **kwargs):
        VGroup.__init__(self, **kwargs)
        base = RoundedRectangle(
            color=color, width=1.0, height=1.5, corner_radius=0.05, fill_opacity=1, stroke_color=BLACK, stroke_width=1,
        )
        num = Integer(number=number).move_to(base.get_center())
        self.add(
            VGroup(base, num).scale(0.9)
        )
    
    def set_value(self, number):
        size = len(str(number))
        new_num = Integer(number=number).move_to(self[0][0].get_center())
        if size > 3:
            new_num.scale(3/size)
        animation = ReplacementTransform(self[0][1], new_num)
        return animation, new_num
    
    def get_value(self):
        return self[0][1].get_value()



class Cards(VGroup):
    def __init__(self, double = True, color = GREEN_E, num_cards = 3, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.num_cards = num_cards
        for i in range(num_cards):
            row = i // 6
            col = i % 6
            if double:
                card = DoubleCard(i+1, color=color).shift((1.05*RIGHT)*col+(1.4*DOWN)*row)
            else:
                card = Card(i+1, color=color).shift((1.05*RIGHT)*col+(1.4*DOWN)*row)
            self.add(card)

    def bunch_up(self):
        first_position = self[0].get_center()
        for i in range(1, self.num_cards):
            self[i].move_to(first_position + 0.1*UP)
    
    def spread_out(self):
        self[0].shift(0.1*UP)
        for i in range(1, self.num_cards):
            row = i // 6
            col = i % 6
            self[i].shift((1.05*RIGHT)*col + (1.4)*DOWN*row)
    
    def shuffle(self):
        animations = []
        first_position = self[0].get_center()
        new_indices = list(range(self.num_cards))
        np.random.shuffle(new_indices)
        unshuffled = [self[i] for i in range(self.num_cards)]
        for new_index in range(self.num_cards-1, -1, -1):
            i = new_indices.index(new_index)
            row = new_index // 6
            col = new_index % 6
            animations.append(self[i].animate.move_to(first_position + (1.05*RIGHT)*col + (1.4)*DOWN*row))

        for i in range(self.num_cards):
            new_index = new_indices[i]
            old_index = self[new_index].z_index
            self[new_index] = unshuffled[i]
            self[new_index].z_index = old_index

        return animations

def keep_around_target(mob, target, buff=0.2):
    mob.width = target.width + buff
    mob.height = target.height + buff 
    mob.move_to(target.get_center())

class DetEncryption(Slide):
    def create_keys(self, ekey, dkey, e, d):
        self.play(
            AnimationGroup(Create(e), Create(d), lag_ratio=1)
        )
        self.wait(duration=0.1)
        self.pause()
        self.wait(duration=0.1)
        self.play(
            AnimationGroup(
                ReplacementTransform(e, ekey),
                ReplacementTransform(d, dkey),
                lag_ratio=0.5
            )
        )
        self.wait(duration=0.1)
        self.pause()

    def shuffle(self, cards):
        shuffling = cards.shuffle()
        self.play(*shuffling)
        self.wait(duration=0.1)
        self.pause()

    def encrypt(self, cards, framebox, key, e):
        key.save_state()
        encrypted_values = [crypt(card.get_value(), e.get_value()) for card in cards]
        animations_newnums = [card.set_value(crypted) for card, crypted in zip(cards, encrypted_values)]
        animations = [elem[0] for elem in animations_newnums]
        newnums = [elem[1] for elem in animations_newnums]
        self.play(
            Create(framebox),
            key.animate.move_to(cards.get_center()),
            *animations
        )
        self.play(
            Restore(key)
        )
        for card, num in zip(cards, newnums):
            card[0][1] = num
        self.wait(duration=0.1)
        self.pause()
    
    def decrypt(self, cards, framebox, key, d, framebox2 = None):
        key.save_state()
        encrypted_values = [crypt(card.get_value(), d.get_value()) for card in cards]
        animations_newnums = [card.set_value(crypted) for card, crypted in zip(cards, encrypted_values)]
        animations = [elem[0] for elem in animations_newnums]
        newnums = [elem[1] for elem in animations_newnums]
        if framebox2 is not None:
            new_framebox2 = SurroundingRectangle(cards, buff=0.1, color=BLUE)
            new_framebox2.add_updater(
                lambda x : keep_around_target(x, cards)
            )
            animations.append(ReplacementTransform(framebox2, new_framebox2))
        self.play(
            *animations,
            Uncreate(framebox),
            key.animate.move_to(cards.get_center()),
        )
        self.play(
            Restore(key)
        )
        for card, num in zip(cards, newnums):
            card[0][1] = num
        self.wait(duration=0.1)
        self.pause()
        if framebox2 is not None:
            return new_framebox2

    def construct(self):
        self.wait(duration=0.1)
        self.pause()
        self.wait(duration=0.1)
        num_cards=24
        cards = Cards(num_cards=num_cards).move_to(0)
        cards_simple = Cards(double=False, num_cards=num_cards).move_to(0)
        self.play(
            FadeIn(cards),
            run_time=2,
            rate_fun=rate_functions.ease_out_sine,
            lag_ratio=0.2,
        )
        self.wait(duration=0.1)
        self.pause()

        self.play(
            ReplacementTransform(cards, cards_simple),
        )
        cards = cards_simple
        self.wait(duration=0.1)
        self.pause()

        self.play(
            cards.animate.bunch_up()
        )
        self.play(
            cards.animate.move_to(LEFT*6.2 + UP * 2)
        )
        self.wait(duration=0.1)
        self.pause()

        dashed = DashedLine([0, -4, 0], [0, 4, 0], color=RED, dash_length=0.1)
        self.play(FadeIn(dashed))
        self.wait(duration=0.1)
        self.pause()

        e1, d1 = generate_keys()
        e1 = Integer(int(e1)).move_to(LEFT*2)
        d1 = Integer(int(d1)).next_to(e1, DOWN)
        ekey1 = Tex("$e_1$", color=YELLOW).move_to(LEFT * 4.8 + UP * 3.4)
        dkey1 = Tex("$d_1$", color=YELLOW).next_to(ekey1, RIGHT).align_to(ekey1, DOWN)
        self.create_keys(ekey1, dkey1, e1, d1)
        self.add_foreground_mobject(ekey1)
        self.add_foreground_mobject(dkey1)

        e2, d2 = generate_keys()
        e2 = Integer(int(e2)).move_to(RIGHT*2)
        d2 = Integer(int(d2)).next_to(e2, DOWN)
        ekey2 = Tex("$e_2$", color=BLUE).move_to(RIGHT * 4.8 + UP * 3.4)
        dkey2 = Tex("$d_2$", color=BLUE).next_to(ekey2, RIGHT).align_to(ekey2, DOWN)
        self.create_keys(ekey2, dkey2, e2, d2)
        self.add_foreground_mobject(ekey2)
        self.add_foreground_mobject(dkey2)

        self.play(
            cards.animate.spread_out()
        )
        self.wait(duration=0.1)
        self.pause()

        self.shuffle(cards)


        framebox1 = SurroundingRectangle(cards, buff=.1, color=YELLOW)
        framebox1.add_updater(
            lambda x : keep_around_target(x, cards)
        )

        self.encrypt(cards, framebox1, ekey1, e1)

        self.play(
            cards.animate.bunch_up()
        )
        self.play(
            cards.animate.move_to(RIGHT*0.8 + UP*2),
        )
        self.wait(duration=0.1)
        self.pause()

        self.play(
            cards.animate.spread_out()
        )
        self.wait(duration=0.1)
        self.pause()

        self.shuffle(cards)

        card1 = cards[-1]
        card2 = cards[-2]
        cards.remove(card1)
        cards.remove(card2)
        cards.num_cards -= 2
        pcards1 = VGroup(card1, card2)
        self.add(pcards1)
        pframebox1 = SurroundingRectangle(pcards1, buff=.1, color=YELLOW)
        pframebox1.add_updater(
            lambda x : keep_around_target(x, pcards1)
        )
        self.play(
            Create(pframebox1)
        )
        self.play(
            pcards1.animate.move_to(LEFT*1.3 + UP*3)
        )
        self.wait(duration=0.1)
        self.pause()

        self.decrypt(pcards1, pframebox1, dkey1, d1) 

        framebox2 = SurroundingRectangle(framebox1, buff=.1, color=BLUE)
        framebox2.add_updater(
            lambda x : keep_around_target(x, framebox1)
        )

        self.encrypt(cards, framebox2, ekey2, e2)
        
        self.play(
            cards.animate.bunch_up()
        )
        self.play(
            cards.animate.move_to(LEFT*6.2 + UP*1.3)
        )
        self.play(
            cards.animate.spread_out()
        )
        self.wait(duration=0.1)
        self.pause()

        framebox2 = self.decrypt(cards, framebox1, dkey1, d1, framebox2)

        self.shuffle(cards)
        
        card3 = cards[-1]
        card4 = cards[-2]
        cards.remove(card3)
        cards.remove(card4)
        cards.num_cards -= 2
        pcards2 = VGroup(card3, card4)
        pframebox2 = SurroundingRectangle(pcards2, buff=.1, color=BLUE)
        pframebox2.add_updater(
            lambda x : keep_around_target(x, pcards2)
        )
        self.play(
            Create(pframebox2)
        )
        self.play(
            pcards2.animate.move_to(RIGHT * 1.3 + UP*3)
        )
        self.wait(duration=0.1)
        self.pause()

        self.decrypt(pcards2, pframebox2, dkey2, d2)

        self.play(
            FadeOut(ekey1),
            FadeOut(dkey1)
        )
        ekeys1 = Tex("[$e_1$, $\dots$, $e_{20}$]", color=YELLOW).move_to(LEFT*5 + UP*3)
        self.play(
            Create(ekeys1)
        )
        ekeys1.save_state()
        self.wait(duration=0.1)
        self.pause()

        frameboxes1 = []
        animations = []
        for card in cards:
            box = SurroundingRectangle(card, buff=.1, color=YELLOW)
            box.add_updater(
                lambda x, card=card: keep_around_target(x, card, 0)
            )
            frameboxes1.append(box)
            animations.append(Create(box))
        
        self.play(
            *animations,
            ekeys1.animate.move_to(cards.get_center())
        )
        self.play(
            Restore(ekeys1)
        )
        self.wait(duration=0.1)
        self.pause()

        self.play(
            cards.animate.shift(RIGHT*7)
        )
        self.wait(duration=0.1)
        self.pause()

        self.decrypt(cards, framebox2, dkey2, d2)

        self.play(
            FadeOut(ekey2),
            FadeOut(dkey2)
        )
        ekeys2 = Tex("[$e_1$, $\dots$, $e_{20}$]", color=BLUE).move_to(RIGHT*4 + UP*3)
        self.play(
            Create(ekeys2)
        )
        ekeys2.save_state()
        self.wait(duration=0.1)
        self.pause()

        frameboxes2 = []
        animations = []
        for card, framebox1 in zip(cards, frameboxes1):
            box = SurroundingRectangle(card, buff=.1, color=BLUE)
            box.add_updater(
                lambda x, framebox1=framebox1: keep_around_target(x, framebox1, 0.1)
            )
            frameboxes2.append(box)
            animations.append(Create(box))
        
        self.play(
            *animations,
            ekeys2.animate.move_to(cards.get_center())
        )
        self.play(
            Restore(ekeys2)
        )
        self.wait(duration=0.1)

        self.pause()
        self.wait(duration=0.1)
        
