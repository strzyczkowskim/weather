from yahoo_finance import Share, Currency
class SharePrice:
    def __init__(self ,enterpriseCode):
        s = Share(enterpriseCode)
        self.price = s.get_price()

    def showAnswer(self):
        return "This is the price: " , self.price
