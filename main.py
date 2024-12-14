import tkinter as tk
from tkinter import messagebox
import random
import os

# 定义卡牌类
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.color = 'black' if suit in ['♠', '♣'] else 'red'

    def __str__(self):
        return f"{self.value}{self.suit}"

# 定义游戏类
class CardGame:
    def __init__(self, master):
        self.master = master
        self.master.title("十点大作战")
        
        self.deck = self.create_deck()
        self.player_hand = []
        self.computer_hand = []
        self.pool = []
        self.player_score = 0
        self.computer_score = 0
        
        self.player_turn = True
        self.setup_game()
        self.setup_ui()
        
    def value_to_score(self, card):
        if card.value in ['J', 'Q', 'K']:
            return 10
        elif card.value == 'A':
            return 1
        else:
            return int(card.value)
    
    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [Card(suit, value) for suit in suits for value in values]
    
    def setup_game(self):
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop() for _ in range(5)]
        self.computer_hand = [self.deck.pop() for _ in range(5)]
        self.pool = [self.deck.pop() for _ in range(10)]
    
    def setup_ui(self):
        # 创建电脑手牌区域
        self.computer_frame = tk.Frame(self.master)
        self.computer_frame.pack(side=tk.TOP, pady=10)
        
        # 创建池子区域
        self.pool_frame = tk.Frame(self.master)
        self.pool_frame.pack(side=tk.TOP, pady=10)
        
        # 创建玩家手牌区域
        self.player_frame = tk.Frame(self.master)
        self.player_frame.pack(side=tk.BOTTOM, pady=10)
        
        # 创建信息显示区域
        self.info_frame = tk.Frame(self.master)
        self.info_frame.pack(side=tk.TOP, pady=10)
        
        self.deck_label = tk.Label(self.info_frame, text=f"牌堆剩余: {len(self.deck)}", font=("Arial", 18))
        self.deck_label.pack(side=tk.LEFT, padx=10)
        
        self.score_label = tk.Label(self.info_frame, text=f"玩家得分: {self.player_score} | 电脑得分: {self.computer_score}", font=("Arial", 18))
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        # 添加游戏提示文字栏
        self.message_label = tk.Label(self.master, text="游戏开始, 请点击牌配对成 10", font=("Arial", 18), wraplength=400, fg="red")
        self.message_label.pack(side=tk.BOTTOM, pady=10)
        
        self.update_ui()
    
    def update_ui(self):
        print("update_ui")
        # 更新电脑手牌
        for widget in self.computer_frame.winfo_children():
            widget.destroy()
        for card in self.computer_hand:
            can_match = self.find_match(card) is not None
            btn = tk.Button(self.computer_frame, text=f"{card.value}\n{card.suit}", font=("Arial", 18), fg=card.color, width=4, height=6)
            if can_match:
                btn.config(bg="light yellow", highlightthickness=2, highlightbackground="green")
            else:
                btn.config(state=tk.DISABLED)
            btn.pack(side=tk.LEFT, padx=2)
        
        # 更新池子
        for widget in self.pool_frame.winfo_children():
            widget.destroy()
        for card in self.pool:
            tk.Button(self.pool_frame, text=f"{card.value}\n{card.suit}", font=("Arial", 18), width=4, height=6, fg=card.color, relief="raised").pack(side=tk.LEFT, padx=2)
        
        # 更新玩家手牌
        player_match = False
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        for card in self.player_hand:
            can_match = self.find_match(card) is not None
            btn = tk.Button(self.player_frame, text=f"{card.value}\n{card.suit}", font=("Arial", 18), fg=card.color, width=4, height=6, 
                            command=lambda c=card: self.player_move(c))
            if can_match:
                btn.config(bg="light yellow", highlightthickness=2, highlightbackground="green")
                player_match = True
            else:
                btn.config(state=tk.DISABLED)
            btn.pack(side=tk.LEFT, padx=2)
        
        if not player_match:
            self.show_message("游戏信息：你 - 没有匹配的牌")
            self.player_turn = False
            self.master.after(1000, self.computer_move)
        
        # 更新信息
        self.deck_label.config(text=f"牌堆剩余: {len(self.deck)}")
        self.score_label.config(text=f"玩家得分: {self.player_score} | 电脑得分: {self.computer_score}")
    
    def player_move(self, selected_card):
        print("player_move")
        if not self.player_turn:
            self.show_message("游戏信息：电脑 - 请等待电脑操作")
            self.update_ui()
            return

        matched_card = self.find_match(selected_card)
        current_score = 0
        if matched_card:
            self.player_hand.remove(selected_card)
            self.pool.remove(matched_card)
            if selected_card.color == 'red':
                current_score += self.value_to_score(selected_card)
            if matched_card.color == 'red':
                current_score += self.value_to_score(matched_card)
            self.replenish_cards()
            self.player_turn = False
            self.update_ui()
            self.show_message(f"游戏信息：你 - 匹配了 {selected_card} 和 {matched_card}, 获得 {current_score} 分")
            self.player_score += current_score
            self.master.after(1000, self.computer_move)
        else:
            self.show_message("游戏信息：你 - 这张牌无法匹配，请选择其他牌")
            return
        
        self.check_game_over()
        self.update_ui()
    
    def computer_move(self):
        print("computer_move")
        if self.player_turn:
            print("computer_move - player_turn!")
            self.update_ui()
            return

        computer_find_match = False
        current_score = 0
        for card in self.computer_hand:
            matched_card = self.find_match(card)
            if matched_card:
                self.computer_hand.remove(card)
                self.pool.remove(matched_card)
                # self.computer_score += 10
                if card.color == 'red':
                    current_score += self.value_to_score(card)
                if matched_card.color == 'red':
                    current_score += self.value_to_score(matched_card)
                self.replenish_cards()
                self.show_message(f"游戏信息：电脑 - 匹配了 {card} 和 {matched_card}, 获得 {current_score} 分")
                self.computer_score += current_score
                computer_find_match = True
                break
        
        if not computer_find_match:
            self.show_message("游戏信息：电脑 - 电脑没有可以匹配的牌")
        
        self.player_turn = True
        self.check_game_over()
        self.update_ui()
        
    def show_message(self, message):
        self.message_label.config(text=message)
    
    def replenish_cards(self):
        if self.deck:
            if len(self.player_hand) < 5:
                self.player_hand.append(self.deck.pop())
            if len(self.computer_hand) < 5:
                self.computer_hand.append(self.deck.pop())
        if self.deck and len(self.pool) < 10:
            self.pool.append(self.deck.pop())
    
    def find_match(self, card):
        card_value = self.get_card_value(card.value)
        for pool_card in self.pool:
            pool_value = self.get_card_value(pool_card.value)
            if (card_value + pool_value == 10) or (card.value in ['10','J', 'Q', 'K'] and card.value == pool_card.value):
                return pool_card
        return None
    
    def get_card_value(self, value):
        if value in ['J', 'Q', 'K']:
            return 10
        elif value == 'A':
            return 1
        else:
            return int(value)

    
    def check_game_over(self):
        try:
            print("check_game_over")
            if (not self.player_hand and not self.computer_hand) or (not self.find_any_match()):
                self.update_ui()
                print("game over", self.player_score, self.computer_score)
                winner = "平局"
                if self.player_score > self.computer_score:
                    winner = "玩家获胜"
                elif self.computer_score > self.player_score:
                    winner = "电脑获胜"
                # 显示游戏结束信息
                self.show_message(f"游戏结束！{winner}!")
                # 等待用户点击确认按钮
                self.master.wait_window(self.master)
                # 退出游戏
                self.master.quit()
        except Exception as e:
            print(f"An error occurred: {e}")
            # 处理错误，例如向用户显示错误消息
            messagebox.showerror("Error", f"An error occurred: {e}")

    
    def find_any_match(self):
        print("find_any_match")
        for card in self.player_hand + self.computer_hand:
            if self.find_match(card):
                return True
        return False

# 创建主窗口并运行游戏
root = tk.Tk()

# 计算屏幕的宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

width = 1000
height = 600

# 计算窗口应该放置的x和y坐标
x = (screen_width - width) // 2
y = (screen_height - height) // 2 - 100

root.geometry(f"{width}x{height}+{x}+{y}")

game = CardGame(root)
root.mainloop()
