import ystockquote

class SharePrice:
    def __init__(self ,enterpriseCode):
        self.price = ystockquote.get_today_open(enterpriseCode)

    def showAnswer(self):
        return "This is the current price: " , self.price
