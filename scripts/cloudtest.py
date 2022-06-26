from wordcloud import WordCloud
from reader import readChat
from matplotlib import pyplot as plt


def main(name, _minWordLength=5):
    # links raus?
    # Farbspektrum ändern?
    data = readChat(name)
    authorlist = list(set(data["author"]))
    words2exclude = ["nicht"]

    for author in authorlist:
        # Filter the author's text and format
        data_author = data[data["author"].str.contains(author)]
        data_author["text"] += " "
        words = data_author["text"].sum()

        words = " ".join([word for word in words.split(" ")
                          if len(word) > _minWordLength
                          and not any(_word in word.lower()
                                      for _word in words2exclude)])

        # Create the word cloud
        wordcloud = WordCloud(width=1600, height=900,
                              max_words=60).generate(words)
        plt.figure(figsize=(16, 9))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(author)
        plt.savefig("results/{}.pdf".format(author))


if __name__ == '__main__':
    main("data/_chat.txt")
