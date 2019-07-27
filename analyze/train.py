from snownlp import sentiment
if __name__ == "__main__":
    sentiment.train("neg.txt", "pos.txt")
    sentiment.save("sentiment_cxk.marshal")