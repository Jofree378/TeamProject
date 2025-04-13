from bot_actions import start_search
from models.user_model import User
from config import TOKEN_D_VK

if __name__ == '__main__':

    user = User(TOKEN_D_VK, 195449167)
    # print(start_search(user))